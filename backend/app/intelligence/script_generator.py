from typing import Dict, Optional, List
from app.models.channel import Channel
from app.services.openrouter_service import call_openai, safe_json_loads
from app.prompts.script_prompts import (
    SCRIPT_HOOK_PROMPT,
    SCRIPT_OUTLINE_PROMPT,
    FULL_SCRIPT_PROMPT,
    TITLE_SUGGESTIONS_PROMPT
)
import logging

logger = logging.getLogger(__name__)

class ScriptGenerator:

    def generate_titles(self, topic: str, channel: Channel, user_id: Optional[str] = None) -> List[Dict]:
        """Generate title suggestions for a video topic."""
        prompt = TITLE_SUGGESTIONS_PROMPT.format(
            topic=topic,
            niche=channel.niche or "general",
            channel_style=channel.personality_summary or "engaging and educational",
            subscriber_count=channel.subscriber_count
        )
        try:
            response = call_openai(
                system_prompt="You are a YouTube title expert. Return JSON only.",
                user_prompt=prompt,
                response_format="json",
                complexity="simple",
                user_id=user_id,
                operation="script_titles",
            )
            data = safe_json_loads(response)
            return data.get("titles", [])
        except Exception as e:
            logger.error(f"Title generation failed: {e}")
            return []

    def generate_hook(self, topic: str, channel: Channel, title: str, user_id: Optional[str] = None) -> str:
        """Generate a hook for the given topic and title."""
        prompt = SCRIPT_HOOK_PROMPT.format(
            topic=topic,
            title=title,
            niche=channel.niche or "general",
            creator_style=channel.speaking_style or "conversational",
            storytelling_structure=channel.storytelling_structure or "problem-solution"
        )
        try:
            return call_openai(
                system_prompt="You are an expert at writing viral YouTube hooks. Write the hook only, no preamble.",
                user_prompt=prompt,
                complexity="simple",
                user_id=user_id,
                operation="script_hook",
            )
        except Exception as e:
            logger.error(f"Hook generation failed: {e}")
            return ""

    def generate_full_script(
        self,
        topic: str,
        title: str,
        hook: str,
        channel: Channel,
        target_duration_minutes: int = 10,
        format_type: str = "educational",
        user_id: Optional[str] = None,
    ) -> Dict[str, str]:
        """Generate a full script with the given parameters."""
        prompt = FULL_SCRIPT_PROMPT.format(
            topic=topic,
            title=title,
            hook=hook,
            niche=channel.niche or "general",
            creator_personality=channel.personality_summary or "engaging and informative",
            speaking_style=channel.speaking_style or "conversational",
            storytelling_structure=channel.storytelling_structure or "problem-solution",
            target_duration=target_duration_minutes,
            format_type=format_type,
            audience_type=channel.audience_type or "general audience"
        )
        try:
            script_text = call_openai(
                system_prompt="You are a professional YouTube scriptwriter. Write complete, detailed scripts.",
                user_prompt=prompt,
                max_tokens=4000,
                complexity="complex",
                user_id=user_id,
                operation="script_full",
            )
            return {
                "full_script": script_text,
                "estimated_duration": f"{target_duration_minutes} minutes"
            }
        except Exception as e:
            logger.error(f"Full script generation failed: {e}")
            return {
                "full_script": "",
                "estimated_duration": f"{target_duration_minutes} minutes"
            }