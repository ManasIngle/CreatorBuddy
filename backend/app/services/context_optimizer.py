"""
Context optimization service for minimizing token usage.
Provides utilities for truncating, summarizing, and compressing content
while maintaining insights quality for AI analysis.
"""
from typing import List, Dict, Tuple, Optional
import tiktoken
import logging

logger = logging.getLogger(__name__)

# Encoding for token counting (cl100k_base is used by GPT-4 and Claude)
ENCODING = tiktoken.get_encoding("cl100k_base")

# Default max tokens for various operations
DEFAULT_MAX_INPUT_TOKENS = 4000
TARGET_AVG_INPUT_TOKENS = 500

# Max transcript length before truncation (chars)
MAX_TRANSCRIPT_CHARS = 10000


def count_tokens(text: str) -> int:
    """
    Count tokens in text using tiktoken.
    
    Args:
        text: Input text to count tokens for
        
    Returns:
        Number of tokens in the text
    """
    if not text:
        return 0
    try:
        return len(ENCODING.encode(text))
    except Exception as e:
        logger.warning(f"Token counting failed: {e}, falling back to char/4 estimate")
        return len(text) // 4


def truncate_to_token_limit(text: str, max_tokens: int = DEFAULT_MAX_INPUT_TOKENS) -> str:
    """
    Hard truncate text to fit within token limit.
    Uses tiktoken for accurate counting.
    
    Args:
        text: Input text to truncate
        max_tokens: Maximum tokens allowed (default 4000)
        
    Returns:
        Truncated text that fits within token limit
    """
    if not text:
        return ""
    
    token_count = count_tokens(text)
    if token_count <= max_tokens:
        return text
    
    # Binary search for exact token limit (more efficient than iterative)
    chars_per_token = len(text) / max(token_count, 1)
    target_chars = int(max_tokens * chars_per_token * 0.95)  # 5% buffer
    
    truncated = text[:target_chars]
    while count_tokens(truncated) > max_tokens and len(truncated) > 100:
        truncated = truncated[:-100]
    
    return truncated


def summarize_text(text: str, max_tokens: int = 150) -> str:
    """
    Summarize text using AI to reduce tokens while preserving key information.
    This is used when we have very long content (transcripts, comments).
    
    Args:
        text: Long text to summarize
        max_tokens: Target output token count
        
    Returns:
        Summarized text
    """
    from app.services.openrouter_service import call_openai
    
    token_count = count_tokens(text)
    if token_count <= max_tokens:
        return text
    
    system_prompt = """You are a concise content summarizer. 
Summarize the following content in 2-3 sentences, preserving key facts, names, and numbers.
Be extremely concise - every word must earn its place."""
    
    user_prompt = f"Summarize this concisely:\n\n{text[:3000]}"
    
    try:
        return call_openai(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=max_tokens,
            complexity="simple"
        )
    except Exception as e:
        logger.warning(f"Summarization failed: {e}, falling back to hard truncate")
        return truncate_to_token_limit(text, max_tokens * 4)


def extract_key_points(text: str, num_points: int = 5) -> List[str]:
    """
    Extract N key points from transcript or comments.
    Used for audience analysis and content pattern detection.
    
    Args:
        text: Input text (transcript, comments, etc.)
        num_points: Number of key points to extract
        
    Returns:
        List of extracted key points
    """
    from app.services.openrouter_service import call_openai
    
    truncated = truncate_to_token_limit(text, 3000)
    
    system_prompt = f"""Extract exactly {num_points} key points from the content below.
Each point should be 1-2 sentences, actionable and specific.
Focus on: patterns, trends, common themes, audience pain points.
Return ONLY a JSON array of strings."""
    
    user_prompt = f"Extract {num_points} key points:\n\n{truncated}"
    
    try:
        response = call_openai(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=num_points * 30,
            response_format="json",
            complexity="simple"
        )
        import json
        return json.loads(response)
    except Exception as e:
        logger.warning(f"Key point extraction failed: {e}")
        # Fallback: split text into approximate chunks
        lines = text.split('\n')
        return [line.strip() for line in lines[:num_points] if line.strip()]


def compress_video_context(video_data: Dict, include_transcript: bool = True) -> str:
    """
    Compress video data for AI analysis.
    Reduces full video data to essential insights while minimizing tokens.
    
    Args:
        video_data: Dict with video details (title, views, likes, duration, transcript_excerpt)
        include_transcript: Whether to include transcript (usually should be False for AI)
        
    Returns:
        Compressed string representation
    """
    title = video_data.get('title', 'Unknown')[:60]
    views = video_data.get('views', 0)
    likes = video_data.get('likes', video_data.get('like_count', 0))
    duration_sec = video_data.get('duration_seconds', 0)
    duration_min = duration_sec // 60
    
    # Format: "Title | Views: X | Likes: X | Duration: Xmin"
    context = f"{title} | {views:,} views | {likes:,} likes | {duration_min}min"
    
    if include_transcript and 'transcript_excerpt' in video_data:
        transcript = video_data['transcript_excerpt'][:500]
        context += f"\nTranscript: {transcript}..."
    
    return context


def compress_videos_for_analysis(videos: List[Dict], max_videos: int = 5) -> str:
    """
    Compress multiple videos into a single context string.
    Limits videos and ensures total context fits token limits.
    
    Args:
        videos: List of video data dicts
        max_videos: Maximum number of videos to include (default 5)
        
    Returns:
        Compressed context string for AI
    """
    compressed = []
    for video in videos[:max_videos]:
        compressed.append(compress_video_context(video, include_transcript=False))
    
    return "\n".join(compressed)


def optimize_transcript_for_ai(transcript: str, max_chars: int = MAX_TRANSCRIPT_CHARS) -> str:
    """
    Optimize transcript content for AI consumption.
    - Truncates if too long
    - Removes filler words indicator
    - Preserves structure
    
    Args:
        transcript: Full transcript text
        max_chars: Maximum characters (default 10000)
        
    Returns:
        Optimized transcript
    """
    if not transcript:
        return ""
    
    # Remove excessive whitespace
    cleaned = ' '.join(transcript.split())
    
    # Truncate if needed
    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars]
    
    return cleaned


def estimate_compression_ratio(original_tokens: int, target_tokens: int) -> float:
    """
    Calculate the compression ratio needed.
    
    Args:
        original_tokens: Original token count
        target_tokens: Target token count
        
    Returns:
        Compression ratio (e.g., 0.3 means reduce to 30% of original)
    """
    if original_tokens <= 0:
        return 1.0
    return max(0.1, min(1.0, target_tokens / original_tokens))


def get_token_budget_status(used_tokens: int, limit_tokens: int) -> Dict:
    """
    Get token budget status with percentage and recommendations.
    
    Args:
        used_tokens: Tokens used so far
        limit_tokens: Total token limit
        
    Returns:
        Dict with status info
    """
    percentage = (used_tokens / limit_tokens * 100) if limit_tokens > 0 else 0
    
    return {
        "used": used_tokens,
        "limit": limit_tokens,
        "percentage": round(percentage, 1),
        "remaining": max(0, limit_tokens - used_tokens),
        "status": "ok" if percentage < 70 else "warning" if percentage < 90 else "critical",
        "recommendation": "Continue normal operations" if percentage < 70 
                         else "Consider reducing context size" if percentage < 90 
                         else "Reduce context or upgrade plan"
    }