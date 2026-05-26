# GTM Pendings

> Honest audit of everything still missing before we can take paying users.
> Items grouped by severity. Estimates are for a single focused engineer.

**Total to GTM-ready: ~7-10 working days.**

---

## 🔴 Hard blockers (cannot launch)

These either break user flows or violate terms of service / payment requirements.

### 1. No payment processing
- `backend/app/routers/billing.py` returns `503` for `create-checkout` and `create-portal`. Stripe is a stub.
- No subscription state on `User` (no `stripe_customer_id`, no `stripe_subscription_id`, no `current_period_end`).
- **Effort:** 3-4 days
- **Tasks:**
  - Stripe products + prices in dashboard (one per plan)
  - Implement `POST /billing/create-checkout` (real Stripe SDK call)
  - Implement `POST /billing/webhook` for `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`
  - Add Stripe columns to `users` table via Alembic migration
  - Implement `POST /billing/create-portal` for self-serve subscription management

### 2. Embeddings never get generated
- `gap_detector` queries `videos.content_embedding`, but `routers/channels.py` background analysis never calls `get_content_embedding()` and never writes to that column.
- Result: gap detection silently falls back to title-string matching every time. Major feature is broken.
- **Effort:** 1 day
- **Tasks:**
  - In `run_full_channel_analysis`, after saving videos, batch top 50 video titles through `embedding_service.get_content_embedding()`
  - Save back to `Video.content_embedding`
  - Same for competitor videos when they're analyzed
  - Optional: also embed `Channel.content_embedding` from creator profile text

### 3. Token usage tracking is wired but unused
- `openrouter_service.call_openai` accepts `user_id` and tracks tokens, but **no engine passes `user_id`** when it calls.
- Result: every paying user shows 0 tokens consumed. Plan budget enforcement is theater.
- **Effort:** half a day
- **Tasks:**
  - Thread `user_id` through every engine method signature (`creator_analyzer`, `gap_detector`, `script_generator`, `hook_engine`, etc.)
  - Pass it to `call_openai(..., user_id=str(current_user.id))` everywhere
  - Add a smoke test: generate a script, then `GET /auth/usage` and verify tokens > 0

### 4. No password reset flow
- Users who forget their password are stuck.
- **Effort:** 1 day
- **Tasks:**
  - `POST /auth/forgot-password` — generates time-limited token, emails reset link
  - `POST /auth/reset-password` — validates token, sets new password
  - Frontend pages for both flows
  - Email template

### 5. Google OAuth callback page is missing
- `frontend/app/(auth)/login/page.tsx:37` redirects to `${origin}/auth/callback`.
- That route does not exist in the frontend. OAuth currently 404s after Google redirects back.
- **Effort:** half a day
- **Tasks:**
  - Add `frontend/app/auth/callback/page.tsx`
  - Reads `?code=...` from query
  - Calls `authApi.googleCallback(code)`
  - Stores token via `setAccessToken`, fetches user via `authApi.me()`, redirects to `/dashboard`
  - Handle error states gracefully

### 6. No legal pages
- No `/privacy`, no `/terms`. Stripe will refuse to activate the account without these.
- Google OAuth requires a privacy policy URL during verification.
- **Effort:** half a day
- **Tasks:**
  - Generate boilerplate via Termly or GetTerms.io
  - `frontend/app/privacy/page.tsx`
  - `frontend/app/terms/page.tsx`
  - Link from footer + during signup
  - Add `privacy_policy_url` to Google OAuth consent screen config

### 7. Anything-goes registration (no email verification)
- Users sign up with any email, immediately hit free-tier limits, can spam-create accounts.
- **Effort:** 1 day
- **Tasks:**
  - Send verification email on register
  - Add `is_verified` check on plan-upgrade and channel-connect routes
  - `GET /auth/verify-email/{token}` endpoint
  - Frontend `verify-email/[token]/page.tsx`

---

## 🟡 Soft blockers (you'll regret launching without these)

### 8. No error monitoring
- Sentry not installed. Production errors discovered via angry support emails.
- **Effort:** 1 hour
- **Tasks:**
  - `pip install sentry-sdk[fastapi]`
  - Add DSN in env vars
  - Initialize in `main.py` startup
  - Same on frontend with `@sentry/nextjs`

### 9. No transactional email provider configured
- `email_service.py` logs instead of sending unless `RESEND_API_KEY` is set.
- Cannot send welcome emails, password resets, or analysis-complete notifications.
- **Effort:** 30 min
- **Tasks:**
  - Sign up for Resend (free tier: 3000 emails/mo)
  - Verify sending domain (DNS records)
  - Drop `RESEND_API_KEY` and `EMAIL_FROM` in env

### 10. Background jobs run on FastAPI threads
- `BackgroundTasks` runs in-process. Pod restart kills running analyses.
- Channels stuck in `"running"` forever (startup recovery is a band-aid).
- Multiple pods can't coordinate — both try the same recovery.
- **Effort:** 2 days
- **Tasks:**
  - Wire up Celery worker process (config already exists in `tasks/celery_app.py`)
  - Replace `background_tasks.add_task(...)` with `celery_task.delay(...)` in `routers/channels.py` and `routers/competitors.py`
  - Add Redis-based per-channel lock to prevent duplicate analysis
  - Update `analysis_jobs` table with `current_step` updates as the worker progresses
  - Add Procfile or docker service for the worker

### 11. No CI/CD
- No GitHub Actions, no automated tests on PR.
- **Effort:** 2 hours
- **Tasks:**
  - `.github/workflows/test.yml` — lint + pytest on PR
  - `.github/workflows/deploy.yml` — deploy on merge to `main`

### 12. No deployment config
- `docker-compose.yml` for local dev only. No Railway/Fly/Vercel files.
- **Effort:** half a day
- **Tasks:**
  - `railway.json` or `fly.toml` for backend
  - Vercel project linked for frontend
  - Production env vars set in dashboards
  - Verify `/health/ready` works in deployed env

### 13. Frontend error boundaries not wrapping critical paths
- `ErrorBoundary` component exists but isn't wrapping route content.
- One unhandled rejection whitescreens the user.
- **Effort:** 2 hours
- **Tasks:**
  - Wrap `(dashboard)/layout.tsx` content in `<ErrorBoundary>`
  - Add fallback UIs with "try again" + report-issue link

### 14. Onboarding requires YouTube API credentials
- Users without a connectable channel have no path through the app.
- Most YouTubers want to demo before signing in.
- **Effort:** 1-2 days
- **Tasks:**
  - Add public "demo mode" — paste any channel URL, get a one-shot analysis
  - Gate write features (save, generate scripts) behind login
  - Conversion CTA: "Sign up to keep these results"

---

## 🔵 Polish (do before paid acquisition)

### 15. No analytics
- No PostHog / Mixpanel / Plausible. No conversion funnel data.
- **Effort:** 2 hours
- **Tasks:**
  - PostHog snippet in `frontend/app/layout.tsx`
  - Track key events: signup, channel_connected, script_generated, plan_upgraded
  - Track funnel: landing → signup → onboarding → first-script

### 16. No marketing surface
- Landing page exists. No docs site, no public pricing page, no changelog.
- **Effort:** 1-2 days
- **Tasks:**
  - Public pricing page (not gated behind login)
  - Simple docs at `/docs` covering "How it works"
  - `/changelog` reading from CHANGELOG.md
  - Compare-features table for plans

### 17. No customer support surface
- No Intercom/Crisp widget, no `support@` email in the UI.
- **Effort:** 1 hour
- **Tasks:**
  - Crisp or Plain widget on `(dashboard)` layout
  - Footer link to `support@creatoriq.io`
  - Status page link

### 18. SEO basics missing
- `metadata` is good in `layout.tsx` but no `sitemap.xml`, `robots.txt`, or per-page `og:image`.
- **Effort:** 2-3 hours
- **Tasks:**
  - `frontend/app/sitemap.ts` (Next.js auto-handles)
  - `frontend/public/robots.txt`
  - Per-page OG images (use `@vercel/og` for dynamic generation)
  - Schema.org markup on landing page

### 19. No abuse protection beyond rate limits
- No CAPTCHA on register. Single IP can register 100 accounts in a minute.
- No fraud detection on OAuth path.
- **Effort:** 2 hours
- **Tasks:**
  - hCaptcha on `/register`
  - Per-IP rate limit on `/auth/register` (10/hour)
  - Email-domain blocklist for known throwaway providers

### 20. Backend exposed directly to internet
- Anyone can `curl` the API. Auth gates it but enables abuse exploration.
- **Effort:** 1 hour
- **Tasks:**
  - Put Cloudflare in front
  - Verify request signature header (frontend includes a known secret)
  - Tighten CORS allowlist for production

---

## Recommended execution order

| Day | Items |
|-----|-------|
| 1 | #2 embeddings + #3 user_id threading — silently broken features |
| 2 | #5 OAuth callback page + #4 password reset |
| 3 | #6 legal pages + #7 email verification |
| 4-7 | #1 Stripe end-to-end |
| 8 | #8 Sentry + #9 Resend + #11 CI |
| 9 | #10 Celery + #12 deploy config |
| 10 | Buffer — manual run-through of full signup→pay→generate flow |

After that:
- Soft-launch to Product Hunt or niche subreddits (r/NewTubers, r/youtubers).
- Watch 20 real users walk through onboarding before paying for ads.
- At least 3 of them should complete a script generation without help.
- Iterate based on the data, not opinions.

The product is closer than it looks. Blockers are the boring stuff: payments, password resets, legal, error monitoring. Knock them out, then ship.
