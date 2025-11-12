# Channel analysis tasks
# Note: For MVP, these are implemented as FastAPI BackgroundTasks in routers/channels.py
# This file is for future Celery migration

from app.tasks.celery_app import celery_app
from app.services.context_optimizer import (
    optimize_transcript_for_ai,
    MAX_TRANSCRIPT_CHARS
)

import logging
logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.channel_tasks.run_full_channel_analysis")
def run_full_channel_analysis(channel_id: str, uploads_playlist_id: str = None):
    """
    Celery task for full channel analysis.
    
    Migration path:
    1. Install Redis and configure REDIS_URL
    2. Start Celery worker: celery -A app.tasks.celery_app worker
    3. Replace BackgroundTasks.add_task() with this.delay()
    """
    from app.database import SessionLocal
    from app.models.channel import Channel
    from app.models.video import Video
    from app.services.youtube_service import (
        fetch_channel_videos, fetch_video_statistics,
        fetch_transcript, fetch_channel_details
    )
    from app.intelligence.creator_analyzer import CreatorAnalyzer
    from datetime import datetime

    db = SessionLocal()
    try:
        channel = db.query(Channel).filter(Channel.id == channel_id).first()
        if not channel:
            return

        channel.analysis_status = "running"
        db.commit()

        # Full implementation in routers/channels.py:run_full_channel_analysis()
        # This is a stub for future Celery migration

        logger.info(f"Celery: Channel analysis task for {channel_id}")
    except Exception as e:
        logger.error(f"Celery: Channel analysis failed for {channel_id}: {e}")
    finally:
        db.close()


# =============================================================================
# OPTIMIZED DATA FETCHING FUNCTIONS
# These are used by routers/channels.py for optimized channel analysis
# =============================================================================

def get_optimized_transcript(transcript_text: str) -> str:
    """
    Get transcript optimized for AI consumption.
    Limits length and removes unnecessary content.
    """
    return optimize_transcript_for_ai(transcript_text, max_chars=MAX_TRANSCRIPT_CHARS)


def get_top_videos_for_analysis(
    video_stats: list, 
    max_videos: int = 5,
    include_transcript_for: int = 3
) -> list:
    """
    Select and prepare top videos for AI analysis.
    
    Args:
        video_stats: List of video stat dicts sorted by views
        max_videos: Maximum number of videos to include (default 5)
        include_transcript_for: How many top videos should include transcript (default 3)
    
    Returns:
        List of prepared video dicts with optimized context
    """
    selected = []
    for i, video in enumerate(video_stats[:max_videos]):
        prepared = {
            'youtube_video_id': video.get('youtube_video_id'),
            'title': video.get('title', 'Unknown')[:60],
            'views': video.get('view_count', 0),
            'likes': video.get('like_count', 0),
            'duration_seconds': video.get('duration_seconds', 0),
        }
        
        # Only include transcript for top N videos to save tokens
        if i < include_transcript_for and video.get('transcript_excerpt'):
            # Truncate transcript for AI
            prepared['transcript_excerpt'] = video['transcript_excerpt'][:500]
        else:
            prepared['transcript_excerpt'] = ''
        
        selected.append(prepared)
    
    return selected


def compress_channel_context(channel_data: dict, video_stats: list) -> dict:
    """
    Compress channel and video data for efficient AI analysis.
    
    Args:
        channel_data: Full channel data from YouTube API
        video_stats: List of video stats
        
    Returns:
        Compact context dict
    """
    # Compress channel info
    context = {
        'title': channel_data.get('title', 'Unknown'),
        'subscriber_count': channel_data.get('subscriber_count', 0),
        'total_videos': len(video_stats),
        'top_videos': []
    }
    
    # Compress top 5 videos (title + basic stats only)
    for video in video_stats[:5]:
        context['top_videos'].append({
            'title': video.get('title', 'Unknown')[:60],
            'views': video.get('view_count', 0),
            'likes': video.get('like_count', 0),
            'duration_min': video.get('duration_seconds', 0) // 60
        })
    
    return context


def should_fetch_transcript(video_views: int, rank: int, max_transcripts: int = 5) -> bool:
    """
    Determine if transcript should be fetched for a video.
    Prioritizes high-performing videos.
    
    Args:
        video_views: View count of the video
        rank: Position in sorted-by-views list
        max_transcripts: Maximum transcripts to fetch
        
    Returns:
        True if transcript should be fetched
    """
    # Fetch for top N videos by performance
    if rank < max_transcripts:
        return True
    
    # Always fetch if video has >1M views (viral potential)
    if video_views > 1_000_000:
        return True
    
    return False


def get_comment_analysis_limit(channel_subscriber_count: int) -> int:
    """
    Determine how many comments to analyze based on channel size.
    Larger channels = more comments for better patterns.
    
    Args:
        channel_subscriber_count: Number of subscribers
        
    Returns:
        Number of comments to analyze
    """
    if channel_subscriber_count > 1_000_000:
        return 50
    elif channel_subscriber_count > 100_000:
        return 30
    elif channel_subscriber_count > 10_000:
        return 20
    else:
        return 10