from typing import List, Optional
from app.services.openrouter_service import get_embedding as openai_get_embedding
import logging

logger = logging.getLogger(__name__)

def get_content_embedding(text: str) -> List[float]:
    """
    Generate embedding for content similarity search.
    Uses OpenAI's text-embedding-3-small model.
    """
    try:
        return openai_get_embedding(text)
    except Exception as e:
        logger.error(f"Failed to generate content embedding: {e}")
        # Return zero vector as fallback
        return [0.0] * 1536

def compute_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """
    Compute cosine similarity between two embeddings.
    """
    if not embedding1 or not embedding2:
        return 0.0
    
    dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
    magnitude1 = sum(a * a for a in embedding1) ** 0.5
    magnitude2 = sum(b * b for b in embedding2) ** 0.5
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)

def find_similar_content(
    query_embedding: List[float],
    content_embeddings: List[List[float]],
    threshold: float = 0.7
) -> List[int]:
    """
    Find indices of content with similarity above threshold.
    
    Args:
        query_embedding: The embedding to compare against
        content_embeddings: List of embeddings to search
        threshold: Minimum similarity score (0-1)
    
    Returns:
        List of indices where similarity >= threshold
    """
    similar_indices = []
    for i, content_emb in enumerate(content_embeddings):
        similarity = compute_similarity(query_embedding, content_emb)
        if similarity >= threshold:
            similar_indices.append(i)
    return similar_indices