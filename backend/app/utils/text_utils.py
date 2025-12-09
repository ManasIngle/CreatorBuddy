import re
from typing import List

def truncate_text(text: str, max_length: int = 1000) -> str:
    """Truncate text to a maximum length, adding ellipsis if truncated."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def clean_title(title: str) -> str:
    """Clean a YouTube video title by removing special characters and extra whitespace."""
    title = re.sub(r'[^\w\s\-:,|]', '', title)
    title = re.sub(r'\s+', ' ', title)
    return title.strip()

def extract_video_id_from_url(url: str) -> str:
    """
    Extract YouTube video ID from various URL formats.
    Supports: youtube.com/watch?v=, youtu.be/, youtube.com/embed/
    """
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/channel/([a-zA-Z0-9_-]{24})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return url

def parse_duration_to_seconds(duration: str) -> int:
    """Convert ISO 8601 duration to seconds. e.g. PT1H2M3S -> 3723"""
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    match = re.match(pattern, duration)
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds

def format_number(num: int) -> str:
    """Format large numbers with K/M suffixes."""
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    if num >= 1_000:
        return f"{num / 1_000:.1f}K"
    return str(num)

def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from text."""
    return re.findall(r'#(\w+)', text)

def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')