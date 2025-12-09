# Utils Module

This module contains backend utility functions for authentication, rate limiting, resilience patterns, caching, and data validation.

## Overview

Utilities provide cross-cutting concerns that support the entire application:
- **auth_utils**: JWT authentication and password hashing
- **rate_limiter**: Endpoint rate limiting middleware
- **resilience**: Circuit breaker, bulkhead, and retry patterns
- **cache_manager**: Scraped data caching
- **text_utils**: Text manipulation helpers
- **base**: Base router, validators, metrics
- **source_validator**: Content source validation

## File Structure

```
backend/app/utils/
├── __init__.py              # Package marker
├── auth_utils.py            # JWT authentication
├── rate_limiter.py          # Rate limiting middleware
├── resilience.py            # Circuit breaker, bulkhead, retry
├── cache_manager.py         # Scraped data cache
├── text_utils.py            # Text manipulation
├── base.py                  # Base utilities (ETags, pagination, metrics)
└── source_validator.py      # Content source validation
```

---

## auth_utils.py

**File:** [`auth_utils.py`](backend/app/utils/auth_utils.py)

### Functions

#### `verify_password(plain: str, hashed: str) -> bool`

Verifies a password against its hash.

**Parameters:**
- `plain` (str): Plaintext password
- `hashed` (str): Bcrypt hash

**Returns:** True if password matches

---

#### `hash_password(password: str) -> str`

Hashes a password using bcrypt.

**Parameters:**
- `password` (str): Plaintext password

**Returns:** Bcrypt hash

---

#### `create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str`

Creates a JWT access token.

**Parameters:**
- `data` (dict): Payload data (must include `"sub"` with user ID)
- `expires_delta` (Optional[timedelta]): Token expiration time

**Returns:** JWT token string

**Settings Used:**
- `SECRET_KEY`: Signing key from config
- `ALGORITHM`: JWT algorithm (default HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Default expiration

---

#### `get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User`

FastAPI dependency for getting current authenticated user.

**Parameters:**
- `token` (str): JWT token from Authorization header
- `db` (Session): Database session

**Returns:** `User` object

**Raises:** HTTPException 401 if token invalid or user not found

**Usage:**
```python
@router.get("/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    return {"user_id": current_user.id}
```

---

## rate_limiter.py

**File:** [`rate_limiter.py`](backend/app/utils/rate_limiter.py)

### Class: `InMemoryRateLimiter`

Simple sliding window rate limiter.

#### Constructor: `__init__(requests: int, window_seconds: int)`

**Parameters:**
- `requests` (int): Max requests allowed
- `window_seconds` (int): Time window

---

#### `is_allowed(key: str) -> Tuple[bool, Dict]`

Checks if request is allowed.

**Parameters:**
- `key` (str): Rate limit key (usually IP + path)

**Returns:** Tuple of (is_allowed, rate_limit_info)

**Rate Limit Info:**
```python
{
    "limit": 100,
    "remaining": 95,
    "reset": 1705312800  # Unix timestamp
}
```

---

### Class: `RateLimitMiddleware`

FastAPI middleware for automatic rate limiting.

#### Usage

```python
from fastapi import FastAPI
from app.utils.rate_limiter import RateLimitMiddleware

app = FastAPI()
app.add_middleware(RateLimitMiddleware, limit_type="default")
```

---

### Default Rate Limits

| Type | Requests | Window | Use Case |
|------|----------|--------|----------|
| `default` | 100 | 60s | General reads |
| `auth` | 20 | 60s | Login/register |
| `write` | 30 | 60s | Create/update |
| `script` | 10 | 60s | Script generation |
| `analysis` | 5 | 60s | Heavy analysis |

---

### Rate Limit Response Headers

- `X-RateLimit-Limit`: Max requests
- `X-RateLimit-Remaining`: Requests left
- `X-RateLimit-Reset`: Unix timestamp of reset
- `Retry-After`: Seconds to wait (on 429)

---

## resilience.py

**File:** [`resilience.py`](backend/app/utils/resilience.py)

### Class: `CircuitBreaker`

Circuit breaker implementation for external API calls.

#### States

| State | Behavior |
|-------|----------|
| `CLOSED` | Normal operation, requests pass |
| `OPEN` | Fail fast, reject all requests |
| `HALF_OPEN` | Test recovery, limited requests |

#### Constructor Parameters

```python
CircuitBreaker(
    name: str,
    failure_threshold: int = 5,      # Failures before opening
    recovery_timeout: int = 60,     # Seconds before testing recovery
    half_open_max_calls: int = 3,   # Calls allowed in half-open
    excluded_exceptions: tuple = ()  # Exceptions that don't count
)
```

#### `async call(func, *args, **kwargs) -> T`

Execute function through circuit breaker.

**Raises:**
- `CircuitBreakerOpen`: When circuit is open
- Original exception: On function failure

---

### Pre-configured Circuit Breakers

```python
YOUTUBE_CB = CircuitBreakerManager.get_breaker(
    "youtube_api",
    failure_threshold=5,
    recovery_timeout=60
)

OPENAI_CB = CircuitBreakerManager.get_breaker(
    "openai_api",
    failure_threshold=3,
    recovery_timeout=30
)

SCRAPER_CB = CircuitBreakerManager.get_breaker(
    "web_scraper",
    failure_threshold=10,
    recovery_timeout=120
)
```

---

### Class: `RateLimiter`

Token bucket rate limiter for API calls.

#### `async acquire(timeout: Optional[float] = None) -> bool`

Acquire a token, waiting if necessary.

**Parameters:**
- `timeout` (float, optional): Max seconds to wait

**Returns:** True if acquired, False if timeout

---

### Class: `Bulkhead`

Bulkhead pattern for resource isolation.

#### `async __aenter__()`

Enter bulkhead context.

**Raises:** `BulkheadFull` if queue is full

---

### Class: `RetryWithBackoff`

Configurable retry with exponential backoff.

#### Constructor Parameters

```python
RetryWithBackoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    jitter: bool = True
)
```

**Usage:**
```python
@RetryWithBackoff(max_attempts=3, base_delay=2.0)
async def call_api():
    ...
```

---

## cache_manager.py

**File:** [`cache_manager.py`](backend/app/utils/cache_manager.py)

### Class: `ScrapedDataCache`

Caches scraped web data with TTL.

**Usage:**
```python
from app.utils.cache_manager import scraped_data_cache

# Cache trends
scraped_data_cache.cache_trends("niche", trends_data)

# Get cached trends
trends = scraped_data_cache.get_trends("niche")
```

---

## text_utils.py

**File:** [`text_utils.py`](backend/app/utils/text_utils.py)

### Functions

#### `truncate_text(text: str, max_length: int, suffix: str = "...") -> str`

Truncates text to max length.

---

#### `clean_text(text: str) -> str`

Removes extra whitespace and cleans text.

---

#### `extract_keywords(text: str, count: int = 10) -> List[str]`

Extracts keywords from text.

---

#### `count_words(text: str) -> int`

Counts words in text.

---

#### `slugify(text: str) -> str`

Converts text to URL-safe slug.

---

## base.py

**File:** [`base.py`](backend/app/utils/base.py)

### Classes

#### `BaseRouter`

Base router with pagination and response helpers.

**Methods:**
- `paginate_query(query, page, page_size)`: Applies pagination
- `build_pagination_response(items, total, page, page_size)`: Builds paginated response

---

#### `ETags`

ETag generation and comparison for cache validation.

**Methods:**
- `generate(data)`: Generate ETag from data
- `match(etag, if_none_match)`: Check if ETag matches

---

#### `MetricsCollector`

Request/operation metrics collection.

**Methods:**
- `record_timing(operation, duration_ms)`: Record timing
- `increment_counter(name, count)`: Increment counter

---

#### `ValidationError`

Custom validation error.

---

#### `InputValidator`

Input validation utilities.

**Methods:**
- `validate_uuid(value, field_name)`: Validate UUID format
- `validate_youtube_channel_id(value)`: Validate YouTube channel ID
- `validate_email(value)`: Validate email format

---

## source_validator.py

**File:** [`source_validator.py`](backend/app/utils/source_validator.py)

### Functions

#### `validate_source_url(url: str) -> bool`

Validates if URL is an allowed scraping source.

---

#### `get_source_type(url: str) -> str`

Determines source type from URL.

**Returns:** reddit, quora, youtube, google, wikipedia, etc.

---

## Usage Examples

### Authentication

```python
from app.utils.auth_utils import get_current_user
from app.models.user import User

@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "plan": current_user.plan
    }
```

### Rate Limiting

```python
from app.utils.rate_limiter import get_rate_limit_middleware

app.add_middleware(
    get_rate_limit_middleware("script"),
    limit_type="script"
)
```

### Circuit Breaker

```python
from app.utils.resilience import YOUTUBE_CB

async def fetch_with_circuit_breaker():
    return await YOUTUBE_CB.call(youtube_service.fetch_channel_details, channel_id)
```

### Validation

```python
from app.utils.base import InputValidator, ValidationError

try:
    validated_id = InputValidator.validate_uuid(channel_id, "channel_id")
except ValidationError as e:
    raise HTTPException(status_code=400, detail=e.message)
```

---

## Configuration

### Environment Variables

```bash
# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rate Limiting
RATE_LIMIT_ENABLED=true
```

---

## Testing

```python
from unittest.mock import patch
from app.utils.auth_utils import verify_password, hash_password

def test_password_hashing():
    password = "securepassword123"
    hashed = hash_password(password)
    
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

def test_rate_limiter():
    from app.utils.rate_limiter import InMemoryRateLimiter
    
    limiter = InMemoryRateLimiter(requests=5, window_seconds=60)
    
    # First 5 should be allowed
    for i in range(5):
        allowed, _ = limiter.is_allowed("test_key")
        assert allowed
    
    # 6th should be denied
    allowed, info = limiter.is_allowed("test_key")
    assert not allowed
    assert info["remaining"] == 0