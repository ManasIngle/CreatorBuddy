"""
Cache Manager for Scraped Data
Caches scraped content with TTL to reduce redundant requests.
Supports Redis-backed distributed caching with in-memory fallback.
"""

import time
import hashlib
import json
import logging
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
import redis
from app.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Cache manager backed by Redis when available, with in-memory fallback.
    Reduces redundant scraping requests and improves performance.
    """
    
    def __init__(self, default_ttl: int = 3600, namespace: str = "cache"):
        self._cache: Dict[str, dict] = {}
        self.default_ttl = default_ttl
        self.max_cache_size = 1000
        self.namespace = namespace
        self._redis = None
        self._redis_failed = False
    
    def _get_redis(self) -> Optional[redis.Redis]:
        """Lazy initializer for synchronous Redis client with fallback."""
        if self._redis_failed:
            return None
        if self._redis is None:
            try:
                self._redis = redis.Redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_timeout=2,
                    socket_connect_timeout=2
                )
                self._redis.ping()
                logger.info(f"Redis CacheManager initialized for namespace: {self.namespace}")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis for CacheManager ({self.namespace}): {e}. Using in-memory fallback.")
                self._redis_failed = True
                self._redis = None
        return self._redis

    def _generate_key(self, url: str, params: Optional[dict] = None) -> str:
        """Generate cache key from URL/niche and optional params."""
        key_string = url
        if params:
            key_string += json.dumps(params, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, url: str, params: Optional[dict] = None) -> Optional[Any]:
        """Get cached data if available and not expired (from Redis or in-memory fallback)."""
        key = self._generate_key(url, params)
        redis_key = f"{self.namespace}:{key}"
        
        r = self._get_redis()
        if r:
            try:
                val = r.get(redis_key)
                if val:
                    logger.debug(f"Redis cache hit for {redis_key}")
                    return json.loads(val)
                return None
            except Exception as e:
                logger.warning(f"Redis GET failed in CacheManager: {e}")
                # Fallback to in-memory below
        
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        
        # Check if expired
        if time.time() > entry["expires_at"]:
            del self._cache[key]
            logger.debug(f"In-memory cache expired for {url}")
            return None
        
        logger.debug(f"In-memory cache hit for {url}")
        return entry["data"]
    
    def set(self, url: str, data: Any, ttl: Optional[int] = None, params: Optional[dict] = None):
        """Set cache entry with optional custom TTL (in Redis or in-memory fallback)."""
        key = self._generate_key(url, params)
        ttl = ttl or self.default_ttl
        redis_key = f"{self.namespace}:{key}"
        
        r = self._get_redis()
        if r:
            try:
                r.setex(redis_key, ttl, json.dumps(data))
                logger.debug(f"Redis cache set for {redis_key} with TTL {ttl}s")
                return
            except Exception as e:
                logger.warning(f"Redis SET failed in CacheManager: {e}")
                # Fallback to in-memory below
        
        if len(self._cache) >= self.max_cache_size:
            # Remove oldest entry
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k]["created_at"])
            del self._cache[oldest_key]
            logger.debug(f"In-memory cache full, removed oldest entry")
        
        self._cache[key] = {
            "data": data,
            "created_at": time.time(),
            "expires_at": time.time() + ttl,
            "url": url
        }
        
        logger.debug(f"Cached in-memory data for {url} with TTL {ttl}s")
    
    def delete(self, url: str, params: Optional[dict] = None):
        """Delete specific cache entry."""
        key = self._generate_key(url, params)
        redis_key = f"{self.namespace}:{key}"
        
        r = self._get_redis()
        if r:
            try:
                r.delete(redis_key)
                logger.debug(f"Redis cache deleted for {redis_key}")
            except Exception as e:
                logger.warning(f"Redis DELETE failed in CacheManager: {e}")
        
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Deleted in-memory cache for {url}")
    
    def clear(self):
        """Clear all cached data."""
        r = self._get_redis()
        if r:
            try:
                # Find and delete all keys in this namespace
                keys = r.keys(f"{self.namespace}:*")
                if keys:
                    r.delete(*keys)
                logger.info(f"Redis cache cleared for namespace {self.namespace}")
            except Exception as e:
                logger.warning(f"Redis CLEAR failed in CacheManager: {e}")
                
        self._cache.clear()
        logger.info(f"In-memory cache cleared for namespace {self.namespace}")
    
    def cleanup_expired(self):
        """Remove all expired entries (only relevant for in-memory)."""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time > entry["expires_at"]
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired in-memory cache entries")
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        current_time = time.time()
        expired = sum(1 for entry in self._cache.values() if current_time > entry["expires_at"])
        
        return {
            "total_entries": len(self._cache),
            "expired_entries": expired,
            "active_entries": len(self._cache) - expired,
            "max_size": self.max_cache_size,
            "default_ttl": self.default_ttl,
            "namespace": self.namespace,
            "using_redis": self._redis is not None and not self._redis_failed
        }


class ScrapedDataCache:
    """
    Specialized cache for scraped intelligence data.
    Provides structured caching for research data.
    """
    
    def __init__(self):
        self.topic_cache = CacheManager(default_ttl=1800, namespace="scraped:topic")  # 30 min for topics
        self.trend_cache = CacheManager(default_ttl=600, namespace="scraped:trend")    # 10 min for trends
        self.audience_cache = CacheManager(default_ttl=3600, namespace="scraped:audience")  # 1 hour for audience
        self.seo_cache = CacheManager(default_ttl=7200, namespace="scraped:seo")     # 2 hours for SEO
    
    def cache_topic_research(self, topic: str, niche: str, data: dict):
        """Cache topic research data."""
        key = f"{topic}:{niche}"
        self.topic_cache.set(key, data)
    
    def get_topic_research(self, topic: str, niche: str) -> Optional[dict]:
        """Get cached topic research."""
        key = f"{topic}:{niche}"
        return self.topic_cache.get(key)
    
    def cache_trends(self, niche: str, data: list):
        """Cache trend data."""
        self.trend_cache.set(niche, data, ttl=600)
    
    def get_trends(self, niche: str) -> Optional[list]:
        """Get cached trends."""
        return self.trend_cache.get(niche)
    
    def cache_audience_insights(self, topic: str, data: dict):
        """Cache audience insights."""
        self.audience_cache.set(topic, data)
    
    def get_audience_insights(self, topic: str) -> Optional[dict]:
        """Get cached audience insights."""
        return self.audience_cache.get(topic)
    
    def cache_seo_data(self, keyword: str, data: dict):
        """Cache SEO data."""
        self.seo_cache.set(keyword, data)
    
    def get_seo_data(self, keyword: str) -> Optional[dict]:
        """Get cached SEO data."""
        return self.seo_cache.get(keyword)
    
    def clear_all(self):
        """Clear all caches."""
        self.topic_cache.clear()
        self.trend_cache.clear()
        self.audience_cache.clear()
        self.seo_cache.clear()


# Global cache instance
scraped_data_cache = ScrapedDataCache()