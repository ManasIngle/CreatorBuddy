from typing import Dict
from app.services.openrouter_service import call_openai, safe_json_loads
from app.prompts.retention_prompts import VIRAL_PATTERN_PROMPT
import logging

logger = logging.getLogger(__name__)

class ViralEngine:

    def analyze_viral_pattern(
        self,
        video_title: str,
        view_count: int,
        like_count: int,
        comment_count: int,
        engagement_rate: float,
        thumbnail_description: str,
        hook_text: str
    ) -> Dict:
        """
        Analyze why a video went viral and identify key patterns.
        """
        prompt = VIRAL_PATTERN_PROMPT.format(
            title=video_title,
            view_count=view_count,
            like_count=like_count,
            comment_count=comment_count,
            engagement_rate=engagement_rate,
            thumbnail_description=thumbnail_description,
            hook_text=hook_text or "No hook text available"
        )
        try:
            response = call_openai(
                system_prompt="You are a viral content analyst. Return JSON only.",
                user_prompt=prompt,
                response_format="json"
            )
            return safe_json_loads(response)
        except Exception as e:
            logger.error(f"Viral pattern analysis failed: {e}")
            return {
                "viral_driver": "unknown",
                "emotional_triggers": [],
                "replicable_pattern": "",
                "why_it_worked": "",
                "advice_for_creator": ""
            }