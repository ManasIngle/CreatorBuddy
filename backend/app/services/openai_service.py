from openai import OpenAI
from typing import Optional, Dict, Any
from app.config import settings
from tenacity import retry, stop_after_attempt, wait_exponential
import json
import logging

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def call_openai(
    system_prompt: str,
    user_prompt: str,
    model: str = "gpt-4o-mini",
    max_tokens: int = 2000,
    response_format: Optional[str] = None
) -> str:
    """
    Central OpenAI call. Uses gpt-4o-mini by default for cost efficiency.
    For response_format="json", adds JSON instruction to system prompt.
    All calls retry up to 3 times with exponential backoff.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    kwargs = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7
    }

    if response_format == "json":
        kwargs["response_format"] = {"type": "json_object"}

    try:
        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        raise

def call_openai_vision(
    image_url: str,
    prompt: str,
    model: str = "gpt-4o"  # Vision requires gpt-4o
) -> str:
    """
    OpenAI vision call for thumbnail analysis.
    Uses gpt-4o (not mini) because vision quality matters.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url, "detail": "high"}
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI vision call failed: {e}")
        raise

def get_embedding(text: str) -> list:
    """
    Generate text embedding for similarity search.
    Used for content gap detection and competitor similarity.
    Model: text-embedding-3-small (1536 dimensions, low cost)
    """
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8000]  # Truncate to avoid token limits
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"OpenAI embedding call failed: {e}")
        raise

def safe_json_loads(response_text: str) -> Dict[str, Any]:
    """
    Safely parse JSON from AI response with error handling.
    Wraps json.loads with try/except for robust parsing.
    """
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        # Try to fix common issues
        cleaned = response_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        try:
            return json.loads(cleaned.strip())
        except json.JSONDecodeError:
            logger.error(f"Failed to parse cleaned JSON: {cleaned[:200]}")
            return {}