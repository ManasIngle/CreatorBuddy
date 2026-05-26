from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    OPENAI_API_KEY: str  # Fallback for embeddings if OpenRouter doesn't support
    OPENROUTER_API_KEY: str  # Primary API key for OpenRouter
    YOUTUBE_API_KEY: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    ENVIRONMENT: str = "development"
    FRONTEND_URL: str = "http://localhost:3000"
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    # OpenRouter model configuration — using free models as of May 2026
    LLM_MODEL: str = "nvidia/nemotron-3-super-120b-a12b:free"  # Default for medium-complexity content gen
    VISION_MODEL: str = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"  # Multimodal: text/image/video
    EMBEDDING_MODEL: str = "openai/text-embedding-3-small"  # Embeddings still go via direct OpenAI
    
    # OpenRouter site info for analytics
    OPENROUTER_SITE_URL: str = "https://creatoriq.app"
    OPENROUTER_SITE_NAME: str = "CreatorIQ"

    # ----- MiniMax Token / Coding Plan (paid subscription) -----
    # Uses the OpenAI-compatible endpoint.
    # Token Plan keys are NOT interchangeable with pay-as-you-go keys.
    # Get key from: https://platform.minimax.io → Billing → Token Plan
    MINIMAX_API_KEY: Optional[str] = None
    MINIMAX_BASE_URL: str = "https://api.minimax.io/v1"
    MINIMAX_MODEL: str = "MiniMax-M2.7"     # flagship coding/reasoning model
    MINIMAX_MODEL_FAST: str = "MiniMax-M2"  # cheaper sibling for medium-tier

    class Config:
        env_file = ".env"

settings = Settings()