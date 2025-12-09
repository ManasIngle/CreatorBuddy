"""
Rate Limiting Middleware for CreatorIQ Platform
Provides endpoint rate limiting with Redis backend for distributed systems.
"""

import time
import logging
from typing import Dict, Tuple
from collections import deque
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse
from app.config import settings

logger = logging.getLogger(__name__)


class RateLimitEntry:
    """Entry in the rate limit store."""
    __slots__ = ('count', 'window_start')
    
    def __init__(self, count: int = 0, window_start: float = 0):
        self.count = count
        self.window_start = window_start


class InMemoryRateLimiter:
    """
    Simple in-memory rate limiter using sliding window.
    
    For production, use Redis-based rate limiting for distributed deployment.
    """
    
    def __init__(self, requests: int, window_seconds: int):
        self.requests = requests
        self.window_seconds = window_seconds
        self._store: Dict[str, RateLimitEntry] = {}
    
    def is_allowed(self, key: str) -> Tuple[bool, Dict[str, any]]:
        """
        Check if request is allowed under rate limit.
        
        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        now = time.time()
        
        if key not in self._store:
            self._store[key] = RateLimitEntry(1, now)
            return True, self._get_info(key, now)
        
        entry = self._store[key]
        
        # Reset if window has passed
        if now - entry.window_start >= self.window_seconds:
            entry.count = 1
            entry.window_start = now
            return True, self._get_info(key, now)
        
        # Increment count
        entry.count += 1
        
        # Check if over limit
        if entry.count > self.requests:
            remaining = 0
            reset_time = entry.window_start + self.window_seconds
            return False, {
                "limit": self.requests,
                "remaining": remaining,
                "reset": int(reset_time)
            }
        
        return True, self._get_info(key, now)
    
    def _get_info(self, key: str, now: float) -> Dict[str, any]:
        """Get rate limit info for key."""
        entry = self._store[key]
        remaining = max(0, self.requests - entry.count)
        reset_time = entry.window_start + self.window_seconds
        
        return {
            "limit": self.requests,
            "remaining": remaining,
            "reset": int(reset_time)
        }
    
    def cleanup(self):
        """Remove expired entries to prevent memory growth."""
        now = time.time()
        expired = [
            key for key, entry in self._store.items()
            if now - entry.window_start >= self.window_seconds
        ]
        for key in expired:
            del self._store[key]


# Default rate limiters for different endpoint types
DEFAULT_RATE_LIMITS = {
    "default": InMemoryRateLimiter(100, 60),      # 100/minute
    "auth": InMemoryRateLimiter(20, 60),          # 20/minute for auth endpoints
    "write": InMemoryRateLimiter(30, 60),         # 30/minute for writes
    "script": InMemoryRateLimiter(10, 60),        # 10/minute for script generation (expensive)
    "analysis": InMemoryRateLimiter(5, 60),       # 5/minute for heavy analysis
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware for FastAPI.
    
    Applies different rate limits based on endpoint category.
    """
    
    def __init__(self, app, limit_type: str = "default"):
        super().__init__(app)
        self.limiter = DEFAULT_RATE_LIMITS.get(limit_type, DEFAULT_RATE_LIMITS["default"])
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with rate limiting."""
        # Skip rate limiting for health endpoints
        if request.url.path in ["/health", "/health/live", "/health/ready"]:
            return await call_next(request)
        
        # Determine rate limit key
        client_ip = self._get_client_ip(request)
        key = f"{client_ip}:{request.url.path}"
        
        # Check rate limit
        allowed, info = self.limiter.is_allowed(key)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for {key}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": 429,
                        "message": "Rate limit exceeded. Please try again later.",
                        "retry_after": info["reset"] - int(time.time())
                    }
                },
                headers={
                    "X-RateLimit-Limit": str(info["limit"]),
                    "X-RateLimit-Remaining": str(info["remaining"]),
                    "X-RateLimit-Reset": str(info["reset"]),
                    "Retry-After": str(info["reset"] - int(time.time()))
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(info["reset"])
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request, considering proxies."""
        # Check X-Forwarded-For header first
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            # Get first IP in chain
            return forwarded.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"


def get_rate_limit_middleware(limit_type: str = "default") -> RateLimitMiddleware:
    """Factory function to create rate limit middleware."""
    def create_middleware(app):
        return RateLimitMiddleware(app, limit_type)
    return create_middleware


# Pre-configured middleware instances for different routes
auth_rate_limit = get_rate_limit_middleware("auth")
write_rate_limit = get_rate_limit_middleware("write")
script_rate_limit = get_rate_limit_middleware("script")
analysis_rate_limit = get_rate_limit_middleware("analysis")