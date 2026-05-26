from typing import Dict, List, Optional
from app.services.openrouter_service import call_openai, safe_json_loads
from app.prompts.creator_prompts import CREATOR_PROFILE_PROMPT
from app.services.context_optimizer import (
    compress_videos_for_analysis, 
    truncate_to_token_limit,
    count_tokens,
    compress_video_context
)
import json
import logging

logger = logging.getLogger(__name__)


class CreatorAnalyzer:

    def analyze_creator(
        self,
        channel_title: str,
        top_video_data: List[Dict],
        subscriber_count: int,
        user_id: Optional[str] = None,
    ) -> Dict:
        """
        Builds creator profile from their top video data.
        Uses context optimization to minimize tokens while preserving insights.
        
        Args:
            channel_title: Name of the channel
            top_video_data: List of video dicts with title, views, transcript_excerpt
            subscriber_count: Number of subscribers
            
        Returns:
            Creator profile dict with niche, audience, personality, etc.
        """
        # Compress video context - use top 5 videos, no transcript for AI context
        # If transcript_excerpt is short enough, include it; otherwise skip
        video_summaries = []
        for vd in top_video_data[:5]:
            # Include transcript only if it's brief (<500 chars)
            transcript = vd.get('transcript_excerpt', '')
            include_transcript = len(transcript) <= 500
            
            summary = compress_video_context(vd, include_transcript=include_transcript)
            video_summaries.append(summary)
        
        # Join with separators and truncate to token limit
        context = "\n\n".join(video_summaries)
        context = truncate_to_token_limit(context, 2000)  # Conservative limit
        
        prompt = CREATOR_PROFILE_PROMPT.format(
            channel_name=channel_title,
            subscriber_count=subscriber_count,
            video_samples=context
        )

        try:
            response = call_openai(
                system_prompt="Analyze YouTube creator. Return JSON only. Be concise.",
                user_prompt=prompt,
                response_format="json",
                complexity="medium",
                user_id=user_id,
                operation="creator_profile",
            )
            return safe_json_loads(response)
        except Exception as e:
            logger.error(f"Creator analysis failed: {e}")
            return {
                "niche": "unknown",
                "niche_tags": [],
                "audience_type": "unknown",
                "personality_summary": "",
                "speaking_style": "",
                "storytelling_structure": "unknown",
                "content_themes": [],
                "audience_pain_points": [],
                "creator_strength": "",
                "growth_opportunity": ""
            }