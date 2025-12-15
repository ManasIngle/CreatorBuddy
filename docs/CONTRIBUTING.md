# Contributing to CreatorIQ

Thank you for your interest in contributing to CreatorIQ! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a welcoming and respectful environment for all contributors and users.

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ with pgvector extension
- Redis (for Celery background tasks)

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Content-Buddy-Saas.git
   cd Content-Buddy-Saas
   ```

3. **Set up the backend**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env  # Edit .env with your credentials
   ```

4. **Set up the frontend**:
   ```bash
   cd frontend
   npm install
   cp .env.example .env.local  # Edit .env.local with your credentials
   ```

5. **Run database migrations**:
   ```bash
   cd backend
   alembic upgrade head
   ```

6. **Start development servers**:
   ```bash
   # Terminal 1: Backend
   cd backend
   uvicorn app.main:app --reload --port 8000

   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

## Project Structure

```
creatoriq/
├── backend/
│   ├── app/
│   │   ├── intelligence/    # AI engines (don't put business logic in routers!)
│   │   ├── prompts/        # All LLM prompts as constants
│   │   ├── routers/        # API route handlers (thin, only HTTP concerns)
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # External service wrappers (YouTube, OpenAI, etc.)
│   │   ├── tasks/          # Celery background tasks
│   │   └── utils/          # Utility functions
│   ├── alembic/           # Database migrations
│   └── openapi.yaml       # OpenAPI specification
│
├── frontend/
│   ├── app/               # Next.js 14 App Router pages
│   ├── components/       # React components
│   │   ├── ui/           # Base design system components
│   │   ├── charts/       # Data visualization components
│   │   └── intelligence/ # Feature-specific smart components
│   ├── hooks/            # Custom React hooks
│   ├── lib/              # API client and utilities
│   └── store/            # Zustand state management
│
└── docs/                 # Documentation
```

## Architecture Principles

### Backend

1. **One AI call = one purpose**
   - Never combine multiple AI tasks in one prompt
   - Each engine should do one thing well

2. **All AI logic lives in `/intelligence/`**
   - Route handlers should only handle HTTP concerns
   - Delegate to engine classes for business logic

3. **All prompts live in `/prompts/`**
   - Store prompts as Python string constants
   - Use `.format()` for variable substitution

4. **Frontend never calls LLM providers directly**
   - Always go through the FastAPI backend
   - Backend handles API key security

5. **Use OpenRouter for all LLM calls**
   - Import from `app.services.openrouter_service`
   - Use model routing for cost optimization (simple/medium/complex)
   - Check `MODEL_COSTS` in openrouter_service.py for cost per token

6. **Background jobs must be idempotent**
   - Safe to retry on failure
   - Use idempotency keys where applicable

### Model Routing and Cost Optimization

OpenRouter provides access to multiple LLM providers. Use the complexity parameter for cost-based routing:

```python
from app.services.openrouter_service import call_openai

# Simple task - use cheapest model (Llama 3)
result = call_openai(system, user, complexity="simple")

# Medium task - use default model (GPT-4o-mini)
result = call_openai(system, user, complexity="medium")

# Complex task - use premium model (GPT-4o)
result = call_openai(system, user, complexity="complex")
```

**When adding new AI features, consider:**
- What complexity level does this task need?
- Can it use a cheaper model without quality loss?
- What's the expected request volume?
- Calculate estimated costs: `requests × tokens × cost_per_token`

**Cost-conscious development:**
- Use `simple` for basic transformations, classifications, formatting
- Use `medium` for standard analysis, summaries, recommendations
- Use `complex` only for nuanced reasoning, creative tasks, multi-step analysis

### Frontend

1. **Use Server Components by default**
   - Only add "use client" when interactivity is needed
   - Keep client boundary as small as possible

2. **Custom hooks for data fetching**
   - Use React Query or similar for server state
   - Keep components presentation-focused

3. **Design system components in `/ui/`**
   - Base components should be reusable and flexible
   - Feature components can be more specific

## Pull Request Process

### Before Submitting

1. **Run tests**:
   ```bash
   # Backend
   cd backend
   pytest

   # Frontend
   cd frontend
   npm run lint
   npm run type-check
   ```

2. **Follow the coding style**:
   - Backend: Black formatter, isort for imports
   - Frontend: Prettier, ESLint

3. **Update documentation**:
   - Add docstrings to new functions and classes
   - Update README if adding new features
   - Add API endpoints to CHANGELOG.md

### PR Guidelines

1. **Title**: Use clear, descriptive titles
   - Good: "Add competitor gap detection endpoint"
   - Bad: "Fix bug" or "Updates"

2. **Description**: Explain what and why
   - Describe the changes made
   - Link to related issues
   - Include screenshots for UI changes

3. **Size**: Keep PRs focused
   - One feature or fix per PR
   - Large changes should be split into multiple PRs

### Review Process

1. Maintainers will review within 48 hours
2. Address feedback constructively
3. Once approved, a maintainer will merge

## Commit Message Format

Use conventional commits:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting (no code change)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance

Example:
```
feat(channels): add re-analysis endpoint

Added POST /channels/{id}/re-analyze to trigger fresh
analysis of channel content and statistics.

Closes #123
```

## Reporting Issues

### Bug Reports

Include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python/Node version, etc.)
- Error messages and stack traces

### Feature Requests

Include:
- Clear description of the feature
- Use case / motivation
- Possible alternatives considered
- Any mockups or examples helpful

## Development Workflow

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation
- `refactor/description` - Code improvements

### Release Process

1. Update version in relevant files
2. Update CHANGELOG.md
3. Create git tag
4. Build and push Docker images
5. Deploy to staging
6. Run integration tests
7. Deploy to production

## Questions?

- **GitHub Issues**: For bug reports and feature requests
- **Discussions**: For questions and general discussion
- **Email**: support@creatoriq.io

## License

By contributing to CreatorIQ, you agree that your contributions will be licensed under the project's proprietary license.