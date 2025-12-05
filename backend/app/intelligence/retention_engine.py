from typing import Dict
from app.services.openrouter_service import call_openai, safe_json_loads
from app.prompts.retention_prompts import RETENTION_ANALYSIS_PROMPT
import logging

logger = logging.getLogger(__name__)

class RetentionEngine:

    def analyze_retention(
        self,
        video_title: str,
        transcript: str,
        duration_seconds: int
    ) -> Dict:
        """
        Analyze video transcript to identify retention patterns and drop-off points.
        """
        prompt = RETENTION_ANALYSIS_PROMPT.format(
            title=video_title,
            transcript=transcript[:5000],  # Limit transcript length
            duration_seconds=duration_seconds
        )
        try:
            response = call_openai(
                system_prompt="You are a YouTube retention analyst. Return JSON only.",
                user_prompt=prompt,
                response_format="json"
            )
            return safe_json_loads(response)
        except Exception as e:
            logger.error(f"Retention analysis failed: {e}")
            return {
                "retention_hooks": [],
                "drop_off_points": [],
                "pacing_score": 0.0,
                "pacing_notes": "",
                "retention_tips": []
            }