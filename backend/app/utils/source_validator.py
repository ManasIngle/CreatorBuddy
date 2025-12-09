"""
Source Validator for Scraped Content
Validates the quality and reliability of scraped content
"""

from typing import Optional, Dict, List
from dataclasses import dataclass
import re
from datetime import datetime


@dataclass
class ValidationResult:
    is_valid: bool
    quality_score: float  # 0.0 to 1.0
    issues: List[str]
    source_type: str
    content_summary: str


class SourceValidator:
    """
    Validates scraped content for quality, relevance, and reliability.
    Ensures scraped data meets minimum quality thresholds.
    """
    
    # Minimum content length for various source types
    MIN_CONTENT_LENGTH = {
        "article": 500,
        "discussion": 200,
        "social": 50,
        "default": 100
    }
    
    # Known high-quality sources
    HIGH_QUALITY_DOMAINS = [
        "wikipedia.org",
        "reddit.com",
        "medium.com",
        "github.com",
        "stackoverflow.com",
        "quora.com",
        "news.google.com"
    ]
    
    # Spam/low-quality indicators
    SPAM_PATTERNS = [
        r"click here",
        r"buy now",
        r"limited time offer",
        r"act now",
        r"free money",
        r"make \$\d+",
        r"weight loss.*guaranteed",
        r"earn.*income.*home"
    ]
    
    def validate_content(
        self,
        content: str,
        source_url: str,
        source_type: str = "default"
    ) -> ValidationResult:
        """
        Validate scraped content for quality.
        
        Returns ValidationResult with:
        - is_valid: Whether content meets minimum quality
        - quality_score: 0.0 to 1.0 quality rating
        - issues: List of identified issues
        - source_type: Detected or provided source type
        - content_summary: Brief summary of content
        """
        issues = []
        min_length = self.MIN_CONTENT_LENGTH.get(source_type, self.MIN_CONTENT_LENGTH["default"])
        
        # Check content length
        if len(content) < min_length:
            issues.append(f"Content too short: {len(content)} chars (min: {min_length})")
        
        # Detect spam patterns
        content_lower = content.lower()
        for pattern in self.SPAM_PATTERNS:
            if re.search(pattern, content_lower):
                issues.append(f"Potential spam detected: pattern '{pattern}' found")
        
        # Check for gibberish/nonsense (very low entropy)
        if self._is_gibberish(content):
            issues.append("Content appears to be gibberish or unreadable")
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(content, source_url, issues)
        
        # Determine source type if not provided
        detected_type = source_type if source_type != "default" else self._detect_source_type(source_url)
        
        # Generate content summary
        content_summary = self._generate_summary(content)
        
        # Content is valid if quality score is above threshold
        is_valid = quality_score >= 0.3 and len(content) >= min_length // 2
        
        return ValidationResult(
            is_valid=is_valid,
            quality_score=quality_score,
            issues=issues,
            source_type=detected_type,
            content_summary=content_summary
        )
    
    def _calculate_quality_score(
        self,
        content: str,
        source_url: str,
        issues: List[str]
    ) -> float:
        """Calculate overall quality score"""
        score = 1.0
        
        # Deduct for issues
        score -= len(issues) * 0.1
        
        # Length factor (normalize to 0-0.3 range)
        length_factor = min(len(content) / 2000, 1.0) * 0.3
        score += length_factor
        
        # Source quality factor
        for domain in self.HIGH_QUALITY_DOMAINS:
            if domain in source_url.lower():
                score += 0.2
                break
        
        # Sentence structure factor (good content has varied sentence lengths)
        sentences = content.split('.')
        if len(sentences) > 5:
            score += 0.1
        
        # Penalize for excessive special characters
        special_char_ratio = sum(1 for c in content if c in '!?@#$%') / max(len(content), 1)
        if special_char_ratio > 0.1:
            score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    def _is_gibberish(self, content: str) -> bool:
        """Detect if content is gibberish"""
        if len(content) < 50:
            return False
        
        # Check for keyboard patterns
        keyboard_patterns = [
            r"asdfghjkl",
            r"qwertyuiop",
            r"zxcvbnm"
        ]
        
        for pattern in keyboard_patterns:
            if pattern in content.lower():
                return True
        
        # Check for excessive repetition
        words = content.lower().split()
        if len(words) > 10:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.3:
                return True
        
        # Check for letter-only content (usually not meaningful)
        if re.match(r'^[a-zA-Z\s]+$', content):
            # But too short words might indicate gibberish
            avg_word_length = sum(len(w) for w in words) / max(len(words), 1)
            if avg_word_length < 2:
                return True
        
        return False
    
    def _detect_source_type(self, url: str) -> str:
        """Detect the type of source from URL"""
        url_lower = url.lower()
        
        if any(domain in url_lower for domain in ["reddit.com", "reddit.com"]):
            return "discussion"
        elif any(domain in url_lower for domain in ["quora.com", "stackoverflow.com"]):
            return "discussion"
        elif any(domain in url_lower for domain in ["medium.com", "blog", "article"]):
            return "article"
        elif any(domain in url_lower for domain in ["twitter.com", "x.com"]):
            return "social"
        elif any(domain in url_lower for domain in ["youtube.com"]):
            return "video"
        elif any(domain in url_lower for domain in ["wikipedia.org"]):
            return "reference"
        elif any(domain in url_lower for domain in ["news.google.com", "news."]):
            return "news"
        
        return "general"
    
    def _generate_summary(self, content: str, max_length: int = 200) -> str:
        """Generate a brief summary of content"""
        if len(content) <= max_length:
            return content
        
        # Try to get first sentence within limit
        sentences = content.split('.')
        summary = ""
        
        for sentence in sentences:
            if len(summary) + len(sentence) <= max_length:
                summary += sentence + "."
            else:
                break
        
        if not summary:
            summary = content[:max_length] + "..."
        
        return summary.strip()
    
    def batch_validate(
        self,
        contents: List[Dict],
        source_type: str = "default"
    ) -> List[ValidationResult]:
        """
        Validate multiple content items.
        
        Expected format for contents:
        [{"content": str, "url": str}, ...]
        """
        results = []
        
        for item in contents:
            content = item.get("content", "")
            url = item.get("url", "")
            
            result = self.validate_content(content, url, source_type)
            results.append(result)
        
        return results
    
    def get_best_sources(
        self,
        contents: List[Dict],
        min_quality: float = 0.5,
        source_type: str = "default"
    ) -> List[Dict]:
        """
        Filter and return only high-quality sources.
        
        Returns list of content items that pass validation,
        sorted by quality score descending.
        """
        results = self.batch_validate(contents, source_type)
        
        validated = []
        for i, result in enumerate(results):
            if result.is_valid and result.quality_score >= min_quality:
                validated.append({
                    **contents[i],
                    "quality_score": result.quality_score,
                    "source_type": result.source_type
                })
        
        # Sort by quality score
        validated.sort(key=lambda x: x.get("quality_score", 0), reverse=True)
        
        return validated


# Global validator instance
source_validator = SourceValidator()