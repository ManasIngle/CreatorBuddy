# CreatorIQ Cost Analysis

This document provides a comprehensive breakdown of operational costs for the CreatorIQ platform, enabling informed pricing strategy and cost optimization decisions.

---

## 1. Infrastructure Costs (Monthly Estimates)

### Railway (Backend Hosting)

| Tier | Price | Resources | Use Case |
|------|-------|-----------|----------|
| Basic | $5/mo | 0.5 GB RAM, shared CPU | Development/Staging |
| Standard | $20/mo | 2 GB RAM, 2 vCPU | Small production (up to 500 users) |
| Pro | $50/mo | 4 GB RAM, 4 vCPU | Medium production (500-2000 users) |

**Recommendation:** Start with Standard, scale to Pro as user base grows.

### PostgreSQL + pgvector (Railway)

| Tier | Price | Storage | RAM | Use Case |
|------|-------|---------|-----|----------|
| Basic | $5/mo | 1 GB | 256 MB | Dev/Light usage |
| Standard | $15/mo | 10 GB | 1 GB | Production (up to 500 users) |
| Pro | $50/mo | 100 GB | 4 GB | Heavy usage (2000+ users) |

**Vector Embedding Costs:** pgvector adds ~20% to storage needs for embedding storage.

### Redis (Railway)

| Tier | Price | Memory | Use Case |
|------|-------|--------|----------|
| Basic | $3/mo | 30 MB | Caching only |
| Pro | $10/mo | 1 GB | Sessions + caching + rate limiting |

**Recommendation:** Pro tier for production to handle session management and aggressive caching.

### Vercel (Frontend)

| Tier | Price | Bandwidth | Use Case |
|------|-------|-----------|----------|
| Hobby | Free | 100 GB/mo | Development |
| Pro | $20/mo | 1 TB/mo | Production |

**Per-User Calculation:**
- Average session: ~50 MB bandwidth
- 10,000 sessions/month = ~500 MB
- Well within free tier for small deployments

### Domain + SSL

- Domain registration: ~$12/year
- SSL: Included with Vercel Pro and Railway
- **Total:** ~$15/year

### Infrastructure Summary

| Scale | Monthly Cost |
|-------|-------------|
| Small (100 users) | $50-60 |
| Medium (500 users) | $150-200 |
| Large (2000 users) | $400-500 |

---

## 2. External API Costs

### OpenRouter (LLM)

Pricing per 1M tokens (input + output combined):

| Model | Input Cost | Output Cost | Effective Rate | Best For |
|-------|------------|-------------|----------------|----------|
| Llama 3 8B | $0.20 | $0.20 | $0.20/1M | Simple tasks, summarization |
| GPT-4o-mini | $0.15 | $0.60 | ~$0.75/1M | General purpose, hooks, titles |
| GPT-4o | $2.50 | $10.00 | ~$12.50/1M | Vision analysis, complex reasoning |
| Claude-3-haiku | $0.25 | $1.25 | ~$1.50/1M | High-quality creative writing |

**Cost Optimization:** Use `ultra_cheap` model for simple operations (hook generation, title suggestions). Reserve GPT-4o for thumbnail vision analysis only.

### YouTube Data API v3

| Quota | Cost |
|-------|------|
| Free tier | 10,000 units/day |
| Beyond free | $0.002 per 1,000 units |

**Unit costs by operation:**
- `videos.list`: 1 unit
- `channels.list`: 1 unit
- `search.list`: 100 units
- `playlistItems.list`: 1 unit

**Calculation:** 10,000 free units ≈ 10,000 video fetches or 100 search queries daily.

### Firecrawl (Web Scraping)

| Tier | Price | Pages/Month | Cost per 1000 Pages |
|------|-------|-------------|---------------------|
| Free | $0 | 500 | $0 |
| Starter | $15 | 5,000 | $3.00 |
| Pro | $99 | 50,000 | $1.98 |

**Use Cases:**
- Deep research: ~10-20 pages per query
- Competitor analysis: ~5 pages per competitor
- Content gap detection: ~15 pages per analysis

### Whisper API (Transcription)

| Metric | Cost |
|--------|------|
| Per minute | $0.006 |
| Average video (12 min) | $0.072 |
| Per channel analysis (3 videos) | $0.22 |

**Optimization:** Only fetch transcripts for top-performing videos (sorted by view count).

---

## 3. Operation Cost Breakdown (Per Operation)

Ranked from highest to lowest cost:

### 1. Full Script Generation (~3000 tokens output)

| Component | Calculation | Cost |
|-----------|-------------|------|
| Input | ~1000 tokens × gpt-4o-mini ($0.00015/1K) | $0.00015 |
| Output | 3000 tokens × gpt-4o-mini ($0.00060/1K) | $0.00180 |
| **Total** | | **~$0.002 per script** |

**Optimization:** Use cached prompts and context compression.

### 2. Thumbnail Vision Analysis (GPT-4o)

| Component | Calculation | Cost |
|-----------|-------------|------|
| Input | ~500 tokens + image = ~$0.005 | $0.005 |
| Output | ~300 tokens = $0.003 | $0.003 |
| **Total** | | **~$0.008 per analysis** |

**Note:** This is the most expensive single operation. Consider caching successful analyses.

### 3. Deep Research (Multiple sources)

| Component | Cost |
|-----------|------|
| Web scraping (10-20 pages) | $0.03-0.10 |
| AI synthesis (~5000 tokens) | $0.01-0.05 |
| **Total** | **~$0.01-0.05 per query** |

**Optimization:** Aggressive caching—research results rarely change hourly.

### 4. Full Channel Analysis (Background job)

| Component | Cost |
|-----------|------|
| 50 video stats fetch (YouTube API) | $0.0001 |
| 3 transcript fetches (Whisper) | $0.22 |
| AI analysis (creator profile) | $0.002 |
| **Total** | **~$0.02-0.05 per channel** |

**Optimization:** Prioritize videos by view count; skip low-performers.

### 5. Competitor Analysis

| Component | Cost |
|-----------|------|
| 5 video analysis | $0.01 |
| Web scraping (5 pages) | $0.015 |
| AI analysis | $0.002 |
| **Total** | **~$0.01-0.02 per competitor** |

### 6. Content Gap Detection

| Component | Cost |
|-----------|------|
| Web scraping (Reddit, forums) | $0.005-0.01 |
| AI analysis | $0.002 |
| **Total** | **~$0.005-0.01 per detection** |

### 7. Hook Generation (5 hooks)

| Component | Calculation | Cost |
|-----------|-------------|------|
| Input | ~500 tokens × gpt-4o-mini | $0.00008 |
| Output | 5 hooks × 100 tokens = 500 tokens | $0.00030 |
| **Total** | | **~$0.0004 per hook** |

**Batch generation:** Generate all 5 hooks in single call = ~$0.002 total.

### 8. Title Suggestions (3 options)

| Component | Cost |
|-----------|------|
| AI generation | ~$0.001 per request |
| **Total** | **~$0.001 for 3 titles** |

### 9. Simple API Calls (No AI)

| Operation | Cost |
|-----------|------|
| Channel stats retrieval | ~$0.0001 |
| Video metadata fetch | ~$0.0001 |
| Search queries | ~$0.0002 |

---

## 4. Monthly Cost Scenarios

### Small Scale: 100 Active Users

| Operation | Volume | Cost |
|-----------|--------|------|
| Channel analyses | 50 | $1.00-2.50 |
| Competitor analyses | 20 | $0.20-0.40 |
| Script generations | 500 | $1.00 |
| Hook generations | 1,000 | $0.40 |
| Deep research | 50 | $0.50-2.50 |
| **LLM Subtotal** | | **$5-10/month** |
| Infrastructure (Standard) | | $50/month |
| **Total** | | **$55-65/month** |
| **Cost per user** | | **$0.55-0.65** |

### Medium Scale: 500 Active Users

| Operation | Volume | Cost |
|-----------|--------|------|
| Channel analyses | 200 | $4.00-10.00 |
| Competitor analyses | 100 | $1.00-2.00 |
| Script generations | 5,000 | $10.00 |
| Hook generations | 10,000 | $4.00 |
| Deep research | 500 | $5.00-25.00 |
| **LLM Subtotal** | | **$50-100/month** |
| Infrastructure | | $150/month |
| **Total** | | **$200-250/month** |
| **Cost per user** | | **$0.40-0.50** |

### Large Scale: 2,000 Active Users

| Operation | Volume | Cost |
|-----------|--------|------|
| Channel analyses | 1,000 | $20.00-50.00 |
| Competitor analyses | 500 | $5.00-10.00 |
| Script generations | 50,000 | $100.00 |
| Hook generations | 100,000 | $40.00 |
| Deep research | 5,000 | $50.00-250.00 |
| **LLM Subtotal** | | **$500-1000/month** |
| Infrastructure | | $400/month |
| **Total** | | **$900-1400/month** |
| **Cost per user** | | **$0.45-0.70** |

### Scale Economics

| Users | Monthly Cost | Cost per User | Margins at 3x Markup |
|-------|-------------|---------------|---------------------|
| 100 | $60 | $0.60 | $1.80/revenue |
| 500 | $225 | $0.45 | $1.35/revenue |
| 2,000 | $1,150 | $0.58 | $1.73/revenue |

---

## 5. Cost Optimization Strategies

### LLM Cost Reduction

1. **Model Tiering**
   - Use `ultra_cheap` for: hooks, titles, simple classifications
   - Use `cheap` for: script generation, content analysis
   - Use `standard` for: competitor analysis, audience insights
   - Use `premium` for: thumbnail vision analysis ONLY

2. **Prompt Compression**
   - Strip redundant context
   - Use compression utilities before sending
   - Target: 30% token reduction

3. **Caching**
   - Cache all AI responses with 24-hour TTL minimum
   - Cache research results for 7 days
   - Cache competitor analysis for 48 hours
   - Target: 95%+ cache hit rate for reads

### API Cost Reduction

1. **YouTube API Optimization**
   - Always use free quota first (10K units/day)
   - Batch video fetches where possible
   - Cache channel stats for 1 hour
   - Skip low-view videos for transcript fetches

2. **Web Scraping Optimization**
   - Limit concurrent scrapes
   - Cache scraped content for 24 hours
   - Use free Firecrawl tier for development
   - Compress stored content

3. **Transcription Optimization**
   - Only transcribe videos with 100K+ views
   - Use YouTube captions when available (free)
   - Skip transcript for deleted/unavailable videos

### Infrastructure Optimization

1. **Railway Scaling**
   - Scale down during off-peak (night hours)
   - Use Basic tier for non-production environments

2. **Redis Caching**
   - Aggressive caching of API responses
   - Session store for authenticated users
   - Rate limiting counters

3. **Database Optimization**
   - Regular vacuum and analyze
   - Index maintenance
   - Archive old data to reduce storage

### Implementation Checklist

- [ ] Implement model tiering by operation type
- [ ] Add response caching layer with Redis
- [ ] Compress prompts before AI calls
- [ ] Batch YouTube API requests
- [ ] Limit transcript fetches to high-performers
- [ ] Set up rate limiting on expensive endpoints
- [ ] Monitor cache hit rates weekly

---

## 6. Pricing Tier Recommendations

Based on cost analysis, recommended pricing structure:

### Free Tier

| Feature | Limit | Your Cost |
|---------|-------|-----------|
| Script generations | 10/month | $0.02 |
| Hook generations | 20/month | $0.008 |
| Channel tracking | 1 | $0.001 |
| Basic analytics | Yes | $0 |
| **Monthly cost** | | **~$0.03** |

**Purpose:** Acquisition funnel, demonstrate value

### Starter Tier — $19/month

| Feature | Limit | Your Cost |
|---------|-------|-----------|
| Script generations | 100/month | $0.20 |
| Hook generations | 500/month | $0.20 |
| Deep research | 10/month | $0.25 |
| Channel tracking | 5 | $0.15 |
| Competitor tracking | 3 | $0.04 |
| Content gap detection | 20/month | $0.10 |
| **Monthly cost** | | **~$1.00** |
| **Margin** | | **~18x** |

### Pro Tier — $49/month

| Feature | Limit | Your Cost |
|---------|-------|-----------|
| Script generations | 500/month | $1.00 |
| Hook generations | 2,000/month | $0.80 |
| Deep research | 50/month | $1.25 |
| Channel tracking | 20 | $0.60 |
| Competitor tracking | 10 | $0.15 |
| Content gap detection | 100/month | $0.50 |
| Thumbnail analysis | 25/month | $0.20 |
| Priority processing | Yes | $0 |
| **Monthly cost** | | **~$4.50** |
| **Margin** | | **~11x** |

### Agency Tier — $149/month

| Feature | Limit | Your Cost |
|---------|-------|-----------|
| Script generations | Unlimited | $5.00 |
| Hook generations | Unlimited | $3.00 |
| Deep research | 200/month | $5.00 |
| Channel tracking | 50 | $1.50 |
| Competitor tracking | 25 | $0.40 |
| Content gap detection | Unlimited | $2.00 |
| Thumbnail analysis | 100/month | $0.80 |
| Priority processing | Yes | $0 |
| Team collaboration | Yes | $0 |
| API access | Limited | $0 |
| **Monthly cost** | | **~$18.00** |
| **Margin** | | **~8x** |

### Enterprise — Custom

Contact sales for volume pricing. Target 5-6x margin at this level.

---

## 7. Revenue Projections

### Conservative Estimates (30% conversion to paid)

| Users | Free Users | Paid Users | Revenue |
|-------|-----------|------------|---------|
| 100 | 70 | 30 | $570-1,170/mo |
| 500 | 350 | 150 | $2,850-5,850/mo |
| 2,000 | 1,400 | 600 | $11,400-23,400/mo |

### Break-Even Analysis

| Scale | Monthly Cost | Break-Even Users (Starter) |
|-------|-------------|---------------------------|
| Small | $60 | 4 |
| Medium | $225 | 12 |
| Large | $1,150 | 61 |

---

## 8. Appendix: Cost Calculation Formulas

### Per-Operation Cost Formula

```
operation_cost = (input_tokens × input_rate) + (output_tokens × output_rate) + external_api_costs
```

### Monthly Infrastructure Cost

```
infra_cost = railway_cost + postgres_cost + redis_cost + vercel_cost + domain_cost
```

### User-Based Cost Projection

```
monthly_cost = (operations_per_user × operations_count × operation_cost) + infra_cost
```

---

## Document Version

- **Version:** 1.0
- **Last Updated:** 2026-01-15
- **Review Cycle:** Quarterly