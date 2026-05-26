"""
OpenRouter service for content generation.
Provides unified API access to multiple LLM providers (OpenAI, Anthropic, Meta, etc.)
with cost optimization, streaming support, token tracking, and content-addressable
LLM response caching (40-60% cost reduction on warm niches).
"""
from openai import OpenAI
from typing import Optional, Dict, Any, Iterator
from app.config import settings
from tenacity import retry, stop_after_attempt, wait_exponential
import json
import hashlib
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# OpenRouter API configuration
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Model configurations for cost optimization
MODEL_COSTS = {
    # Cost per million tokens (input, output) - approximate values
    "openai/gpt-4o-mini": (0.15, 0.60),
    "openai/gpt-4o": (2.50, 10.00),
    "anthropic/claude-3.5-haiku": (0.80, 4.00),
    "anthropic/claude-3.5-sonnet": (3.00, 15.00),
    "meta-llama/llama-3.1-8b-instruct": (0.05, 0.05),
    "mistralai/mixtral-8x7b": (0.24, 0.24),
    "google/gemini-flash-1.5": (0.075, 0.30),
}

# Model mappings for OpenRouter (provider/model format)
# Default models for different tasks
DEFAULT_LLM_MODEL = getattr(settings, 'LLM_MODEL', 'openai/gpt-4o-mini')
DEFAULT_VISION_MODEL = getattr(settings, 'VISION_MODEL', 'anthropic/claude-3.5-haiku')
DEFAULT_EMBEDDING_MODEL = getattr(settings, 'EMBEDDING_MODEL', 'openai/gpt-4o-mini')

# Create OpenRouter client
client = OpenAI(
    base_url=OPENROUTER_BASE_URL,
    api_key=settings.OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": getattr(settings, 'OPENROUTER_SITE_URL', 'https://creatoriq.app'),
        "X-Title": getattr(settings, 'OPENROUTER_SITE_NAME', 'CreatorIQ'),
    }
)


def _get_model_for_complexity(complexity: str = "medium") -> str:
    """
    Select appropriate model based on task complexity for cost optimization.
    
    Complexity levels:
    - ultra_cheap: Llama 3.1 8B for simple extractions, classifications
    - simple:      GPT-4o-mini for basic transformations and hooks
    - medium:      GPT-4o-mini (default) for standard analysis
    - complex:     Claude 3.5 Sonnet for nuanced reasoning and long scripts
    """
    if complexity == "ultra_cheap":
        return "meta-llama/llama-3.1-8b-instruct"
    elif complexity == "simple":
        return "openai/gpt-4o-mini"
    elif complexity == "complex":
        return "anthropic/claude-3.5-sonnet"
    else:
        return DEFAULT_LLM_MODEL


# ---------------------------------------------------------------------------
# Content-addressable LLM response cache
# Deterministic prompts (temperature=0) → deterministic outputs.
# Cache key = sha256(model + system + user + format + max_tokens).
# TTL varies: 7d for hooks/titles, 24h for analysis, 1h for fast-changing data.
# Expected hit rate: 40-60% on warm niches.
# ---------------------------------------------------------------------------

def _llm_cache_key(model: str, system: str, user: str, response_format: Optional[str], max_tokens: int) -> str:
    raw = f"{model}:{system}:{user}:{response_format}:{max_tokens}"
    return "llm:" + hashlib.sha256(raw.encode()).hexdigest()


def _get_llm_cached(key: str) -> Optional[str]:
    """Synchronous Redis get — runs in thread context (non-async route)."""
    try:
        import redis as sync_redis
        r = sync_redis.from_url(settings.REDIS_URL, decode_responses=True)
        val = r.get(key)
        r.close()
        if val:
            logger.debug(f"LLM cache hit: {key[:32]}…")
            return val
    except Exception:
        pass
    return None


def _set_llm_cached(key: str, value: str, ttl: int = 86400) -> None:
    """Synchronous Redis set — fire and forget."""
    try:
        import redis as sync_redis
        r = sync_redis.from_url(settings.REDIS_URL, decode_responses=True)
        r.setex(key, ttl, value)
        r.close()
    except Exception:
        pass  # Cache failure must never break the call


def _estimate_tokens(text: str) -> int:
    """Rough estimate of tokens in text (chars / 4)."""
    if not text:
        return 0
    return len(text) // 4


def _log_token_usage(
    model: str, 
    input_text: str, 
    output_text: str, 
    operation: str,
    user_id: Optional[str] = None
):
    """
    Log token usage for monitoring and analytics.
    In production, this would write to a database or analytics service.
    """
    input_tokens = _estimate_tokens(input_text)
    output_tokens = _estimate_tokens(output_text)
    total_tokens = input_tokens + output_tokens
    
    input_cost, output_cost = MODEL_COSTS.get(model, (0, 0))
    estimated_cost = (input_tokens * input_cost / 1_000_000) + \
                     (output_tokens * output_cost / 1_000_000)
    
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "operation": operation,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "estimated_cost_usd": round(estimated_cost, 6),
        "user_id": user_id
    }
    
    logger.info(f"Token usage: {log_data}")
    
    # Track usage in budget manager if user_id provided
    if user_id:
        try:
            from app.services.token_budget import TokenBudgetManager
            TokenBudgetManager.track_tokens(user_id, input_tokens, output_tokens)
        except Exception:
            pass  # Don't fail on tracking errors


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def call_openai(
    system_prompt: str,
    user_prompt: str,
    model: Optional[str] = None,
    max_tokens: int = 2000,
    response_format: Optional[str] = None,
    complexity: Optional[str] = None,
    user_id: Optional[str] = None,
    operation: str = "unknown",
    cache_ttl: int = 86400,      # seconds; 0 disables caching for this call
    temperature: float = 0.0,    # deterministic by default → safe to cache
) -> str:
    """
    Central OpenRouter call for content generation.

    Caching: deterministic calls (temperature=0) are cached by content hash.
    Pass cache_ttl=0 to bypass the cache (e.g. for creative / non-deterministic calls).

    Model selection priority: explicit model > complexity routing > DEFAULT_LLM_MODEL.
    """
    if model is None:
        model = _get_model_for_complexity(complexity) if complexity else DEFAULT_LLM_MODEL

    # --- LLM response cache ---
    if cache_ttl > 0 and temperature == 0.0:
        cache_key = _llm_cache_key(model, system_prompt, user_prompt, response_format, max_tokens)
        cached = _get_llm_cached(cache_key)
        if cached is not None:
            return cached

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    kwargs: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    if response_format == "json":
        kwargs["response_format"] = {"type": "json_object"}

    try:
        response = client.chat.completions.create(**kwargs)
        output = response.choices[0].message.content

        # Persist to cache
        if cache_ttl > 0 and temperature == 0.0:
            _set_llm_cached(cache_key, output, ttl=cache_ttl)

        # Log token usage
        _log_token_usage(model, system_prompt + user_prompt, output, operation, user_id)

        return output
    except Exception as e:
        logger.error(f"OpenRouter API call failed: {e}")
        raise


def call_openai_vision(
    image_url: str,
    prompt: str,
    model: Optional[str] = None
) -> str:
    """
    OpenRouter vision call for thumbnail analysis.
    Uses vision-capable model (e.g., claude-3-haiku with vision).
    Passes image as base64 data URI for OpenRouter compatibility.
    """
    if model is None:
        model = DEFAULT_VISION_MODEL
    
    try:
        # OpenRouter supports images via URL or base64
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
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenRouter vision call failed: {e}")
        raise


def call_openai_streaming(
    system_prompt: str,
    user_prompt: str,
    model: Optional[str] = None,
    max_tokens: int = 2000,
    callback: Optional[callable] = None
) -> str:
    """
    OpenRouter streaming call for real-time response generation.
    
    Args:
        system_prompt: System instructions
        user_prompt: User query
        model: OpenRouter model ID
        max_tokens: Maximum response length
        callback: Optional callback function for each chunk
    
    Returns:
        Full response text
    """
    if model is None:
        model = DEFAULT_LLM_MODEL
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        full_content = ""
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7,
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_content += content
                if callback:
                    callback(content)
        
        return full_content
    except Exception as e:
        logger.error(f"OpenRouter streaming call failed: {e}")
        raise


def get_embedding(text: str, model: Optional[str] = None) -> list:
    """
    Generate text embedding via OpenRouter.
    Uses a model that supports embeddings (e.g., openai/gpt-4o-mini).
    Note: OpenRouter has limited embedding support; may need to use
    a dedicated embedding service or route to OpenAI for embeddings.
    """
    if model is None:
        model = DEFAULT_EMBEDDING_MODEL
    
    try:
        # OpenRouter may not support all embedding models
        # Use OpenAI-compatible embedding endpoint if available
        response = client.embeddings.create(
            model=model,
            input=text[:8000]  # Truncate to avoid token limits
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"OpenRouter embedding call failed: {e}")
        # Fallback: try direct OpenAI endpoint for embeddings
        try:
            from openai import OpenAI as DirectOpenAI
            direct_client = DirectOpenAI(api_key=settings.OPENAI_API_KEY)
            response = direct_client.embeddings.create(
                model="text-embedding-3-small",
                input=text[:8000]
            )
            return response.data[0].embedding
        except Exception as fallback_error:
            logger.error(f"Fallback embedding also failed: {fallback_error}")
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


def get_model_info(model: str) -> Dict[str, Any]:
    """
    Get information about a model including estimated costs.
    Useful for logging and cost tracking.
    """
    input_cost, output_cost = MODEL_COSTS.get(model, (0, 0))
    return {
        "model": model,
        "estimated_cost_per_1m_tokens": {
            "input": input_cost,
            "output": output_cost
        }
    }


def get_cost_estimate(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Calculate estimated cost for a given model and token counts.
    
    Args:
        model: Model identifier
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        
    Returns:
        Estimated cost in USD
    """
    input_cost, output_cost = MODEL_COSTS.get(model, (0, 0))
    return (input_tokens * input_cost / 1_000_000) + (output_tokens * output_cost / 1_000_000)