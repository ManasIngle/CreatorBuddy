from typing import List, Dict
from sqlalchemy.orm import Session
from app.models.video import Video
from app.models.hook import Hook
from app.models.channel import Channel
from app.services.openrouter_service import call_openai, safe_json_loads
from app.prompts.script_prompts import HOOK_ANALYSIS_PROMPT
from app.prompts.hook_prompts import HOOK_GENERATION_PROMPT
from app.services.context_optimizer import truncate_to_token_limit
import logging

logger = logging.getLogger(__name__)


class HookEngine:

    def analyze_viral_hooks(self, channel: Channel, db: Session) -> List[Dict]:
        """
        Analyzes viral hooks with optimized context.
        Uses hook excerpts only (already short) with reduced count.
        """
        # Get viral videos - reduced limit
        viral_videos = db.query(Video).filter(
            Video.channel_id == channel.id,
            Video.is_viral == True,
            Video.hook_text != None
        ).order_by(Video.view_count.desc()).limit(10).all()  # Reduced from 20 to 10

        if len(viral_videos) < 3:
            return []

        # Use hook excerpts only - they're already short (first 30 seconds)
        hooks = [v.hook_text for v in viral_videos if v.hook_text][:8]  # Reduced from 10 to 8
        
        # Truncate hooks if needed (shouldn't be needed as they're already excerpts)
        hooks_text = "\n---\n".join(hooks)
        hooks_text = truncate_to_token_limit(hooks_text, 1500)

        prompt = HOOK_ANALYSIS_PROMPT.format(
            count=len(hooks),
            niche=channel.niche or "general",
            hooks=hooks_text
        )

        try:
            response = call_openai(
                system_prompt="You are a YouTube retention expert. Return JSON only. Be concise.",
                user_prompt=prompt,
                response_format="json",
                complexity="medium"
            )
            data = safe_json_loads(response)
            return data.get("patterns", [])
        except Exception as e:
            logger.error(f"Viral hook analysis failed: {e}")
            return []

    def generate_hooks_for_topic(
        self,
        topic: str,
        channel: Channel,
        count: int = 5
    ) -> List[Dict]:
        """Generate multiple hook variations for a given topic."""
        prompt = HOOK_GENERATION_PROMPT.format(
            topic=topic,
            niche=channel.niche or "general",
            creator_style=channel.speaking_style or "conversational",
            count=count
        )
        try:
            response = call_openai(
                system_prompt="You are a hook writing expert. Return JSON only.",
                user_prompt=prompt,
                response_format="json",
                complexity="medium"
            )
            data = safe_json_loads(response)
            return data.get("hooks", [])
        except Exception as e:
            logger.error(f"Hook generation failed: {e}")
            return []