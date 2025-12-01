# CreatorIQ Documentation

Welcome to the CreatorIQ platform documentation. This index provides a comprehensive overview of all module documentation to help you understand and work on any part of the codebase.

## 📚 Module Documentation Index

### Backend Modules

| Module | Documentation | Description |
|--------|--------------|-------------|
| **Models** | [`backend/app/models/README.md`](backend/app/models/README.md) | SQLAlchemy ORM models for User, Channel, Video, Competitor, ContentGap, Script, Hook, Trend, AnalysisJob |
| **Services** | [`backend/app/services/README.md`](backend/app/services/README.md) | External service wrappers: OpenRouter, YouTube, Redis, OpenAI, Embedding, Whisper, Scraper |
| **Intelligence** | [`backend/app/intelligence/README.md`](backend/app/intelligence/README.md) | AI engines: CreatorAnalyzer, CompetitorEngine, GapDetector, ScriptGenerator, HookEngine, ThumbnailEngine, AudienceEngine, TrendEngine, RetentionEngine, ViralEngine |
| **Routers** | [`backend/app/routers/README.md`](backend/app/routers/README.md) | FastAPI route handlers: Auth, Channels, Competitors, Gaps, Hooks, Scripts, Audience, Research, Thumbnails, Trends |
| **Prompts** | [`backend/app/prompts/README.md`](backend/app/prompts/README.md) | LLM prompt templates for all AI engines |
| **Tasks** | [`backend/app/tasks/README.md`](backend/app/tasks/README.md) | Celery background tasks: channel_tasks, competitor_tasks, trend_tasks |
| **Utils** | [`backend/app/utils/README.md`](backend/app/utils/README.md) | Utilities: Auth, RateLimiter, Resilience, CacheManager, TextUtils, Base, SourceValidator |

### Frontend Modules

| Module | Documentation | Description |
|--------|--------------|-------------|
| **App** | [`frontend/app/README.md`](frontend/app/README.md) | Next.js 14 App Router pages and layouts |
| **Components** | [`frontend/components/README.md`](frontend/components/README.md) | React components: UI primitives, Charts, Intelligence displays, Layout |
| **Hooks** | [`frontend/hooks/README.md`](frontend/hooks/README.md) | Custom React hooks with TanStack Query |
| **Lib** | [`frontend/lib/README.md`](frontend/lib/README.md) | API client, Auth (NextAuth), Utilities |

## 🎯 Quick Links

### Getting Started
- **[README.md](README.md)** - Main project documentation with architecture, setup, and features
- **[IMPLEMENTATION.md](IMPLEMENTATION.md)** - Complete implementation guide (4046 lines)

### Development Guides
- **[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)** - Contribution guidelines, coding standards, PR process
- **[docs/CHANGELOG.md](docs/CHANGELOG.md)** - API changelog and version history

### Configuration
- **[backend/.env.example](backend/.env.example)** - Backend environment variables template
- **[frontend/.env.example](frontend/.env.example)** - Frontend environment variables template

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        USER BROWSER                          │
│            Next.js 14 (Vercel CDN)                           │
│    React SPA + App Router + TanStack Query + Zustand        │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTPS REST
┌─────────────────────────▼───────────────────────────────────┐
│                  FastAPI (Railway)                            │
│  /api/v1/* — All business logic                              │
│  Auth | YouTube | AI Pipelines | Background Jobs             │
└────────────┬─────────────────────────────┬───────────────────┘
             │                             │
┌────────────▼──────────┐   ┌──────────────▼──────────────────┐
│    PostgreSQL         │   │         Celery Workers          │
│    + pgvector         │   │   (background AI processing)   │
│    (Railway)          │   │   Redis broker (Railway)       │
└───────────────────────┘   └────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
┌───────▼───────┐  ┌───────────▼──────┐  ┌────────────▼─────┐
│ YouTube Data  │  │  OpenRouter API │  │  Whisper API      │
│ API v3        │  │  (unified LLM)  │  │  Transcription   │
└───────────────┘  └─────────────────┘  └──────────────────┘
```

## 📊 Key Technologies

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Next.js 14 | React framework with App Router |
| **Frontend** | TanStack Query | Server state management, caching |
| **Frontend** | Zustand | Client state management |
| **Frontend** | Tailwind CSS | Utility-first styling |
| **Backend** | FastAPI | Async Python API framework |
| **Backend** | SQLAlchemy | ORM with async support |
| **Database** | PostgreSQL | Primary database |
| **Database** | pgvector | Vector similarity search |
| **AI** | OpenRouter | Unified LLM API (multi-provider) |
| **Background** | Celery | Distributed task queue |
| **Cache** | Redis | Caching and message broker |

## 🔧 Development Workflow

### Backend Development

```bash
# Start backend server
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Run tests
pytest

# Format code
black .
flake8 .
```

### Frontend Development

```bash
# Start frontend dev server
cd frontend
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint
```

## 📁 Directory Structure

```
Content-Buddy-Saas/
├── backend/
│   └── app/
│       ├── models/          # Database models
│       ├── schemas/         # Pydantic schemas
│       ├── routers/         # API routes
│       ├── services/        # External integrations
│       ├── intelligence/    # AI engines
│       ├── prompts/         # LLM prompts
│       ├── tasks/           # Celery tasks
│       └── utils/           # Utilities
├── frontend/
│   ├── app/                # Next.js pages
│   │   ├── (auth)/        # Auth pages
│   │   └── (dashboard)/   # Dashboard pages
│   ├── components/         # React components
│   │   ├── ui/            # Design system
│   │   ├── charts/        # Visualizations
│   │   ├── intelligence/  # Feature components
│   │   └── layout/        # Layout components
│   ├── hooks/             # Custom hooks
│   ├── lib/               # Utilities
│   ├── store/             # Zustand store
│   └── types/             # TypeScript types
├── docs/                  # Documentation
├── docker-compose.yml     # Docker setup
└── README.md             # This file
```

## 🚀 Feature Overview

### Completed Features

1. **Authentication** - Email/password and Google OAuth
2. **Channel Management** - Connect and analyze YouTube channels
3. **Competitor Intelligence** - Track and analyze competitor channels
4. **Content Gap Detection** - AI-powered topic opportunity identification
5. **Script Generation** - Complete video scripts with hooks, titles, CTAs
6. **Hook Intelligence** - Viral hook pattern analysis and generation
7. **Thumbnail Intelligence** - CTR analysis and concept recommendations
8. **Trend Radar** - Real-time trend detection and tracking
9. **Audience Insights** - Audience psychology analysis

### Coming Soon

- Rate limiting enforcement
- Webhook support for async notifications
- Batch script generation
- Team collaboration features
- Export functionality (CSV, PDF)
- Mobile app API

## 📖 Reading Guide

**For LLM working on a specific module:**
1. Start with the module's README.md for a complete overview
2. Reference individual file documentation for specific implementations
3. Check IMPLEMENTATION.md for architectural context

**For understanding the full system:**
1. Start with README.md (this file)
2. Read the architecture section in main README.md
3. Explore each module's README for depth

## 🆘 Support

- **GitHub Issues**: Bug reports and feature requests
- **Email**: support@creatoriq.io
- **Documentation**: https://docs.creatoriq.io