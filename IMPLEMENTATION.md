# CreatorIQ — Implementation Guide

> An opinionated engineering blueprint for building CreatorIQ as a fast, cheap, reliable SaaS. Every design decision below is justified against three constraints: **cost per active user**, **p95 latency**, and **operational simplicity**. Where the current code diverges from this design, I call it out explicitly.

---

## 0. Reading guide

Sections are independent; jump to the part you're working on.

| § | Topic | Read if you're working on… |
|---|-------|----------------------------|
| 1 | First principles & invariants | Anything |
| 2 | System architecture | Infra, deployment |
| 3 | Data model & invariants | Models, migrations, schema design |
| 4 | AI pipeline & cost model | Intelligence engines, prompts, OpenRouter |
| 5 | Caching strategy | Anything that touches Redis or hits an external API |
| 6 | Background jobs & idempotency | Channel/competitor analysis, trend refresh |
| 7 | API design | Routers, error handling, pagination |
| 8 | Frontend architecture | Next.js app, hooks, state |
| 9 | Database performance | Queries, indexes, pgvector |
| 10 | Security & multi-tenancy | Auth, plan gating, rate limits |
| 11 | Observability | Logging, metrics, tracing |
| 12 | Phased rollout | Anything before MVP launch |

---

## 1. First principles

These are the rules I'd defend in any review.

1. **AI calls are the dominant cost.** A single `Pro` user generating 10 scripts a month is ~$2 in LLM, ~$0.50 in YouTube API, and rounding-error in compute. **Optimize for tokens before anything else.**
2. **One AI call = one purpose.** Never combine creator-profile + gap-detection + script in one prompt. Smaller prompts are cheaper, more cacheable, easier to debug, and give predictable outputs.
3. **Cache at three layers.** HTTP (ETag), Redis (warm), Postgres (durable). Anything an LLM produced once should be reusable.
4. **Read paths must never call external APIs.** Channel `GET` should hit Postgres. YouTube/LLM calls happen only in background jobs or write paths.
5. **Make every job idempotent.** Re-running channel analysis must converge, not duplicate. Use `source_id + content_hash` as natural keys.
6. **Fail soft on enrichment.** If Firecrawl is down, gap detection still works on YouTube data alone. The user always gets *something*.
7. **Plan-gate at the application layer, not just the UI.** A `free` user POSTing a script must be rejected by the API, not just hidden.
8. **Background work belongs in workers.** FastAPI threads do not.
9. **Frontend is presentation only.** No business logic, no LLM keys, no derived metrics that the backend hasn't already computed.

---

## 2. System architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  Next.js 14 (Vercel)                                             │
│   • App Router, RSC where possible, "use client" only at leaves  │
│   • TanStack Query for server cache; Zustand for ephemeral UI    │
│   • Single typed API client, never calls third parties           │
└────────────────────────┬─────────────────────────────────────────┘
                         │ HTTPS · JWT in Authorization header
┌────────────────────────▼─────────────────────────────────────────┐
│  FastAPI (Railway / Fly)                                         │
│   • Stateless app pods (autoscale 2..N)                          │
│   • Routers: thin HTTP, delegate to services/intelligence        │
│   • Auth: JWT (HS256), 7d access token, refresh via re-login     │
└──┬──────────────────┬──────────────────────────────┬─────────────┘
   │ SQLAlchemy 2.0   │ redis.asyncio                │ Celery enqueue
┌──▼─────────────┐  ┌─▼──────────────────┐   ┌───────▼────────────┐
│ Postgres 16 +  │  │ Redis 7            │   │ Celery worker pool │
│ pgvector       │  │ • Cache (TTL)      │   │ • Long-running     │
│ • Source of    │  │ • Celery broker    │   │   pipelines         │
│   truth         │  │ • Rate-limit ctrs  │   │ • Beat for cron    │
└────────────────┘  └────────────────────┘   └────────┬───────────┘
                                                      │
                          ┌───────────────────────────┼──────────────┐
                          │                           │              │
                  ┌───────▼────────┐         ┌────────▼────────┐  ┌──▼────────┐
                  │ YouTube Data   │         │ OpenRouter      │  │ Firecrawl │
                  │ API v3         │         │ (multi-LLM)     │  │           │
                  └────────────────┘         └─────────────────┘  └───────────┘
```

### Why this shape

- **Stateless web layer + worker layer** — the web pods can be aggressively autoscaled because they hold nothing. Heavy work runs in workers with their own scaling profile (CPU-bound vs IO-bound).
- **Single Postgres** — pgvector + relational + JSONB is enough for the next 10x. Don't add Pinecone/Mongo until a measured query exceeds 100ms.
- **Redis for everything ephemeral** — broker, cache, rate-limit, distributed locks. One dependency, one failure mode.
- **No Kafka, no microservices.** This is a CRUD app with AI sprinkled in. Keep it boring.

### Where the current code differs and what I'd change

| Current | Issue | Fix |
|---|---|---|
| Background work runs on `threading.Thread` started inside FastAPI startup/handlers | Lost on pod restart, no retry, no visibility | Move all enrichment to Celery; FastAPI returns `202` + `analysis_job_id` |
| `main.py` recovers stuck analyses on startup | Won't scale past 1 pod (each pod tries to recover the same channels) | Workers acquire a Redis lock per `channel_id` before processing |
| ETag middleware reads `response.body` | Breaks streaming responses | Compute ETag in the route handlers that benefit, not globally |
| OpenAPI hidden in production | Killing this hurts API consumers and partner integrations | Expose under `/openapi.json`, gate `/docs` UI with basic auth in prod |

---

## 3. Data model

### Core entities

```
User ──< Channel ──< Video
              │
              ├──< Competitor ──< Video (is_competitor_video=true)
              ├──< ContentGap
              ├──< Hook
              └──< Script (also FK to User)
                       │
                       └─< AnalysisJob  ── tracks any async job
Trend (no FK to Channel — global, joined by niche string)
```

### Decisions worth defending

**1. UUIDv4 PKs everywhere.** Cheap, sortable enough with `created_at` indexes, no enumeration leaks, safe to expose in URLs.

**2. `Video` is one table, not two.** `videos.is_competitor_video bool` + `videos.channel_id` (the *owning* channel, even for competitor videos). Pros:
- Single embedding index serves both.
- Joins are simpler.
Con: requires a partial index `WHERE is_competitor_video = true` for competitor-only scans (already cheap).

**3. JSONB for AI-derived "soft" fields.** `niche_tags`, `emotional_triggers_used`, `hook_patterns` etc. live in JSONB. They evolve with prompt changes; locking them into columns means a migration every prompt iteration.

**4. Embeddings on the row, not in a side table.** `Vector(1536)` columns on `channels` and `videos`. Co-locating embedding with row data makes filter+ANN queries one-shot:
```sql
SELECT id, title FROM videos
WHERE channel_id = :id
ORDER BY content_embedding <=> :query_emb
LIMIT 10;
```

**5. `AnalysisJob` is a single table, polymorphic via `entity_type`.** Don't create `ChannelJob`, `CompetitorJob`, etc. Track:
- `entity_type, entity_id` — what's being processed
- `status` — `queued|running|done|failed`
- `progress_pct, current_step` — for UI polling
- `celery_task_id` — for cancellation
- `idempotency_key` — natural dedup
- `error_message, retry_count`

**6. Subscription state lives on `User`.** Plan, monthly script counter, current period anchor. Don't build a separate `subscription` table until Stripe integration adds requirements (next billing date, payment method, etc.).

### Schema invariants enforced at DB level

- `users.email` unique, lowercased on insert.
- `channels.youtube_channel_id` unique (one creator can connect a channel only once globally — easier privacy story).
- `videos.youtube_video_id` unique with partial index per `(channel_id, is_competitor_video)` — same video can appear once as creator's, once as competitor's.
- `analysis_jobs.idempotency_key` unique — caller-provided, prevents duplicate enqueues.
- All FKs `ON DELETE CASCADE` so deleting a user is one statement.

### Migration strategy

The current repo has **only an indexes migration** and no baseline schema migration. I'd:

1. Generate a single `0001_baseline.py` from the current models with `alembic revision --autogenerate`.
2. Prepend it with `op.execute("CREATE EXTENSION IF NOT EXISTS vector;")`.
3. Move the existing indexes migration to `0002_add_indexes.py` with `down_revision = "0001_baseline"`.
4. Never use `Base.metadata.create_all()` outside tests.

---

## 4. AI pipeline & cost model

This is the section that determines whether the business is profitable.

### 4.1 The cost-routing decision

Every LLM call is one of three tiers, picked at the *call site* based on what the task actually needs:

| Tier | Model | When | Why |
|------|-------|------|-----|
| `simple` | `meta-llama/llama-3.1-8b-instruct` | Title generation, hook generation, classification, JSON reformatting | $0.05/M tokens. Quality is sufficient when the prompt is templated and constraints are tight. |
| `medium` | `openai/gpt-4o-mini` | Creator profile, gap detection, audience analysis, competitor synthesis | Sweet spot. Reasoning is fine, costs are 10-15× cheaper than premium. |
| `complex` | `anthropic/claude-3.5-sonnet` | Full script generation, retention analysis | Long-form coherence and creative tone matter. Used at most once per script. |
| `vision` | `anthropic/claude-3.5-haiku` | Thumbnail analysis | Cheap multimodal. GPT-4o vision is 8× more expensive for marginally better results. |

Picking the model is a one-line change:
```python
result = call_openai(system, user, complexity="simple")
```

### 4.2 Token reduction techniques (in order of payoff)

1. **Compress inputs aggressively.** A creator profile doesn't need 10 full transcripts; it needs 5 video titles + view counts + the first 200 chars of each transcript. The current `compress_video_context` helper does this. **Always run it before formatting prompts.**
2. **Truncate to a hard token budget.** Use `tiktoken.encoding_for_model("gpt-4o").encode()` and slice. Never trust upstream lengths.
3. **Prefer titles over transcripts.** Most signal is in titles. Reach for transcripts only when the engine specifically needs *what was said*.
4. **Strip HTML before LLM eyes ever see it.** `clean_html` (already in `scraper_service.py`) drops 80% of bytes from a typical scrape.
5. **Cap `max_tokens` per call.** Don't request 4000 tokens when 800 will do. The model will fill the budget.
6. **JSON mode, not free-form.** Forces shorter outputs and removes the parser tax.
7. **Don't ask for explanations.** "Return JSON only. No preamble." saves 100-300 output tokens per call.

### 4.3 Engine architecture

Each engine has the same shape:

```
inputs (already-fetched DB rows + a small config) 
  → context_builder (compresses, truncates, formats)
  → prompt (templated, in app/prompts/)
  → call_openai(complexity=...)
  → safe_json_loads
  → outputs (typed dict)
  → caller persists to Postgres
```

Engines must not:
- Open DB sessions (caller passes them in or hands over plain dicts).
- Call YouTube API (services/ does that).
- Trigger Celery tasks (caller does that).
- Cache things (services do that — see §5).

This separation means engines are unit-testable with no infra running.

### 4.4 Smarter gap detection (the one I'd rewrite)

Current `gap_detector.detect_gaps` asks an LLM to compare two lists of titles. That's expensive and brittle.

**Better approach — embedding-based with LLM only at the synthesis step:**

```
1. Embed all creator video titles  → V_creator (cached, only on new uploads)
2. Embed all competitor video titles → V_comp
3. Find competitor titles whose nearest creator-title is > 0.4 cosine away
   (i.e. topics the creator hasn't touched). pgvector handles this in SQL:

   SELECT v.title
   FROM videos v
   WHERE v.channel_id = :chan AND v.is_competitor_video = true
     AND NOT EXISTS (
       SELECT 1 FROM videos cv
       WHERE cv.channel_id = :chan AND cv.is_competitor_video = false
         AND v.content_embedding <=> cv.content_embedding < 0.4
     )
   ORDER BY v.view_count DESC
   LIMIT 30;

4. Take those 30 candidate "uncovered" titles, plus scraped Reddit/Quora 
   questions, and run ONE LLM call to:
   - Cluster into N gaps (default 8)
   - Score opportunity (1-10) per gap
   - Suggest angle and title

That's 1 LLM call instead of N, and the candidate set is data-driven 
rather than vibes-driven. Cost drops from ~$0.005/run to ~$0.001/run, 
and quality goes up because the LLM gets curated input.
```

### 4.5 Content-addressable LLM cache

This is the highest-leverage optimization not yet in the codebase.

```python
# Cache key: hash(model + system + user + temperature + max_tokens)
# TTL: 24h for analytical calls, 7d for stable prompts (titles, hooks)

async def call_openai_cached(system, user, **kwargs):
    key = sha256(f"{model}:{system}:{user}:{kwargs}".encode()).hexdigest()
    cached = await redis_cache.get(f"llm:{key}")
    if cached:
        metrics.inc("llm_cache_hit")
        return cached
    result = await call_openai(system, user, **kwargs)
    await redis_cache.set(f"llm:{key}", result, ttl=kwargs.get("cache_ttl", 86400))
    return result
```

Why it works: deterministic prompts (which most engine prompts are after `temperature=0` is set) produce deterministic outputs. Two creators in the same niche running gap detection on overlapping competitors will share cache entries.

Expected hit rate after a month: **40-60%** for "warm" niches (gaming, tech, beauty), 5-15% for long-tail niches.

### 4.6 Per-user token budgets

`token_budget.py` exists but is undertested and stores monthly totals only. I'd:

1. Track token usage per user **per month** in Redis (`incr` on a daily key, sum at read time).
2. Mirror weekly totals to Postgres for analytics (Celery beat task, daily).
3. Plan limits enforced as middleware on script/hook/research routes:

```python
@router.post("/generate")
async def generate_script(..., user: User = Depends(get_current_user)):
    estimate = estimate_tokens(topic, target_duration_minutes)
    if not TokenBudget.allow(user.id, user.plan, estimate):
        raise HTTPException(429, "Monthly token budget exceeded. Upgrade or wait until next reset.")
    # ...
```

4. Surface a `GET /me/usage` endpoint so the frontend can show a usage bar.

---

## 5. Caching strategy

### 5.1 Three layers

| Layer | Where | TTL | What |
|---|---|---|---|
| **HTTP** | Browser ↔ FastAPI | Per-route (60s–1d) | List endpoints, ETag-based 304s |
| **Redis** | FastAPI ↔ external | 1h–7d | YouTube channel/video stats, scrape results, LLM responses |
| **Postgres** | Permanent | Until invalidation | Analyzed channels/competitors/gaps/scripts |

### 5.2 Cache key conventions

```
yt:channel:<youtube_channel_id>          → 1h   (stats change slowly)
yt:videos:<channel_id>:<page>            → 30m  (depends on upload cadence)
yt:transcript:<video_id>                 → 30d  (transcripts don't change)
scrape:reddit:<topic>                    → 6h
scrape:quora:<topic>                     → 24h
scrape:google:<keyword>                  → 24h
llm:<sha256(call_signature)>             → 24h–7d
trends:<niche>                           → 1h
```

Always namespace keys. Always include version prefix in production (`v2:yt:channel:...`) so prompt changes can invalidate stale LLM caches without flushing Redis.

### 5.3 Invalidation

- **Channel re-analyze** → delete `yt:channel:<id>`, `yt:videos:<channel_id>:*`, all gap caches for that channel.
- **Plan upgrade** → delete `usage:<user_id>:*` (so limits reset cleanly).
- **Prompt template change** → bump the version prefix.

### 5.4 Stampede protection

For expensive operations (full channel analysis, deep research), use Redis SETNX as a lock:

```python
async def with_lock(key: str, ttl_seconds: int):
    acquired = await redis.set(f"lock:{key}", "1", nx=True, ex=ttl_seconds)
    if not acquired:
        raise AlreadyRunning()
    try:
        yield
    finally:
        await redis.delete(f"lock:{key}")
```

Prevents two simultaneous "Connect channel" clicks from kicking off two analysis pipelines.

---

## 6. Background jobs & idempotency

### 6.1 The core pipeline (channel analysis)

```
USER: POST /channels/connect { youtube_channel_id }

ROUTE:
  1. Validate handle/ID format (regex + InputValidator)
  2. Check user.plan vs current channel count → 402 if over limit
  3. INSERT channels(... analysis_status='pending') with idempotency on yt_id
  4. Enqueue Celery task: analyze_channel.delay(channel.id, idempotency_key=...)
  5. Return 202 + { id, analysis_status, job_id }

WORKER (analyze_channel):
  Step 1: Acquire lock on channel.id (Redis SETNX, 30min TTL)
  Step 2: Update analysis_status='running', emit AnalysisJob(progress=10%)
  Step 3: fetch_channel_details_cached() ─────────────── 1 quota unit
  Step 4: fetch_channel_videos(uploads_playlist_id, 50) ─ 1 unit/page
  Step 5: fetch_video_statistics(top 50 video_ids) ───── 1 unit
  Step 6: For top 5 videos by views, fetch_transcript()  free (or Whisper $0.07 ea)
  Step 7: Persist videos in bulk (one INSERT ... ON CONFLICT)
  Step 8: Generate embeddings for top 20 video titles ──  1 LLM call (batched)
  Step 9: CreatorAnalyzer.analyze_creator() ──────────── 1 LLM call (medium)
  Step 10: Save profile fields to channel
  Step 11: Update analysis_status='done', emit progress=100%
  Step 12: Release lock

ON FAILURE:
  - Mark analysis_status='failed', store error_message
  - Celery auto-retries on transient errors (network) with exp backoff
  - On final failure: emit notification (email/in-app)
```

**Costs per channel analysis:** ~6 YouTube units (negligible), ~$0.02 LLM, ~$0.01 transcript. Total: **~$0.03**.

### 6.2 Idempotency

Every Celery task takes an `idempotency_key` (default: `f"{task_name}:{entity_id}:{date}"`). Worker checks `analysis_jobs` for a completed job with the same key in the last hour. If found, return its result.

This makes the entire pipeline replay-safe: pod restarts, network blips, and double-clicks all converge to the same outcome.

### 6.3 Trend refresh — the one cron job

Daily 4am UTC, Celery beat:
1. For each distinct `niche` with at least 1 active channel, run `TrendEngine.detect_trends(niche)`.
2. UPSERT into `trends` table.
3. Soft-delete trends not seen in 14 days (`opportunity_window='closed'`).

That's it. No real-time trend detection — it's almost always wasted compute since users won't refresh fast enough to notice.

---

## 7. API design

### 7.1 Conventions

- **Versioned base:** `/api/v1/...`. Bumping major version = new prefix, old kept alive 6 months.
- **Always return JSON.** Even errors:
  ```json
  { "error": { "code": "PLAN_LIMIT_EXCEEDED", "message": "...", "details": {...} } }
  ```
- **Pagination:** cursor-based for lists > 100 items, offset for everything else. Always include `total` and `has_more`.
- **Timestamps:** ISO 8601 with `Z` (UTC), never local time.
- **Correlation:** every response carries `X-Request-ID`; clients echo it in error reports.
- **Rate limiting:** `429` with `Retry-After` header; never silently drop.

### 7.2 Endpoint shape

Read endpoints (`GET /channels/`) **must**:
- Return only DB data; never call YouTube/LLM/Firecrawl.
- Be cheap (< 50ms p95).
- Be cached client-side (TanStack Query handles it).

Write endpoints (`POST /channels/connect`) **must**:
- Validate inputs (Pydantic + custom validators).
- Check plan limits.
- Persist a record with status=`pending`.
- Enqueue work.
- Return `202 Accepted` with the persisted record + `analysis_job_id`.

Long polling: `GET /jobs/{job_id}` returns current status. Frontend polls every 3s with `refetchInterval` until status terminal.

### 7.3 Error contract

```python
class APIError(HTTPException):
    code: str           # PLAN_LIMIT_EXCEEDED, BUDGET_EXCEEDED, NOT_FOUND, ...
    message: str        # Human-readable, safe to show users
    details: dict       # Machine-readable (limit, current, etc.)
    status_code: int
```

All routes raise `APIError`. The exception handler turns it into the JSON shape above. Frontend has a single `handleApiError` that maps codes to UI behavior.

---

## 8. Frontend architecture

### 8.1 Layering

```
app/                  Next.js App Router pages (RSC by default)
  (auth)/             Public routes
  (dashboard)/        Protected routes — middleware checks JWT
components/
  ui/                 Primitives (Button, Card, ...). NO data, NO state.
  intelligence/       Feature components (CompetitorCard, ScriptEditor, ...)
  charts/             Recharts wrappers
  layout/             Sidebar, TopBar
hooks/                One hook per resource. Wraps TanStack Query.
lib/
  api.ts              Single axios instance + typed sub-APIs
  auth.ts             Token storage, refresh logic
  utils.ts            cn(), formatters, date helpers
store/
  useStore.ts         Zustand for auth token + active channel ONLY
types/
  index.ts            Mirror of backend Pydantic schemas
```

**Critical:** the current repo is missing `lib/`. Every UI component imports `cn` from `@/lib/utils` and every hook/page imports from `@/lib/api`. Without that folder the app does not compile. The `.gitignore`'s `lib/` rule is eating it (collision with the Python build dir pattern). Fix: change to `/lib/` (root-anchored) or add `!frontend/lib/`.

### 8.2 Data fetching rules

- **Server Components fetch directly** (e.g. dashboard page reads channels server-side, hydrates the client).
- **Mutations always go through TanStack Query mutations** — never raw fetch — so cache invalidation is centralized.
- **`staleTime` defaults to 5 min, `gcTime` to 30 min.** Override per resource:
  - Channel list: 5min stale (changes when user adds one).
  - Trends: 1h stale (refreshed daily server-side).
  - Scripts: 0min stale (always fresh after generation).
- **Polling** for long-running jobs uses `refetchInterval` set to 3s while `data?.status` is non-terminal, then `false`.

### 8.3 The `lib/api.ts` I'd ship

Single axios instance, JWT injected via interceptor, retry on 429/5xx with exp backoff, automatic logout on 401.

```ts
// Sketched signature, full impl elsewhere
export const api = axios.create({ baseURL: process.env.NEXT_PUBLIC_API_URL });
api.interceptors.request.use(injectAuth);
api.interceptors.response.use(passthrough, retryAndUnauthHandler);

export const channelsApi = {
  list:        () => api.get<Channel[]>("/channels/"),
  get:         (id: string) => api.get<Channel>(`/channels/${id}`),
  connect:     (yt_id: string) => api.post<Channel>("/channels/connect", { youtube_channel_id: yt_id }),
  reanalyze:   (id: string) => api.post<{job_id: string}>(`/channels/${id}/re-analyze`),
};
// ... one object per resource, mirroring backend routers
```

---

## 9. Database performance

### 9.1 Indexes that pay rent

Every index here covers a query I expect to run > 100 times/day. Don't add more without measuring.

```sql
-- User lookup (auth)
users(email)                              UNIQUE

-- Channel access patterns
channels(user_id, created_at DESC)
channels(youtube_channel_id)              UNIQUE
channels(analysis_status) WHERE analysis_status IN ('pending','running')   -- partial

-- Video queries
videos(channel_id, published_at DESC)
videos(channel_id, view_count DESC) WHERE is_competitor_video = false      -- creator's top
videos(channel_id, view_count DESC) WHERE is_competitor_video = true       -- competitor's top
videos(channel_id, is_viral) WHERE is_viral = true                         -- partial, small
videos(youtube_video_id)                  UNIQUE

-- Vector ANN
videos USING ivfflat (content_embedding vector_cosine_ops) WITH (lists=100)
channels USING ivfflat (content_embedding vector_cosine_ops) WITH (lists=100)

-- Gaps
content_gaps(channel_id, opportunity_score DESC) WHERE is_acted_on = false

-- Jobs
analysis_jobs(entity_id, created_at DESC)
analysis_jobs(idempotency_key)            UNIQUE
analysis_jobs(status) WHERE status IN ('queued','running')
```

### 9.2 Connection pool sizing

```
pool_size=5, max_overflow=10, pool_timeout=30, pool_recycle=1800
```

Reasoning: free-tier Postgres allows 100 connections. Each web pod needs at most 15 (5 base + 10 burst). With 4 pods + 2 worker pods that's 90, leaving headroom for migrations and ad-hoc queries. The current value of `5+10` is correct; the docs claim `20+30` but the code is right — fix the docs.

### 9.3 N+1 prevention

Every `.options(selectinload(Channel.videos))` should be explicit. Add a tiny lint rule:

```python
# tests/test_no_lazy_loads.py
def test_no_implicit_lazy_loading(db_session):
    db_session.bind.echo = True
    # ... run typical request paths and assert query count thresholds
```

---

## 10. Security & multi-tenancy

### 10.1 Auth

- **JWT (HS256) with 7-day expiry.** Sufficient for SaaS, no need for refresh tokens until enterprise customers ask.
- **`SECRET_KEY` is 64 hex chars.** Generated by `openssl rand -hex 32`. Rotate via dual-key validation window (accept old + new for 7 days).
- **Google OAuth** for "Sign in with Google" + YouTube readonly scope. Backend exchanges code for tokens, stores `google_refresh_token` encrypted at rest (use Postgres `pgp_sym_encrypt` keyed by `SECRET_KEY`).

### 10.2 Authorization

Every route that touches a channel/script must verify `resource.user_id == current_user.id`. Wrap this in a dependency:

```python
def get_owned_channel(channel_id: UUID, user: User = Depends(get_current_user), db = Depends(get_db)):
    ch = db.query(Channel).filter_by(id=channel_id, user_id=user.id).first()
    if not ch:
        raise APIError(404, "NOT_FOUND")
    return ch
```

Use it in every route: `def endpoint(channel: Channel = Depends(get_owned_channel)): ...`. Removes whole class of IDOR bugs.

### 10.3 Plan gating

Two enforcement points:
1. **At write time** — `POST /channels/connect` checks `count(channels) < plan.max_channels`.
2. **In token budget middleware** — script/hook generation checks remaining tokens.

Plan limits live in code (not DB) until you need self-serve plan editing:

```python
PLAN_LIMITS = {
    "free":    {"channels": 1, "competitors": 3,  "scripts_per_month": 3,  "tokens": 100_000},
    "starter": {"channels": 1, "competitors": 5,  "scripts_per_month": 15, "tokens": 500_000},
    "pro":     {"channels": 5, "competitors": 10, "scripts_per_month": -1, "tokens": 2_000_000},
    "agency":  {"channels": 25,"competitors": 25, "scripts_per_month": -1, "tokens": 10_000_000},
}
```

### 10.4 Rate limiting

- **Per-IP** on auth endpoints: 20/min (slow brute force).
- **Per-user** on script/hook generation: 10/min (prevents accidental loops).
- **Per-user** on research: 5/min (Firecrawl bills by call).

Implement in Redis with token bucket. Already wired in `utils/rate_limiter.py`; wire into routes.

### 10.5 Input validation

- All UUIDs validated via `InputValidator.validate_uuid`.
- YouTube IDs match `^(UC[A-Za-z0-9_-]{22}|@[A-Za-z0-9._-]{1,30})$`.
- Free text fields capped at sane lengths (5000 chars for script topic, 200 for title).
- All scrape targets allowlisted by domain before passing to Firecrawl.

### 10.6 Secrets

- Env vars only, never in code, never in repo.
- `.env` in `.gitignore`. CI uses encrypted secrets.
- Production secrets in Railway/Vercel env config, not in `.env` files on disk.

---

## 11. Observability

Three signals, in order of value for this product:

### 11.1 Structured logs

Every log line includes `request_id`, `user_id` (if available), `route`, `latency_ms`. JSON format. Aggregate in any cheap log service (Axiom, Logtail).

### 11.2 Counters & timings

In-memory `MetricsCollector` is fine for now. Endpoints to expose:
- `request.<METHOD>.<path>` p50/p95/p99
- `llm.<engine>.<complexity>` count + token totals + cost totals
- `cache.<layer>.hit` / `cache.<layer>.miss`
- `youtube.api.units_used` (cumulative daily)
- `circuit_breaker.<service>.state`

Migrate to Prometheus client when you have > 2 pods (in-memory metrics fragment).

### 11.3 Errors

Sentry. One DSN, sourcemaps for the frontend, breadcrumbs on every API call. Alert thresholds:
- `> 5 errors/min` for any route → page on-call.
- `circuit_breaker_open` → page on-call.
- `youtube.api.units_used > 9000/day` → warning (we're 90% of free tier).

### 11.4 Cost tracking

`token_budget.log_token_consumption` already logs per-call. Forward those to a `llm_calls` table:

```sql
CREATE TABLE llm_calls (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  operation TEXT NOT NULL,            -- 'creator_analysis', etc.
  model TEXT NOT NULL,
  input_tokens INT, output_tokens INT,
  cost_usd NUMERIC(10,6),
  cached BOOLEAN,
  duration_ms INT,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

Materialized view `mv_llm_cost_per_user_per_day` rebuilt nightly. Powers the per-user cost dashboard and informs plan pricing.

---

## 12. Phased rollout plan

The shortest path from current code to a launchable product. Each phase is independently shippable.

### Phase 0 — make it run (1 day)

Right now the project doesn't start. Fix:

1. Create `frontend/lib/{api.ts,auth.ts,utils.ts}` (every component imports from it). Update `.gitignore` to scope the `lib/` rule to `/lib/` so it stops getting eaten.
2. Replace `conn.execute("SELECT 1")` with `conn.execute(text("SELECT 1"))` in `main.py:96`.
3. Drop `openrouter-python==0.4.0` from `requirements.txt` (phantom package).
4. Set `EMBEDDING_MODEL=openai/text-embedding-3-small` (current value is a chat model).
5. Add baseline alembic migration that creates the schema + `CREATE EXTENSION vector`.
6. Remove the broken `uploads_playlist_id` reference in `main.py`'s startup recovery — replace with workers + locks (Phase 2).

### Phase 1 — correctness (3 days)

7. Move all background work from `threading.Thread` to Celery. Single worker config, `task_acks_late=True`, idempotency keys.
8. Wire rate limits into auth, script, hook, research routes.
9. Add `get_owned_channel` dependency, audit every route for cross-tenant access.
10. Add LLM response cache (§4.5) — 30 lines of code, 40% cost reduction.
11. Replace `gap_detector.detect_gaps` with the embedding-based version (§4.4).

### Phase 2 — production readiness (1 week)

12. Stripe integration: `POST /billing/create-checkout`, webhook handler, subscription state on `User`. Plan changes invalidate token budget caches.
13. Email notifications via Resend or SES. Templates: welcome, analysis complete, plan limit warning, monthly summary.
14. Sentry, structured logs to Axiom, basic alerts.
15. Test suite. Start with the 20 most-trafficked routes; aim for 70% line coverage on `routers/` and `intelligence/`.
16. Stress test with k6 on the analysis pipeline. Verify the lock prevents double-runs.

### Phase 3 — scale (2 weeks)

17. Distributed rate limiter (Redis-backed, replace in-memory).
18. WebSocket push for analysis-job progress (replaces polling).
19. Per-user `llm_calls` table + cost dashboard.
20. YouTube PubSubHubbub for real-time competitor upload alerts.

### Phase 4 — growth features

21. PDF export for scripts and competitor reports (weasyprint).
22. Team accounts (multi-user per channel).
23. Public API + API keys.

---

## Appendix A — directory structure (target)

```
backend/
  app/
    __init__.py
    main.py                      # Thin: middleware, lifespan, router include
    config.py                    # Settings via pydantic-settings
    database.py                  # Engine, SessionLocal, get_db, get_db_session
    deps.py                      # Shared FastAPI deps (get_current_user, get_owned_channel)
    routers/                     # Thin HTTP only
      auth.py
      channels.py
      competitors.py
      gaps.py
      scripts.py
      hooks.py
      thumbnails.py
      trends.py
      audience.py
      research.py
      billing.py                 # NEW: Stripe webhooks
      jobs.py                    # NEW: GET /jobs/{id} status
    schemas/                     # Pydantic request/response
    models/                      # SQLAlchemy ORM
    intelligence/                # AI engines (pure functions, no IO)
      creator_analyzer.py
      competitor_engine.py
      gap_detector.py
      script_generator.py
      hook_engine.py
      thumbnail_engine.py
      audience_engine.py
      trend_engine.py
      retention_engine.py
      viral_engine.py
    prompts/                     # Templated strings
    services/                    # External IO + caching
      youtube_service.py
      openrouter_service.py
      scraper_service.py
      whisper_service.py
      embedding_service.py
      redis_cache.py
      async_http.py
      token_budget.py
      email_service.py           # NEW: transactional email
      stripe_service.py          # NEW
    tasks/                       # Celery
      celery_app.py
      channel_tasks.py
      competitor_tasks.py
      trend_tasks.py
      email_tasks.py             # NEW
    utils/
      auth_utils.py
      base.py                    # Validators, ETag, MetricsCollector
      cache_manager.py
      rate_limiter.py
      resilience.py
      source_validator.py
      text_utils.py
  alembic/
    env.py
    versions/
      0001_baseline.py           # NEW: full schema + CREATE EXTENSION vector
      0002_add_indexes.py
  tests/                         # NEW
    conftest.py
    test_auth.py
    test_channels.py
    ...
  requirements.txt
  Dockerfile

frontend/
  app/
    layout.tsx, page.tsx, providers.tsx
    (auth)/login, register
    (dashboard)/...
    onboarding/
  components/
    ui/                          # Primitives
    intelligence/                # Feature components
    charts/
    layout/
  hooks/                         # One per resource
  lib/                           # MISSING in current repo — see Phase 0
    api.ts
    auth.ts
    utils.ts
  store/useStore.ts
  types/index.ts
```

---

## Appendix B — design choices I'd argue for in review

| Decision | Why | What I'd reject |
|---|---|---|
| Single Postgres + pgvector | Simpler ops, plenty fast for < 1M videos | Pinecone — pay $70/mo for query latency we don't need |
| OpenRouter, not direct provider SDKs | One key, automatic fallback, cost routing | Maintaining OpenAI + Anthropic + Together clients |
| Celery + Redis broker | Mature, observable, simple ops | RQ (less observability), Temporal (overkill) |
| Cursor pagination | Stable under inserts, scales to millions | Page-number — breaks when items added mid-scroll |
| Plan limits in code | Read-only product config, easy to test | Plans table + admin UI before we have an admin |
| JWT with no refresh tokens | Simplicity; users sign back in weekly | Refresh + rotation until enterprise asks |
| Embedding-based gap detection | Data-driven, deterministic part is in SQL | Pure-LLM gap detection — too expensive, drifts |
| FastAPI + Pydantic v2 | Best-in-class DX, automatic OpenAPI | Django (heavier), Litestar (smaller community) |
| TanStack Query over Redux | Server state ≠ client state | Putting server data in Zustand |
| Tailwind | Fast iteration, stable design tokens | CSS-in-JS — runtime cost, harder server components |

---

## Appendix C — what *not* to build (yet)

- **No GraphQL.** REST is fine. Flexible queries aren't a real user need.
- **No real-time anything.** Polling at 3s is sufficient for analysis jobs.
- **No microservices.** One web app, one worker, one DB.
- **No multi-region.** US-East is fine for v1.
- **No A/B testing framework.** Use Vercel Edge Config or hardcode flags until you have > 1000 paying users.
- **No mobile app.** The web app is mobile-responsive; revisit at 5000 paying users.
- **No multi-language.** English only. Localization is a quagmire pre-PMF.

---

## Closing note

The codebase is closer to "done" than the docs suggest, but the gap between "compiles in dev" and "runs reliably for 1000 paying users" is exactly the work in Phases 0-2 above. The intelligence engines and prompts are the genuinely valuable IP — protect their quality with the cache + token-budget + plan-gating discipline laid out here, and the unit economics work.
