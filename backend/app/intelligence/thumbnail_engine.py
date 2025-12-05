from typing import Dict, List
from app.services.openrouter_service import call_openai_vision, call_openai, safe_json_loads
from app.prompts.thumbnail_prompts import THUMBNAIL_ANALYSIS_PROMPT, THUMBNAIL_RECOMMENDATION_PROMPT
import logging

logger = logging.getLogger(__name__)

class ThumbnailEngine:

    def analyze_thumbnail(self, thumbnail_url: str, video_title: str) -> Dict:
        """
        Analyzes a thumbnail image using GPT-4o vision.
        Returns CTR prediction, emotional strength, and recommendations.
        """
        prompt = THUMBNAIL_ANALYSIS_PROMPT.format(video_title=video_title)
        try:
            response = call_openai_vision(
                image_url=thumbnail_url,
                prompt=prompt
            )
            return safe_json_loads(response)
        except Exception as e:
            logger.error(f"Thumbnail analysis failed: {e}")
            return {
                "ctr_prediction": 0.0,
                "emotional_impact": 0.0,
                "curiosity_intensity": 0.0,
                "text_clarity": 0.0,
                "color_contrast": 0.0,
                "simplicity": 0.0,
                "alignment_score": 0.0,
                "primary_emotion": "unknown",
                "strengths": [],
                "weaknesses": [],
                "improvement_suggestions": []
            }

    def recommend_thumbnail_concept(
        self,
        topic: str,
        title: str,
        niche: str,
        top_competitor_styles: List[str]
    ) -> Dict:
        """
        Recommends a thumbnail concept based on topic and competitor analysis.
        Returns design directions without requiring an actual image.
        """
        prompt = THUMBNAIL_RECOMMENDATION_PROMPT.format(
            topic=topic,
            title=title,
            niche=niche,
            competitor_styles="\n".join(top_competitor_styles)
        )
        try:
            response = call_openai(
                system_prompt="You are a YouTube thumbnail strategist. Return JSON only.",
                user_prompt=prompt,
                response_format="json"
            )
            return safe_json_loads(response)
        except Exception as e:
            logger.error(f"Thumbnail recommendation failed: {e}")
            return {
                "concept": "",
                "layout": "",
                "recommended_emotion": "",
                "color_palette": [],
                "text_overlay": "",
                "background_style": "",
                "psychological_hook": "",
                "differentiation_from_competitors": ""
            }