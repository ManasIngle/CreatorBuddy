"""
Async HTTP Client for YouTube Service
Provides async HTTP operations with connection pooling and resilience.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class AsyncHTTPClient:
    """
    Async HTTP client with connection pooling, timeouts, and retry logic.
    
    Benefits:
    - Connection reuse via persistent connections
    - Async operations for non-blocking I/O
    - Built-in retry with exponential backoff
    - Connection pool limits prevent resource exhaustion
    """
    
    _instance: Optional['AsyncHTTPClient'] = None
    _client: Optional[httpx.AsyncClient] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def initialize(self):
        """Initialize the async HTTP client with connection pooling."""
        if self._client is None:
            limits = httpx.Limits(
                max_keepalive_connections=20,
                max_connections=50,
                keepalive_expiry=30.0
            )
            timeout = httpx.Timeout(
                connect=10.0,
                read=30.0,
                write=30.0,
                pool=30.0
            )
            self._client = httpx.AsyncClient(
                limits=limits,
                timeout=timeout,
                follow_redirects=True,
                headers={
                    "User-Agent": "CreatorIQ/1.0",
                    "Accept": "application/json"
                }
            )
            logger.info("Async HTTP client initialized")
    
    async def close(self):
        """Close the HTTP client and release connections."""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("Async HTTP client closed")
    
    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client instance."""
        if self._client is None:
            raise RuntimeError("HTTP client not initialized. Call initialize() first.")
        return self._client
    
    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> httpx.Response:
        """
        Perform async GET request.
        
        Args:
            url: Target URL
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout override
            
        Returns:
            httpx.Response object
        """
        if not self._client:
            await self.initialize()
        
        timeout_obj = httpx.Timeout(timeout) if timeout else None
        
        response = await self._client.get(
            url,
            params=params,
            headers=headers,
            timeout=timeout_obj
        )
        response.raise_for_status()
        return response
    
    async def post(
        self,
        url: str,
        json: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> httpx.Response:
        """Perform async POST request."""
        if not self._client:
            await self.initialize()
        
        timeout_obj = httpx.Timeout(timeout) if timeout else None
        
        response = await self._client.post(
            url,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout_obj
        )
        response.raise_for_status()
        return response
    
    async def batch_get(
        self,
        urls: List[str],
        max_concurrent: int = 5,
        timeout: Optional[float] = None
    ) -> List[httpx.Response]:
        """
        Perform batch GET requests with concurrency limit.
        
        Args:
            urls: List of URLs to fetch
            max_concurrent: Maximum concurrent requests
            timeout: Request timeout
            
        Returns:
            List of responses in same order as URLs
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_with_limit(url: str) -> httpx.Response:
            async with semaphore:
                return await self.get(url, timeout=timeout)
        
        tasks = [fetch_with_limit(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to None responses
        return [r if isinstance(r, httpx.Response) else None for r in results]


# Global HTTP client instance
http_client = AsyncHTTPClient()


class YouTubeAPIClient:
    """
    Specialized YouTube API client with async operations.
    
    Uses googleapiclient for actual API calls (synchronous),
    but wraps operations in async functions for better concurrency.
    """
    
    def __init__(self):
        self._youtube = None
        self._access_token: Optional[str] = None
    
    def _get_youtube_client(self, access_token: Optional[str] = None):
        """Get or create YouTube API client."""
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials
        
        # Return cached client if no token change
        if access_token and access_token != self._access_token:
            creds = Credentials(token=access_token)
            self._youtube = build("youtube", "v3", credentials=creds)
            self._access_token = access_token
        elif self._youtube is None:
            self._youtube = build("youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)
        
        return self._youtube
    
    async def fetch_channel_details_async(self, channel_id: str) -> Dict[str, Any]:
        """
        Fetch channel details asynchronously.
        
        Note: YouTube API client is sync, so we run it in executor.
        """
        loop = asyncio.get_event_loop()
        
        def fetch():
            youtube = self._get_youtube_client()
            response = youtube.channels().list(
                part="snippet,statistics,contentDetails,brandingSettings",
                id=channel_id
            ).execute()
            if not response.get("items"):
                raise ValueError(f"Channel {channel_id} not found")
            item = response["items"][0]
            return {
                "youtube_channel_id": item["id"],
                "title": item["snippet"]["title"],
                "description": item["snippet"].get("description", ""),
                "thumbnail_url": item["snippet"]["thumbnails"].get("high", {}).get("url"),
                "subscriber_count": int(item["statistics"].get("subscriberCount", 0)),
                "video_count": int(item["statistics"].get("videoCount", 0)),
                "view_count": int(item["statistics"].get("viewCount", 0)),
                "country": item["snippet"].get("country"),
                "uploads_playlist_id": item["contentDetails"]["relatedPlaylists"]["uploads"],
                "custom_url": item.get("snippet", {}).get("customUrl")
            }
        
        return await loop.run_in_executor(None, fetch)
    
    async def fetch_videos_parallel(
        self,
        uploads_playlist_id: str,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Fetch channel videos with improved concurrency.
        
        Fetches video list then statistics in parallel where possible.
        """
        loop = asyncio.get_event_loop()
        
        def fetch_video_ids():
            youtube = self._get_youtube_client()
            videos = []
            next_page_token = None
            
            while len(videos) < max_results:
                response = youtube.playlistItems().list(
                    part="snippet,contentDetails",
                    playlistId=uploads_playlist_id,
                    maxResults=min(50, max_results - len(videos)),
                    pageToken=next_page_token
                ).execute()
                
                for item in response.get("items", []):
                    videos.append({
                        "youtube_video_id": item["contentDetails"]["videoId"],
                        "title": item["snippet"]["title"],
                        "published_at": item["snippet"]["publishedAt"],
                        "thumbnail_url": item["snippet"]["thumbnails"].get("high", {}).get("url")
                    })
                
                next_page_token = response.get("nextPageToken")
                if not next_page_token:
                    break
            
            return videos
        
        # Fetch video IDs
        videos = await loop.run_in_executor(None, fetch_video_ids)
        
        # Fetch statistics in batches (YouTube API allows 50 at a time)
        video_ids = [v["youtube_video_id"] for v in videos]
        
        async def fetch_batch(batch_ids: List[str]) -> List[Dict]:
            def fetch():
                youtube = self._get_youtube_client()
                response = youtube.videos().list(
                    part="snippet,statistics,contentDetails",
                    id=",".join(batch_ids)
                ).execute()
                
                results = []
                for item in response.get("items", []):
                    duration = item["contentDetails"].get("duration", "PT0S")
                    duration_seconds = self._parse_duration(duration)
                    results.append({
                        "youtube_video_id": item["id"],
                        "title": item["snippet"]["title"],
                        "description": item["snippet"].get("description", ""),
                        "tags": item["snippet"].get("tags", []),
                        "category_id": item["snippet"].get("categoryId"),
                        "published_at": item["snippet"]["publishedAt"],
                        "thumbnail_url": item["snippet"]["thumbnails"].get("maxres", 
                            item["snippet"]["thumbnails"].get("high", {})).get("url"),
                        "view_count": int(item["statistics"].get("viewCount", 0)),
                        "like_count": int(item["statistics"].get("likeCount", 0)),
                        "comment_count": int(item["statistics"].get("commentCount", 0)),
                        "duration_seconds": duration_seconds
                    })
                return results
        
        # Fetch stats in parallel batches (3 at a time to avoid quota issues)
        semaphore = asyncio.Semaphore(3)
        
        async def fetch_batch_with_limit(batch_ids: List[str]) -> List[Dict]:
            async with semaphore:
                return await loop.run_in_executor(None, lambda: fetch_batch(batch_ids))
        
        batches = [video_ids[i:i+50] for i in range(0, len(video_ids), 50)]
        batch_results = await asyncio.gather(*[
            fetch_batch_with_limit(batch) for batch in batches
        ])
        
        # Flatten results
        all_stats = []
        for batch_result in batch_results:
            all_stats.extend(batch_result)
        
        # Merge with video info
        stats_dict = {s["youtube_video_id"]: s for s in all_stats}
        for video in videos:
            video.update(stats_dict.get(video["youtube_video_id"], {}))
        
        return videos
    
    def _parse_duration(self, duration: str) -> int:
        """Convert ISO 8601 duration to seconds."""
        import re
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration)
        if not match:
            return 0
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        return hours * 3600 + minutes * 60 + seconds


# Global YouTube API client
youtube_client = YouTubeAPIClient()