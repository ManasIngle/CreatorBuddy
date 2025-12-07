from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Header
from sqlalchemy.orm import Session, selectinload
from app.database import get_db
from app.models.user import User
from app.models.channel import Channel
from app.models.analysis_job import AnalysisJob
from app.utils.auth_utils import get_current_user
from app.utils.base import BaseRouter, ETags, MetricsCollector, ValidationError, InputValidator
from app.services.youtube_service import fetch_channel_details
from app.services.redis_cache import redis_cache, CacheKeys, CacheInvalidator
from app.schemas.channel import ChannelResponse, ConnectChannelRequest, ChannelListResponse
from typing import List, Optional
import uuid
import logging
import time

logger = logging.getLogger(__name__)

router = APIRouter()


def run_full_channel_analysis(channel_id: str, uploads_playlist_id: str = None):
    """
    Background task for full channel analysis.
    Uses database session context manager for proper cleanup.
    """
    from app.database import get_db_session
    from app.models.channel import Channel
    from app.models.video import Video
    from app.services.youtube_service import (
        fetch_channel_videos, fetch_video_statistics,
        fetch_transcript
    )
    from app.services.openrouter_service import get_embedding
    from app.intelligence.creator_analyzer import CreatorAnalyzer
    from app.prompts.creator_prompts import CREATOR_PROFILE_PROMPT
    from app.utils.cache_manager import scraped_data_cache
    from datetime import datetime

    with get_db_session() as db:
        try:
            start_time = time.time()
            channel = db.query(Channel).filter(Channel.id == channel_id).first()
            if not channel:
                return

            channel.analysis_status = "running"
            db.commit()

            # Step 1 & 2: Fetch videos
            if not uploads_playlist_id:
                yt_data = fetch_channel_details(channel.youtube_channel_id)
                uploads_playlist_id = yt_data["uploads_playlist_id"]

            raw_videos = fetch_channel_videos(uploads_playlist_id, max_results=50)
            video_ids = [v["youtube_video_id"] for v in raw_videos]
            video_stats = fetch_video_statistics(video_ids)

            if not video_stats:
                channel.analysis_status = "failed"
                db.commit()
                return

            # Calculate channel averages
            total_views = sum(v["view_count"] for v in video_stats)
            avg_views = total_views / len(video_stats) if video_stats else 0

            # Step 3 & 4: Save videos and extract transcripts
            transcripts_collected = []
            for vs in video_stats:
                engagement = (vs["like_count"] + vs["comment_count"]) / max(vs["view_count"], 1)
                is_viral = vs["view_count"] > (avg_views * 3)

                video = db.query(Video).filter(
                    Video.youtube_video_id == vs["youtube_video_id"]
                ).first()

                if not video:
                    video = Video(channel_id=channel_id)

                video.youtube_video_id = vs["youtube_video_id"]
                video.title = vs["title"]
                video.description = vs.get("description", "")
                video.thumbnail_url = vs.get("thumbnail_url")
                video.view_count = vs["view_count"]
                video.like_count = vs["like_count"]
                video.comment_count = vs["comment_count"]
                video.engagement_rate = engagement
                video.duration_seconds = vs.get("duration_seconds", 0)
                video.tags = vs.get("tags", [])
                video.published_at = vs["published_at"]
                video.is_viral = is_viral
                video.is_competitor_video = False

                db.add(video)

                # Fetch transcript for top 10 by views
                if len(transcripts_collected) < 10 and vs["view_count"] > avg_views * 0.5:
                    transcript = fetch_transcript(vs["youtube_video_id"])
                    if transcript:
                        video.transcript = transcript[:10000]
                        video.hook_text = transcript[:500]
                        transcripts_collected.append({
                            "title": vs["title"],
                            "views": vs["view_count"],
                            "transcript_excerpt": transcript[:1000]
                        })

            db.commit()

            # Step 5: AI Creator Profile Analysis
            if transcripts_collected:
                analyzer = CreatorAnalyzer()
                profile = analyzer.analyze_creator(
                    channel_title=channel.title,
                    top_video_data=transcripts_collected[:5],
                    subscriber_count=channel.subscriber_count
                )
                channel.niche = profile.get("niche")
                channel.niche_tags = profile.get("niche_tags", [])
                channel.audience_type = profile.get("audience_type")
                channel.personality_summary = profile.get("personality_summary")
                channel.speaking_style = profile.get("speaking_style")
                channel.storytelling_structure = profile.get("storytelling_structure")

            channel.avg_views = avg_views
            channel.last_analyzed_at = datetime.utcnow()
            channel.analysis_status = "done"
            db.commit()

            # Invalidate cache after successful analysis
            import asyncio
            asyncio.create_task(CacheInvalidator.invalidate_channel(str(channel_id)))
            
            duration = (time.time() - start_time) * 1000
            MetricsCollector.record_timing("channel_analysis", duration)
            logger.info(f"Channel analysis complete for {channel_id} in {duration:.0f}ms")

        except Exception as e:
            logger.error(f"Channel analysis failed for {channel_id}: {e}")
            if channel:
                channel.analysis_status = "failed"
                db.commit()


@router.post("/connect", response_model=ChannelResponse, status_code=201, tags=["channels"])
async def connect_channel(
    request: ConnectChannelRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Connect a YouTube channel to the user's account.
    
    - **youtube_channel_id**: The channel ID (starts with UC...) or handle (@username)
    
    Triggers full background analysis immediately after creation.
    Analysis typically takes 2-3 minutes to complete.
    """
    # Validate input
    try:
        validated_channel_id = InputValidator.validate_youtube_channel_id(request.youtube_channel_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    
    # Check if already connected
    existing = db.query(Channel).filter(
        Channel.youtube_channel_id == validated_channel_id,
        Channel.user_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Channel already connected")

    # Fetch basic channel info from YouTube
    try:
        yt_data = fetch_channel_details(validated_channel_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"YouTube API error: {e}")
        raise HTTPException(status_code=502, detail="Failed to fetch channel from YouTube")

    channel = Channel(
        user_id=current_user.id,
        youtube_channel_id=yt_data["youtube_channel_id"],
        title=yt_data["title"],
        description=yt_data["description"],
        subscriber_count=yt_data["subscriber_count"],
        video_count=yt_data["video_count"],
        view_count=yt_data["view_count"],
        thumbnail_url=yt_data["thumbnail_url"],
        country=yt_data.get("country"),
        analysis_status="pending"
    )
    db.add(channel)
    db.commit()
    db.refresh(channel)

    # Create analysis job
    job = AnalysisJob(
        job_type="channel_analysis",
        entity_id=channel.id,
        status="queued"
    )
    db.add(job)
    db.commit()

    # Queue background analysis
    background_tasks.add_task(
        run_full_channel_analysis,
        str(channel.id),
        yt_data.get("uploads_playlist_id")
    )
    logger.info(f"Channel analysis queued for {channel.id}")

    return channel


@router.get("/", response_model=ChannelListResponse, tags=["channels"])
async def list_channels(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    if_none_match: Optional[str] = Header(None)
):
    """
    List all YouTube channels connected to the current user with pagination.
    
    Supports ETag caching - include If-None-Match header for conditional requests.
    """
    # Build cache key
    cache_key = f"{CacheKeys.CHANNEL}:user:{current_user.id}:page:{page}:size:{page_size}"
    
    # Try cache first
    await redis_cache.initialize()
    cached = await redis_cache.get(cache_key)
    if cached is not None:
        # Check ETag
        etag = ETags.generate(cached)
        if if_none_match and ETags.match(etag, if_none_match):
            from fastapi.responses import Response
            return Response(status_code=304)
        return cached
    
    # Query database with optimized loading
    query = db.query(Channel).filter(Channel.user_id == current_user.id)
    paginated_query, total = BaseRouter.paginate_query(query, page, page_size)
    
    channels = paginated_query.all()
    
    response = BaseRouter.build_pagination_response(
        items=[ChannelResponse.model_validate(c) for c in channels],
        total=total,
        page=page,
        page_size=page_size
    )
    
    # Cache for 5 minutes
    await redis_cache.set(cache_key, response, ttl=300)
    
    return response


@router.get("/{channel_id}", response_model=ChannelResponse, tags=["channels"])
async def get_channel(
    channel_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    if_none_match: Optional[str] = Header(None)
):
    """
    Get details for a specific channel.
    
    - **channel_id**: UUID of the connected channel
    
    Supports ETag caching.
    """
    # Validate UUID
    try:
        validated_id = InputValidator.validate_uuid(channel_id, "channel_id")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    
    # Check cache first
    cache_key = f"{CacheKeys.CHANNEL}:{validated_id}"
    await redis_cache.initialize()
    cached = await redis_cache.get(cache_key)
    if cached:
        etag = ETags.generate(cached)
        if if_none_match and ETags.match(etag, if_none_match):
            from fastapi.responses import Response
            return Response(status_code=304)
        return cached
    
    channel = db.query(Channel).filter(
        Channel.id == validated_id,
        Channel.user_id == current_user.id
    ).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    response = ChannelResponse.model_validate(channel)
    
    # Cache for 10 minutes
    await redis_cache.set(cache_key, response, ttl=600)
    
    return response


@router.post("/{channel_id}/re-analyze", tags=["channels"])
async def trigger_reanalysis(
    channel_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Trigger re-analysis of a channel's content and stats.
    
    - **channel_id**: UUID of the channel to re-analyze
    
    This will re-fetch all videos, transcripts, and regenerate AI insights.
    Takes approximately 2-3 minutes to complete.
    """
    # Validate UUID
    try:
        validated_id = InputValidator.validate_uuid(channel_id, "channel_id")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    
    channel = db.query(Channel).filter(
        Channel.id == validated_id,
        Channel.user_id == current_user.id
    ).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # Invalidate cache before re-analysis
    await CacheInvalidator.invalidate_channel(str(channel.id))
    
    channel.analysis_status = "pending"
    db.commit()
    background_tasks.add_task(run_full_channel_analysis, str(channel.id), None)
    logger.info(f"Channel re-analysis queued for {channel.id}")
    return {"message": "Re-analysis queued"}