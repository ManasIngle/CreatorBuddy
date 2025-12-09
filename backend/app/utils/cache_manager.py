"""
Cache Manager for Scraped Data
Caches scraped content with TTL to reduce redundant requests
"""

import time
import hashlib
import json
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """
    In-memory cache for scraped data with TTL support.
    Reduces redundant scraping requests and improves performance.
    """
    
    def __init__(self, default_ttl: int = 3600):  # Default 1 hour TTL
        self._cache: Dict[str, dict] = {}
        self.default_ttl = default_ttl
        self.max_cache_size = 1000
    
    def _generate_key(self, url: str, params: Optional[dict] = None) -> str:
        """Generate cache key from URL and optional params"""
        key_string = url
        if params:
            key_string += json.dumps(params, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, url: str, params: Optional[dict] = None) -> Optional[Any]:
        """Get cached data if available and not expired"""
        key = self._generate_key(url, params)
        
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        
        # Check if expired
        if time.time() > entry["expires_at"]:
            del self._cache[key]
            logger.debug(f"Cache expired for {url}")
            return None
        
        logger.debug(f"Cache hit for {url}")
        return entry["data"]
    
    def set(self, url: str, data: Any, ttl: Optional[int] = None, params: Optional[dict] = None):
        """Set cache entry with optional custom TTL"""
        if len(self._cache) >= self.max_cache_size:
            # Remove oldest entry
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k]["created_at"])
            del self._cache[oldest_key]
            logger.debug(f"Cache full, removed oldest entry")
        
        key = self._generate_key(url, params)
        ttl = ttl or self.default_ttl
        
        self._cache[key] = {
            "data": data,
            "created_at": time.time(),
            "expires_at": time.time() + ttl,
            "url": url
        }
        
        logger.debug(f"Cached data for {url} with TTL {ttl}s")
    
    def delete(self, url: str, params: Optional[dict] = None):
        """Delete specific cache entry"""
        key = self._generate_key(url, params)
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Deleted cache for {url}")
    
    def clear(self):
        """Clear all cached data"""
        self._cache.clear()
        logger.info("Cache cleared")
    
    def cleanup_expired(self):
        """Remove all expired entries"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time > entry["expires_at"]
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        current_time = time.time()
        expired = sum(1 for entry in self._cache.values() if current_time > entry["expires_at"])
        
        return {
            "total_entries": len(self._cache),
            "expired_entries": expired,
            "active_entries": len(self._cache) - expired,
            "max_size": self.max_cache_size,
            "default_ttl": self.default_ttl
        }


class ScrapedDataCache:
    """
    Specialized cache for scraped intelligence data.
    Provides structured caching for research data.
    """
    
    def __init__(self):
        self.topic_cache = CacheManager(default_ttl=1800)  # 30 min for topics
        self.trend_cache = CacheManager(default_ttl=600)    # 10 min for trends
        self.audience_cache = CacheManager(default_ttl=3600)  # 1 hour for audience
        self.seo_cache = CacheManager(default_ttl=7200)     # 2 hours for SEO
    
    def cache_topic_research(self, topic: str, niche: str, data: dict):
        """Cache topic research data"""
        key = f"{topic}:{niche}"
        self.topic_cache.set(key, data)
    
    def get_topic_research(self, topic: str, niche: str) -> Optional[dict]:
        """Get cached topic research"""
        key = f"{topic}:{niche}"
        return self.topic_cache.get(key)
    
    def cache_trends(self, niche: str, data: list):
        """Cache trend data"""
        self.trend_cache.set(niche, data, ttl=600)
    
    def get_trends(self, niche: str) -> Optional[list]:
        """Get cached trends"""
        return self.trend_cache.get(niche)
    
    def cache_audience_insights(self, topic: str, data: dict):
        """Cache audience insights"""
        self.audience_cache.set(topic, data)
    
    def get_audience_insights(self, topic: str) -> Optional[dict]:
        """Get cached audience insights"""
        return self.audience_cache.get(topic)
    
    def cache_seo_data(self, keyword: str, data: dict):
        """Cache SEO data"""
        self.seo_cache.set(keyword, data)
    
    def get_seo_data(self, keyword: str) -> Optional[dict]:
        """Get cached SEO data"""
        return self.seo_cache.get(keyword)
    
    def clear_all(self):
        """Clear all caches"""
        self.topic_cache.clear()
        self.trend_cache.clear()
        self.audience_cache.clear()
        self.seo_cache.clear()


# Global cache instance
scraped_data_cache = ScrapedDataCache()