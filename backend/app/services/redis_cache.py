"""
Redis Cache Service for CreatorIQ Platform
Provides distributed caching with TTL, cache-aside pattern, and automatic invalidation.
"""

import json
import hashlib
import logging
from typing import Optional, Any, Dict, List, Callable
from datetime import timedelta
from functools import wraps
import redis.asyncio as redis
from redis.asyncio.client import Redis
from redis.exceptions import RedisError

from app.config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    """
    Async Redis cache with connection pooling and automatic serialization.
    Implements cache-aside pattern with TTL support.
    """
    
    _instance: Optional['RedisCache'] = None
    _redis: Optional[Redis] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def initialize(self):
        """Initialize Redis connection pool."""
        if self._redis is None:
            try:
                self._redis = redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=50,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                    retry_on_timeout=True
                )
                # Test connection
                await self._redis.ping()
                logger.info("Redis cache initialized successfully")
            except RedisError as e:
                logger.error(f"Failed to initialize Redis: {e}")
                self._redis = None
    
    async def close(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None
    
    @property
    def client(self) -> Optional[Redis]:
        """Get Redis client instance."""
        return self._redis
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from prefix and arguments."""
        key_data = f"{prefix}:{args}:{json.dumps(kwargs, sort_keys=True)}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:16]
        return f"{prefix}:{key_hash}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self._redis:
            return None
        try:
            value = await self._redis.get(key)
            if value:
                return json.loads(value)
            return None
        except RedisError as e:
            logger.warning(f"Redis GET failed for {key}: {e}")
            return None
        except json.JSONDecodeError:
            return value
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = 3600,
        nx: bool = False
    ) -> bool:
        """Set value in cache with TTL (in seconds)."""
        if not self._redis:
            return False
        try:
            serialized = json.dumps(value)
            if nx:
                return await self._redis.setnx(key, serialized)
            await self._redis.setex(key, ttl, serialized)
            return True
        except RedisError as e:
            logger.warning(f"Redis SET failed for {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self._redis:
            return False
        try:
            await self._redis.delete(key)
            return True
        except RedisError as e:
            logger.warning(f"Redis DELETE failed for {key}: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not self._redis:
            return 0
        try:
            keys = []
            async for key in self._redis.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                return await self._redis.delete(*keys)
            return 0
        except RedisError as e:
            logger.warning(f"Redis DELETE pattern failed for {pattern}: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self._redis:
            return False
        try:
            return await self._redis.exists(key) > 0
        except RedisError as e:
            logger.warning(f"Redis EXISTS failed for {key}: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter in cache."""
        if not self._redis:
            return None
        try:
            return await self._redis.incrby(key, amount)
        except RedisError as e:
            logger.warning(f"Redis INCR failed for {key}: {e}")
            return None
    
    async def get_ttl(self, key: str) -> int:
        """Get remaining TTL for key."""
        if not self._redis:
            return -1
        try:
            return await self._redis.ttl(key)
        except RedisError:
            return -1


# Cache key prefixes for different data types
class CacheKeys:
    """Cache key prefix constants."""
    CHANNEL = "channel"
    COMPETITOR = "competitor"
    VIDEO = "video"
    TRENDS = "trends"
    SCRIPT = "script"
    HOOK = "hook"
    GAP = "gap"
    AUDIENCE = "audience"
    YOUTUBE_STATS = "yt:stats"
    YOUTUBE_CHANNEL = "yt:channel"


# Specialized cache decorators and helpers
class CachedOperation:
    """
    Decorator for caching expensive operations.
    Implements cache-aside pattern with automatic serialization.
    """
    
    def __init__(
        self,
        prefix: str,
        ttl: int = 3600,
        key_builder: Optional[Callable] = None
    ):
        self.prefix = prefix
        self.ttl = ttl
        self.key_builder = key_builder
    
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = RedisCache()
            await cache.initialize()
            
            # Build cache key
            if self.key_builder:
                cache_key = self.key_builder(*args, **kwargs)
            else:
                cache_key = cache._generate_key(self.prefix, *args, **kwargs)
            
            # Try cache first
            cached = await cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached
            
            # Execute function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Store in cache
            await cache.set(cache_key, result, self.ttl)
            logger.debug(f"Cache miss for {cache_key}, stored result")
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, skip caching (or use sync Redis client)
            return func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return wrapper
        return sync_wrapper


# Cache invalidation helpers
class CacheInvalidator:
    """Helper class for cache invalidation strategies."""
    
    @staticmethod
    async def invalidate_channel(channel_id: str):
        """Invalidate all cache entries related to a channel."""
        cache = RedisCache()
        await cache.initialize()
        patterns = [
            f"{CacheKeys.CHANNEL}:{channel_id}*",
            f"{CacheKeys.VIDEO}:channel:{channel_id}*",
            f"{CacheKeys.COMPETITOR}:channel:{channel_id}*",
        ]
        for pattern in patterns:
            await cache.delete_pattern(pattern)
        logger.info(f"Invalidated cache for channel {channel_id}")
    
    @staticmethod
    async def invalidate_user(user_id: str):
        """Invalidate all cache entries for a user."""
        cache = RedisCache()
        await cache.initialize()
        patterns = [
            f"{CacheKeys.CHANNEL}:user:{user_id}*",
            f"{CacheKeys.SCRIPT}:user:{user_id}*",
        ]
        for pattern in patterns:
            await cache.delete_pattern(pattern)
        logger.info(f"Invalidated cache for user {user_id}")
    
    @staticmethod
    async def invalidate_youtube_data(channel_id: str):
        """Invalidate YouTube API cached data for a channel."""
        cache = RedisCache()
        await cache.initialize()
        patterns = [
            f"{CacheKeys.YOUTUBE_STATS}:{channel_id}*",
            f"{CacheKeys.YOUTUBE_CHANNEL}:{channel_id}*",
        ]
        for pattern in patterns:
            await cache.delete_pattern(pattern)
        logger.info(f"Invalidated YouTube cache for channel {channel_id}")


# Global cache instance
redis_cache = RedisCache()


# Import asyncio for decorator
import asyncio
from typing import Callable, Optional