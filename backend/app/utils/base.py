"""
Base Classes for CreatorIQ Platform
Provides shared functionality to reduce code duplication across services and routers.
"""

from typing import Optional, List, Any, Dict
from datetime import datetime
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseService(ABC):
    """
    Abstract base class for services.
    Provides common functionality like logging and error handling.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def log_error(self, message: str, error: Exception = None):
        """Log error with context."""
        if error:
            self.logger.error(f"{message}: {str(error)}")
        else:
            self.logger.error(message)
    
    def log_info(self, message: str):
        """Log info message."""
        self.logger.info(message)


class BaseRouter:
    """
    Shared router utilities for reducing duplication.
    Not a true base class (FastAPI routers don't inherit well),
    but provides static methods for common patterns.
    """
    
    @staticmethod
    def paginate_query(query, page: int = 1, page_size: int = 50):
        """
        Apply pagination to a SQLAlchemy query.
        
        Args:
            query: SQLAlchemy query object
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Tuple of (query with pagination applied, total count)
        """
        offset = (page - 1) * page_size
        total = query.count()
        return query.offset(offset).limit(page_size), total
    
    @staticmethod
    def build_pagination_response(
        items: List[Any],
        total: int,
        page: int,
        page_size: int,
        url_builder: callable = None
    ) -> Dict[str, Any]:
        """
        Build standardized pagination response.
        
        Args:
            items: List of items for current page
            total: Total number of items
            page: Current page number
            page_size: Items per page
            url_builder: Optional function(page) -> URL string
            
        Returns:
            Dict with items, pagination metadata
        """
        total_pages = (total + page_size - 1) // page_size
        
        response = {
            "items": items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
        
        if url_builder:
            response["pagination"]["next"] = url_builder(page + 1) if page < total_pages else None
            response["pagination"]["prev"] = url_builder(page - 1) if page > 1 else None
        
        return response


class BaseModelMixin:
    """
    Mixin class for shared model functionality.
    Not meant to be used directly - models should inherit from this.
    """
    
    @classmethod
    def get_column_names(cls) -> List[str]:
        """Get all column names for a model."""
        return [c.name for c in cls.__table__.columns]
    
    def to_dict(self, exclude: List[str] = None) -> Dict[str, Any]:
        """
        Convert model to dictionary.
        
        Args:
            exclude: List of column names to exclude
            
        Returns:
            Dictionary representation of model
        """
        exclude = exclude or []
        result = {}
        for col in self.__table__.columns:
            if col.name not in exclude:
                value = getattr(self, col.name)
                if isinstance(value, datetime):
                    value = value.isoformat()
                result[col.name] = value
        return result


class ValidationError(Exception):
    """Custom validation error for better error messages."""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(message)


class InputValidator:
    """
    Static methods for input validation across the application.
    """
    
    @staticmethod
    def validate_uuid(value: str, field_name: str = "id") -> str:
        """Validate UUID format."""
        import uuid
        try:
            uuid.UUID(value)
            return value
        except (ValueError, AttributeError):
            raise ValidationError(f"Invalid {field_name} format", field_name)
    
    @staticmethod
    def validate_youtube_channel_id(value: str) -> str:
        """Validate YouTube channel ID format."""
        if not value:
            raise ValidationError("Channel ID is required", "youtube_channel_id")
        
        # Channel IDs start with UC and are 24 characters
        if value.startswith("UC") and len(value) == 24:
            return value
        # Handle @username format
        if value.startswith("@"):
            return value
        
        raise ValidationError(
            "Invalid YouTube channel ID format. Expected UC... format or @username",
            "youtube_channel_id"
        )
    
    @staticmethod
    def validate_youtube_video_id(value: str) -> str:
        """Validate YouTube video ID format."""
        if not value or len(value) < 10 or len(value) > 20:
            raise ValidationError("Invalid YouTube video ID", "video_id")
        return value
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize string input."""
        if not value:
            return ""
        # Remove control characters, limit length
        cleaned = "".join(c for c in value if c.isprintable() or c in "\n\t")
        return cleaned[:max_length].strip()
    
    @staticmethod
    def validate_pagination(page: int, page_size: int, max_page_size: int = 100) -> tuple:
        """
        Validate pagination parameters.
        
        Returns:
            Tuple of (validated_page, validated_page_size)
        """
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 50
        if page_size > max_page_size:
            page_size = max_page_size
        
        return page, page_size


class ETags:
    """
    ETag generation and validation utilities.
    """
    
    @staticmethod
    def generate(data: Any) -> str:
        """
        Generate ETag from data.
        
        Args:
            data: Any serializable data
            
        Returns:
            ETag string
        """
        import hashlib
        import json
        
        if isinstance(data, dict):
            # Sort keys for consistent hashing
            data_str = json.dumps(data, sort_keys=True, default=str)
        else:
            data_str = str(data)
        
        return hashlib.md5(data_str.encode()).hexdigest()
    
    @staticmethod
    def match(etag: str, if_none_match: str) -> bool:
        """
        Check if ETag matches If-None-Match header.
        
        Handles wildcards and multiple ETags.
        """
        if not if_none_match or not etag:
            return False
        
        # Handle wildcards
        if if_none_match == "*":
            return True
        
        # Handle multiple ETags
        etags = [e.strip() for e in if_none_match.split(",")]
        return etag in etags


class MetricsCollector:
    """
    Simple in-memory metrics collection for monitoring.
    In production, use Prometheus or similar.
    """
    
    _metrics: Dict[str, List[float]] = {}
    _counters: Dict[str, int] = {}
    
    @classmethod
    def record_timing(cls, metric_name: str, duration_ms: float):
        """Record timing metric."""
        if metric_name not in cls._metrics:
            cls._metrics[metric_name] = []
        cls._metrics[metric_name].append(duration_ms)
        
        # Keep only last 1000 measurements
        if len(cls._metrics[metric_name]) > 1000:
            cls._metrics[metric_name] = cls._metrics[metric_name][-1000:]
    
    @classmethod
    def increment_counter(cls, counter_name: str, amount: int = 1):
        """Increment counter."""
        cls._counters[counter_name] = cls._counters.get(counter_name, 0) + amount
    
    @classmethod
    def get_metrics(cls) -> Dict[str, Any]:
        """Get all metrics."""
        import statistics
        
        result = {
            "timings": {},
            "counters": dict(cls._counters)
        }
        
        for name, values in cls._metrics.items():
            if values:
                result["timings"][name] = {
                    "count": len(values),
                    "avg": round(statistics.mean(values), 2),
                    "min": round(min(values), 2),
                    "max": round(max(values), 2),
                    "p95": round(statistics.quantiles(values, n=20)[18], 2) if len(values) >= 20 else None
                }
        
        return result
    
    @classmethod
    def reset(cls):
        """Reset all metrics."""
        cls._metrics.clear()
        cls._counters.clear()


# Import for type hints
from typing import Callable, TypeVar, Generic

Dict[str, Any] = dict