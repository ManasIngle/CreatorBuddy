# Docs Directory

This directory contains supplementary documentation for the CreatorIQ platform.

## 📄 Documentation Files

| File | Description |
|------|-------------|
| **[CHANGELOG.md](CHANGELOG.md)** | API changelog documenting all endpoint additions, changes, and deprecations |
| **[CONTRIBUTING.md](CONTRIBUTING.md)** | Contribution guidelines including development setup, coding standards, PR process |
| **[COST_ANALYSIS.md](COST_ANALYSIS.md)** | Cost analysis for LLM usage across the platform |
| **[DATABASE_INDEXES.md](DATABASE_INDEXES.md)** | Database index strategy and query optimization |
| **[EFFICIENCY_OPTIMIZATIONS.md](EFFICIENCY_OPTIMIZATIONS.md)** | Performance optimizations and best practices |
| **[OPENROUTER.md](OPENROUTER.md)** | OpenRouter API integration details and model routing |

## 📊 Documentation Categories

### API Documentation
- **CHANGELOG.md** - All API endpoints, request/response schemas, rate limits, error formats
- **OPENROUTER.md** - LLM integration details, model routing, cost optimization

### Development Guides
- **CONTRIBUTING.md** - Setup instructions, architecture principles, PR guidelines
- **EFFICIENCY_OPTIMIZATIONS.md** - Caching strategies, connection pooling, bulk operations

### Infrastructure
- **DATABASE_INDEXES.md** - Index strategy for PostgreSQL + pgvector
- **COST_ANALYSIS.md** - Token budgets, usage tracking, cost management

## 🔗 Related Documentation

- **[Root README.md](../README.md)** - Main project documentation
- **[backend/app/models/README.md](../backend/app/models/README.md)** - Database model documentation
- **[backend/app/routers/README.md](../backend/app/routers/README.md)** - API route documentation
- **[backend/app/intelligence/README.md](../backend/app/intelligence/README.md)** - AI engine documentation

## 📝 Adding New Documentation

When adding new documentation files to this directory:

1. Follow the naming convention: `UPPERCASE_WORDS.md`
2. Add a link in this README's table
3. Update the documentation index in root `README.md`

## 🔍 Finding Documentation

### By Topic

| Topic | File |
|-------|------|
| API Changes | CHANGELOG.md |
| Contributing | CONTRIBUTING.md |
| LLM Costs | COST_ANALYSIS.md |
| Database | DATABASE_INDEXES.md |
| Performance | EFFICIENCY_OPTIMIZATIONS.md |
| AI Integration | OPENROUTER.md |

### By Stack Layer

| Layer | Documentation Location |
|-------|----------------------|
| Frontend | `/frontend/` directories, each with README.md |
| Backend | `/backend/app/` subdirectories, each with README.md |
| Project-wide | Root `README.md` and `/docs/` directory |

## 📚 Documentation Style Guide

### Markdown Headers
- Use `#` for page title
- Use `##` for major sections
- Use `###` for subsections
- Keep heading hierarchy consistent

### Code Blocks
- Use ` ```language ``` ` for fenced code blocks
- Include language for syntax highlighting
- Provide context for code examples

### Tables
- Use tables for structured information
- Include all columns in header
- Use pipes `|` for column dividers

### Links
- Use relative links for internal documentation
- Use absolute URLs for external resources
- Include descriptive link text

## 🚀 Quick Reference

### Key Environment Variables

**Backend (backend/.env)**
```
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
OPENROUTER_API_KEY=sk-or-...
YOUTUBE_API_KEY=AIza...
SECRET_KEY=...
```

**Frontend (frontend/.env.local)**
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

### Common Commands

```bash
# Backend
cd backend
uvicorn app.main:app --reload  # Development
pytest  # Tests
alembic upgrade head  # Migrations

# Frontend
cd frontend
npm run dev  # Development
npm run lint  # Linting
npm run type-check  # Type checking

# Docker
docker-compose up -d  # Start all services
docker-compose logs -f  # View logs
```

### API Base URL

Development: `http://localhost:8000/api/v1`
Production: Configured via `NEXT_PUBLIC_API_URL` environment variable