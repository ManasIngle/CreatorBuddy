"""
DEPRECATED: Legacy OpenAI service.
All new code should use openrouter_service.py instead.
This file is kept for backward compatibility only.

Import from openrouter_service:
    from app.services.openrouter_service import call_openai, safe_json_loads, get_embedding
"""

# Re-export from the canonical service for backward compatibility
from app.services.openrouter_service import (
    call_openai,
    call_openai_vision,
    get_embedding,
    safe_json_loads,
)

import warnings
import logging

logger = logging.getLogger(__name__)

# Warn on import so developers know to update their imports
warnings.warn(
    "openai_service is deprecated. Use openrouter_service instead.",
    DeprecationWarning,
    stacklevel=2
)
logger.warning("DEPRECATION: openai_service.py imported — migrate to openrouter_service.py")