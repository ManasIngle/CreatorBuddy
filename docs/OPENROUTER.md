# OpenRouter Integration

CreatorIQ uses [OpenRouter](https://openrouter.ai/) as the unified API gateway for large language model (LLM) integrations, replacing direct OpenAI API calls.

## Why OpenRouter?

### Cost Flexibility

OpenRouter aggregates models from multiple providers (OpenAI, Anthropic, Meta, Mistral, Google) under a single API. This enables:

- **Pay-per-token pricing** from multiple providers in one place
- **Automatic fallback** if one provider has issues
- **Model diversity** without managing multiple API keys
- **Unified billing** through OpenRouter

### Cost Savings

| Model | Provider | Input $/1M | Output $/1M |
|-------|----------|-------------|-------------|
| GPT-4o-mini | OpenAI | $0.15 | $0.60 |
| Claude-3-haiku | Anthropic | $0.25 | $1.25 |
| Llama 3 8B | Meta | $0.20 | $0.20 |
| GPT-4o | OpenAI | $2.50 | $10.00 |

By routing simple tasks to cheaper models (Llama 3), we reduce costs by ~90% compared to using GPT-4o for everything.

## Architecture

```
┌─────────────────┐
│  FastAPI Backend │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ openrouter_service│ ◄── Single import point
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   OpenRouter    │ ◄── Unified API
│   API Gateway   │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
┌──────┐ ┌───────┐ ┌─────────┐ ┌───────┐
│OpenAI│ │Anthropic│ │  Meta  │ │Mistral│
│ GPT-4│ │Claude  │ │ Llama 3│ │Mixtral│
└──────┘ └───────┘ └─────────┘ └───────┘
```

## Available Models

### Text Generation Models

| Model ID | Provider | Best For | Complexity |
|----------|----------|----------|------------|
| `openai/gpt-4o-mini` | OpenAI | Default for most tasks | medium |
| `openai/gpt-4o` | OpenAI | Complex reasoning, creative | complex |
| `anthropic/claude-3-haiku` | Anthropic | Vision tasks, fast responses | simple |
| `anthropic/claude-3-sonnet` | Anthropic | Balance of capability and speed | medium |
| `meta-llama/llama-3-8b-instruct` | Meta | Simple transformations, classification | simple |
| `mistralai/mixtral-8x7b` | Mistral | Code, technical tasks | medium |
| `google/gemini-pro` | Google | Multimodal tasks | medium |

### Vision Models

| Model ID | Provider | Best For |
|----------|----------|----------|
| `anthropic/claude-3-haiku` | Anthropic | Thumbnail analysis (recommended) |
| `openai/gpt-4o` | OpenAI | High-detail vision analysis |

## Model Routing

The [`openrouter_service.py`](backend/app/services/openrouter_service.py) provides automatic model selection based on task complexity:

### Complexity Levels

```python
from app.services.openrouter_service import call_openai

# Simple: Uses Llama 3 8B
# Fast, cheap - ideal for:
# - Text formatting and transformations
# - Simple classifications
# - Basic sentiment detection
result = call_openai(system_prompt, user_prompt, complexity="simple")

# Medium: Uses GPT-4o-mini (default)
# Balanced - ideal for:
# - Content gap analysis
# - Hook suggestions
# - Audience insights
result = call_openai(system_prompt, user_prompt, complexity="medium")

# Complex: Uses GPT-4o
# Premium - ideal for:
# - Nuanced content analysis
# - Creative script generation
# - Multi-step reasoning
result = call_openai(system_prompt, user_prompt, complexity="complex")
```

### Direct Model Specification

For specific model requirements:

```python
from app.services.openrouter_service import call_openai

# Use a specific model
result = call_openai(
    system_prompt,
    user_prompt,
    model="anthropic/claude-3-haiku"
)
```

## Environment Variables

```bash
# Required
OPENROUTER_API_KEY=sk-or-your-openrouter-api-key

# Model configuration (defaults shown)
LLM_MODEL=openai/gpt-4o-mini          # Default text generation
VISION_MODEL=anthropic/claude-3-haiku # Vision/image analysis
EMBEDDING_MODEL=openai/gpt-4o-mini    # Text embeddings

# Optional - for OpenRouter dashboard analytics
OPENROUTER_SITE_URL=https://creatoriq.app
OPENROUTER_SITE_NAME=CreatorIQ
```

## API Reference

### call_openai()

Main text generation function.

```python
def call_openai(
    system_prompt: str,
    user_prompt: str,
    model: Optional[str] = None,
    max_tokens: int = 2000,
    response_format: Optional[str] = None,
    complexity: Optional[str] = None
) -> str
```

**Parameters:**
- `system_prompt`: System instructions for the AI
- `user_prompt`: User query or input
- `model`: Specific OpenRouter model ID (e.g., `openai/gpt-4o-mini`)
- `max_tokens`: Maximum response length (default: 2000)
- `response_format`: Set to `"json"` for JSON-structured responses
- `complexity`: `"simple"`, `"medium"`, or `"complex"` for automatic model routing

**Returns:** Raw text response from the model.

### call_openai_vision()

Vision-capable model for image analysis.

```python
def call_openai_vision(
    image_url: str,
    prompt: str,
    model: Optional[str] = None
) -> str
```

**Parameters:**
- `image_url`: URL or base64 data URI of the image
- `prompt`: Text prompt for image analysis
- `model`: Vision model ID (default: `VISION_MODEL` env var)

**Returns:** Text description or analysis of the image.

### call_openai_streaming()

Streaming response for real-time output.

```python
def call_openai_streaming(
    system_prompt: str,
    user_prompt: str,
    model: Optional[str] = None,
    max_tokens: int = 2000,
    callback: Optional[callable] = None
) -> str
```

**Parameters:**
- `callback`: Function called for each streaming chunk

**Returns:** Complete response text.

### get_embedding()

Generate text embeddings for similarity search.

```python
def get_embedding(
    text: str,
    model: Optional[str] = None
) -> list[float]
```

Note: OpenRouter has limited embedding support. Falls back to direct OpenAI API for embeddings.

### get_model_info()

Get cost information for a model.

```python
def get_model_info(model: str) -> dict
```

Returns:
```python
{
    "model": "openai/gpt-4o-mini",
    "estimated_cost_per_1m_tokens": {
        "input": 0.15,
        "output": 0.60
    }
}
```

## Adding New Models

### 1. Update MODEL_COSTS

In [`backend/app/services/openrouter_service.py`](backend/app/services/openrouter_service.py:19):

```python
MODEL_COSTS = {
    # ... existing models ...
    "provider/model-id": (input_cost_per_million, output_cost_per_million),
}
```

### 2. Update Defaults (if needed)

Modify the default model constants:

```python
DEFAULT_LLM_MODEL = "provider/new-default-model"
DEFAULT_VISION_MODEL = "provider/new-vision-model"
```

### 3. Document in This File

Add the model to the tables above with use cases.

## Cost Optimization Tips

1. **Use complexity parameter wisely**
   - Simple tasks don't need premium models
   - Reserve `complex` for tasks requiring nuanced reasoning

2. **Batch when possible**
   - Group similar operations to reduce API calls
   - Use streaming for large outputs when possible

3. **Monitor usage**
   - Check OpenRouter dashboard for spending
   - Use `get_model_info()` for cost estimates before calling

4. **Set token limits appropriately**
   - Don't set `max_tokens=2000` if 200 words is enough
   - Lower limits = lower costs on truncated responses

## Troubleshooting

### API Errors

**"Invalid API key"**
- Verify `OPENROUTER_API_KEY` is correct
- Check key has available credits at openrouter.ai/credits

**"Model not found"**
- Verify model ID matches OpenRouter format (`provider/model-name`)
- Check OpenRouter supported models list

**"Context length exceeded"**
- Reduce input text length
- Consider summarizing long content before sending

### Rate Limiting

OpenRouter has per-minute rate limits based on tier. Implement retry logic:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def call_with_retry(system, user):
    return call_openai(system, user)
```

### Embedding Failures

If embeddings fail via OpenRouter, the service automatically falls back to direct OpenAI API for the embedding request only. This ensures continuity while using OpenRouter for primary LLM calls.

## Further Resources

- [OpenRouter Documentation](https://openrouter.ai/docs)
- [OpenRouter Models List](https://openrouter.ai/models)
- [API Keys Management](https://openrouter.ai/keys)
- [Usage and Billing](https://openrouter.ai/credits)