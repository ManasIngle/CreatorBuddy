# CreatorIQ API Changelog

All notable changes to the CreatorIQ API will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2024-01-01

### Added

#### Authentication
- `POST /api/v1/auth/register` - User registration with email/password
- `POST /api/v1/auth/login` - OAuth2 password flow login
- `GET /api/v1/auth/me` - Get current authenticated user
- `POST /api/v1/auth/google/callback` - Google OAuth integration

#### Channel Management
- `POST /api/v1/channels/connect` - Connect YouTube channel
- `GET /api/v1/channels/` - List connected channels
- `GET /api/v1/channels/{channel_id}` - Get channel details
- `POST /api/v1/channels/{channel_id}/re-analyze` - Trigger re-analysis

#### Competitor Intelligence
- `POST /api/v1/competitors/{channel_id}/add` - Add competitor channel
- `GET /api/v1/competitors/{channel_id}/` - List competitors
- `GET /api/v1/competitors/{channel_id}/{competitor_id}` - Get competitor details
- `DELETE /api/v1/competitors/{channel_id}/{competitor_id}` - Remove competitor

#### Content Gap Detection
- `POST /api/v1/gaps/{channel_id}/detect` - Trigger gap detection
- `GET /api/v1/gaps/{channel_id}/` - List content gaps
- `POST /api/v1/gaps/{channel_id}/gaps/{gap_id}/acted-on` - Mark gap as acted on

#### Script Generation
- `POST /api/v1/scripts/generate` - Generate AI script
- `GET /api/v1/scripts/` - List user scripts
- `GET /api/v1/scripts/{script_id}` - Get script details
- `DELETE /api/v1/scripts/{script_id}` - Delete script

#### AI Intelligence Engines
- Creator Analyzer - Analyzes channel content style and personality
- Competitor Engine - Deep competitor analysis and pattern extraction
- Gap Detector - Identifies content opportunities
- Script Generator - Creates complete video scripts with hooks
- Hook Engine - Viral hook pattern analysis and generation
- Thumbnail Engine - CTR analysis and recommendations
- Audience Engine - Psychology-based audience insights
- Retention Engine - Retention pattern analysis
- Viral Engine - Viral content pattern detection

#### Infrastructure
- PostgreSQL with pgvector for vector similarity search
- Celery background task processing
- Redis broker for task queue
- JWT authentication with configurable expiration
- CORS middleware for frontend integration
- Request ID tracking for debugging

### Response Headers
All API responses include:
- `API-Version` - Current API version (e.g., "1.0.0")
- `X-Request-ID` - Unique request identifier for debugging

### Error Response Format
All errors follow a consistent format:
```json
{
  "detail": "Human-readable error message",
  "code": "MACHINE_READABLE_ERROR_CODE"
}
```

### Rate Limiting
Rate limiting is configured but not yet enforced. Expected limits:
- Free tier: 100 requests/minute
- Pro tier: 1000 requests/minute
- Agency tier: 5000 requests/minute

## [1.1.0] - 2026-05-23

### Added

#### SaaS Plan Enforcements & Gating
- Connected YouTube channels limits: Free/Starter (1 max), Pro (5 max), Agency (25 max).
- Competitor tracking limits: Free (3 max), Starter (5 max), Pro (10 max), Agency (25 max).
- Monthly script generation limits: Free (3 scripts/mo), Starter (15 scripts/mo), Pro/Agency (unlimited).
- Token budget gating: Active token allowance checks on hook and script generation.
- Dynamic subscription tiers support: Integrated plan column checks on user profile with PUT `/api/v1/auth/plan` updating plan instantly.

#### Technical AI & Model Upgrades
- Primary OpenRouter models upgraded: Llama 3.1 8B, Claude 3.5 Haiku, Claude 3.5 Sonnet, Gemini 1.5 Flash.
- Modern Model Costing structures: Synced local estimation trackers to match modern token rates.
- AI Model Cost Routing: Integrated `complexity="simple"` for title and hook generation (saving ~70% token costs).
- Deprecated legacy `openai_service.py` with a thin re-export warning shim.

#### Caching & Web Scraping Optimization
- YouTube API caching: Redis cache helpers for channel metadata details (1-hour TTL) inside `connect_channel`.
- Distributed Scraping Cache: Synchronized `CacheManager` with Redis-backed namespace caching for topic research, trends, audience insights, and SEO data.
- Fallback Web Scraper HTML parsing: Added standard library `HTMLTextExtractor` and `clean_html` regex helpers in `_fallback_scrape` to clean HTML code and save LLM token waste.

#### Database & Server Optimization
- Connection Pool Scaling: Reduced SQLAlchemy engine pool from 50 to 15 (5 base, 10 overflow) to protect PostgreSQL limits.
- Foreign Key Database Indexes: Created manual Alembic baseline migration script `20260523_1000_add_missing_indexes.py` for `user_id` and `channel_id` indexes.
- Startup Recovery: Added daemon thread restart triggers inside FastAPI `startup_event` to resume stuck channel analyses.

#### Frontend Core Additions & UX
- **Root Landing Page (`/`)**: Implemented a responsive glassmorphic landing page showcasing features, CTAs, UI mockup, and creator pricing.
- **Fullscreen Onboarding Flow (`/onboarding`)**: Implemented a multi-step fullscreen onboarding wizard with profiles setup, channel connections, and real-time database AI sync checkmarks.
- **TanStack Query staleTime Defaults**: Implemented global `Providers` QueryClient setup with 5-minute staleTime and 30-minute gcTime.
- **Pricing Management Modal**: Developed interactive subscription grid in `settings/page.tsx` + upsell cards in sidebar layout.

## [Unreleased]

### Added

#### Web Scraping Intelligence
- Firecrawl SDK integration for advanced web scraping
- `POST /research/topic` - Deep research on topics from multiple web sources
- `POST /research/competitor` - Comprehensive competitor web intelligence
- `POST /research/trends` - Multi-source trend aggregation
- `POST /research/audience` - Audience discourse from forums, Reddit, Quora
- `POST /research/deep-research` - 10+ source comprehensive briefing
- `GET /research/sources` - List available scraping sources and status

#### Enhanced Intelligence Engines with Web Scraping
- `CompetitorEngine.enhanced_competitor_analysis()` - Web presence scraping
- `GapDetector.enhanced_gap_detection()` - Reddit, Quora, forum gap detection
- `AudienceEngine.enhanced_audience_analysis()` - Community discussion scraping
- `TrendEngine` - Real-time trend detection with multi-source scraping

#### Web Scraping Utilities
- `RateLimiter` - Per-domain rate limiting for respectful scraping
- `CacheManager` - TTL-based caching for scraped data
- `ScrapedDataCache` - Specialized cache for research data
- `SourceValidator` - Content quality and spam detection

#### Frontend Research Dashboard
- Research page at `(dashboard)/research/page.tsx`
- Deep research with topic/niche input
- Source aggregator showing scraped data
- AI synthesis panel
- Platform-specific trend detection

### Planned Features
- [ ] Rate limiting enforcement
- [ ] Webhook support for async notifications
- [ ] Batch script generation
- [ ] Advanced analytics endpoints
- [ ] Team collaboration features
- [ ] Custom competitor tracking
- [ ] Export functionality (CSV, PDF)
- [ ] Mobile app API

### Deprecations
None at this time.

---

## Versioning Policy

The CreatorIQ API follows semantic versioning:
- **Major version** (1.0.0): Breaking changes
- **Minor version** (1.1.0): New features, backward compatible
- **Patch version** (1.0.1): Bug fixes, backward compatible

When a major version is released, older versions will be supported for at least 12 months.

## API Support

For API support, contact:
- Email: api-support@creatoriq.io
- Documentation: https://docs.creatoriq.io
- Status Page: https://status.creatoriq.io
