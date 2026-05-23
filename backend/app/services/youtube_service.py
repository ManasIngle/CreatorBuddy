from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from youtube_transcript_api import YouTubeTranscriptApi
from typing import List, Optional, Dict, Any
from app.config import settings
import httpx
import logging
import json

logger = logging.getLogger(__name__)


# ── Redis cache helpers for YouTube API ─────────────────────────────────
async def _get_cached(key: str) -> Optional[Any]:
    """Get value from Redis cache (non-blocking, returns None on failure)."""
    try:
        from app.services.redis_cache import redis_cache
        await redis_cache.initialize()
        return await redis_cache.get(key)
    except Exception:
        return None

async def _set_cached(key: str, value: Any, ttl: int = 3600) -> None:
    """Set value in Redis cache (fire-and-forget)."""
    try:
        from app.services.redis_cache import redis_cache
        await redis_cache.initialize()
        await redis_cache.set(key, value, ttl=ttl)
    except Exception:
        pass


def get_youtube_client(access_token: Optional[str] = None):
    """
    Returns YouTube API client.
    If access_token provided, uses OAuth (for private channel data).
    Otherwise uses API key (for public data).
    Docs: https://developers.google.com/youtube/v3/getting-started
    """
    if access_token:
        creds = Credentials(token=access_token)
        return build("youtube", "v3", credentials=creds)
    return build("youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)

def fetch_channel_details(channel_id: str) -> Dict[str, Any]:
    """
    Fetches channel metadata.
    API ref: https://developers.google.com/youtube/v3/docs/channels/list
    Parts used: snippet, statistics, contentDetails
    Cost: 1 quota unit
    """
    youtube = get_youtube_client()
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
        "uploads_playlist_id": item["contentDetails"]["relatedPlaylists"]["uploads"]
    }


async def fetch_channel_details_cached(channel_id: str) -> Dict[str, Any]:
    """
    Cached version of fetch_channel_details.
    Cache TTL: 1 hour — channel metadata rarely changes.
    Saves 1 YouTube API quota unit per cache hit.
    """
    cache_key = f"yt:channel:{channel_id}"
    cached = await _get_cached(cache_key)
    if cached is not None:
        logger.debug(f"Cache hit for channel {channel_id}")
        return cached
    
    result = fetch_channel_details(channel_id)
    await _set_cached(cache_key, result, ttl=3600)  # 1 hour
    return result

def fetch_channel_videos(uploads_playlist_id: str, max_results: int = 50) -> List[Dict]:
    """
    Fetches video IDs from uploads playlist.
    API ref: https://developers.google.com/youtube/v3/docs/playlistItems/list
    Cost: 1 quota unit per page (50 results per page)
    """
    youtube = get_youtube_client()
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

def fetch_video_statistics(video_ids: List[str]) -> List[Dict]:
    """
    Fetches detailed stats for up to 50 videos per request.
    API ref: https://developers.google.com/youtube/v3/docs/videos/list
    Cost: 1 quota unit per 50 videos
    """
    youtube = get_youtube_client()
    all_results = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        response = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=",".join(batch)
        ).execute()
        for item in response.get("items", []):
            duration = item["contentDetails"].get("duration", "PT0S")
            # Parse ISO 8601 duration to seconds
            duration_seconds = _parse_duration(duration)
            all_results.append({
                "youtube_video_id": item["id"],
                "title": item["snippet"]["title"],
                "description": item["snippet"].get("description", ""),
                "tags": item["snippet"].get("tags", []),
                "category_id": item["snippet"].get("categoryId"),
                "published_at": item["snippet"]["publishedAt"],
                "thumbnail_url": item["snippet"]["thumbnails"].get("maxres", item["snippet"]["thumbnails"].get("high", {})).get("url"),
                "view_count": int(item["statistics"].get("viewCount", 0)),
                "like_count": int(item["statistics"].get("likeCount", 0)),
                "comment_count": int(item["statistics"].get("commentCount", 0)),
                "duration_seconds": duration_seconds
            })
    return all_results

def fetch_video_comments(video_id: str, max_results: int = 100) -> List[str]:
    """
    Fetches top-level comment texts for audience psychology analysis.
    API ref: https://developers.google.com/youtube/v3/docs/commentThreads/list
    Cost: 1 quota unit per page
    """
    youtube = get_youtube_client()
    comments = []
    try:
        response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=min(100, max_results),
            order="relevance",
            textFormat="plainText"
        ).execute()
        for item in response.get("items", []):
            text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(text)
    except Exception as e:
        logger.warning(f"Failed to fetch comments for video {video_id}: {e}")
        pass  # Comments may be disabled
    return comments

def fetch_transcript(video_id: str) -> Optional[str]:
    """
    Fetches auto-generated or manual transcript.
    Uses youtube-transcript-api library.
    Falls back gracefully if transcript unavailable.
    """
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([item["text"] for item in transcript_list])
    except Exception as e:
        logger.warning(f"Failed to fetch transcript for video {video_id}: {e}")
        return None

def search_competitor_channels(niche: str, max_results: int = 10) -> List[Dict]:
    """
    Searches for competitor channels by niche keyword.
    API ref: https://developers.google.com/youtube/v3/docs/search/list
    Cost: 100 quota units per request — use sparingly
    """
    youtube = get_youtube_client()
    response = youtube.search().list(
        part="snippet",
        q=niche,
        type="channel",
        maxResults=max_results,
        order="relevance"
    ).execute()
    results = []
    for item in response.get("items", []):
        results.append({
            "youtube_channel_id": item["snippet"]["channelId"],
            "title": item["snippet"]["channelTitle"],
            "description": item["snippet"].get("description", "")
        })
    return results

def _parse_duration(duration: str) -> int:
    """Convert ISO 8601 duration to seconds. e.g. PT1H2M3S -> 3723"""
    import re
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, duration)
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds