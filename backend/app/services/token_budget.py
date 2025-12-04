"""
Token budget management service.
Tracks daily/weekly token usage per user and enforces limits based on subscription plan.
"""
from typing import Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

# Default token limits per plan (monthly)
TOKEN_LIMITS = {
    "free": 100_000,
    "starter": 500_000,
    "pro": 2_000_000,
    "enterprise": 10_000_000
}

# Alert thresholds
WARNING_THRESHOLD = 0.70  # 70% of limit
CRITICAL_THRESHOLD = 0.90  # 90% of limit


class TokenBudgetManager:
    """
    Manages token usage budgets per user based on subscription plan.
    Tracks usage in-memory and periodically persists to database.
    """
    
    # In-memory tracking (reset on restart - in production, use Redis)
    _usage_cache: Dict[str, Dict] = {}
    _last_reset: Dict[str, datetime] = {}
    
    @classmethod
    def get_user_plan(cls, user_id: str, db: Session) -> str:
        """Get user's subscription plan from database."""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user and hasattr(user, 'subscription_tier'):
                return user.subscription_tier or "free"
        except Exception as e:
            logger.warning(f"Could not fetch user plan: {e}")
        return "free"
    
    @classmethod
    def get_token_limit(cls, plan: str) -> int:
        """Get token limit for a subscription plan."""
        return TOKEN_LIMITS.get(plan, TOKEN_LIMITS["free"])
    
    @classmethod
    def get_period_start(cls, period_type: str = "monthly") -> datetime:
        """Get start of current period (daily or monthly)."""
        now = datetime.utcnow()
        if period_type == "daily":
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    @classmethod
    def _init_user_tracking(cls, user_id: str):
        """Initialize tracking for a user if not exists."""
        if user_id not in cls._usage_cache:
            cls._usage_cache[user_id] = {
                "tokens_used": 0,
                "requests_count": 0,
                "period_start": cls.get_period_start(),
                "daily_usage": {}
            }
    
    @classmethod
    def track_tokens(cls, user_id: str, input_tokens: int, output_tokens: int = 0):
        """
        Track token usage for a user.
        Call this after each AI API call.
        
        Args:
            user_id: User ID
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens used
        """
        cls._init_user_tracking(user_id)
        
        now = datetime.utcnow()
        period_start = cls.get_period_start()
        
        # Reset if new period
        if cls._usage_cache[user_id]["period_start"] < period_start:
            cls._usage_cache[user_id] = {
                "tokens_used": 0,
                "requests_count": 0,
                "period_start": period_start,
                "daily_usage": {}
            }
        
        # Track daily usage for finer granularity
        today = now.date().isoformat()
        daily = cls._usage_cache[user_id].get("daily_usage", {})
        daily[today] = daily.get(today, 0) + input_tokens + output_tokens
        cls._usage_cache[user_id]["daily_usage"] = daily
        
        cls._usage_cache[user_id]["tokens_used"] += input_tokens + output_tokens
        cls._usage_cache[user_id]["requests_count"] += 1
        
        logger.debug(f"Token usage tracked for {user_id}: {input_tokens + output_tokens} tokens")
    
    @classmethod
    def get_usage(cls, user_id: str, plan: str, period_type: str = "monthly") -> Dict:
        """
        Get current token usage for a user.
        
        Args:
            user_id: User ID
            plan: Subscription plan
            period_type: "daily" or "monthly"
            
        Returns:
            Dict with usage stats and budget status
        """
        cls._init_user_tracking(user_id)
        
        limit = cls.get_token_limit(plan)
        used = cls._usage_cache[user_id]["tokens_used"]
        requests = cls._usage_cache[user_id]["requests_count"]
        
        if period_type == "daily":
            today = datetime.utcnow().date().isoformat()
            daily_usage = cls._usage_cache[user_id].get("daily_usage", {})
            used = daily_usage.get(today, 0)
            # Approximate daily limit as monthly / 30
            limit = limit // 30
        
        percentage = (used / limit * 100) if limit > 0 else 0
        
        return {
            "user_id": user_id,
            "plan": plan,
            "period_type": period_type,
            "tokens_used": used,
            "token_limit": limit,
            "percentage": round(percentage, 1),
            "remaining": max(0, limit - used),
            "requests_count": requests,
            "status": "ok" if percentage < WARNING_THRESHOLD * 100 
                    else "warning" if percentage < CRITICAL_THRESHOLD * 100 
                    else "critical",
            "can_proceed": percentage < CRITICAL_THRESHOLD * 100
        }
    
    @classmethod
    def check_budget(cls, user_id: str, plan: str, estimated_tokens: int) -> bool:
        """
        Check if user has sufficient budget for a request.
        
        Args:
            user_id: User ID
            plan: Subscription plan
            estimated_tokens: Estimated tokens for the request
            
        Returns:
            True if user can proceed, False if over budget
        """
        usage = cls.get_usage(user_id, plan)
        return usage["remaining"] >= estimated_tokens
    
    @classmethod
    def get_remaining_tokens(cls, user_id: str, plan: str) -> int:
        """Get remaining tokens for user."""
        usage = cls.get_usage(user_id, plan)
        return usage["remaining"]
    
    @classmethod
    def log_token_consumption(
        cls,
        user_id: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        operation: str,
        success: bool = True
    ):
        """
        Log detailed token consumption for analytics.
        In production, this would write to a database or analytics service.
        
        Args:
            user_id: User ID
            model: Model used
            input_tokens: Input token count
            output_tokens: Output token count
            operation: Operation type (e.g., "creator_analysis", "hook_generation")
            success: Whether the operation succeeded
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "operation": operation,
            "success": success
        }
        
        # In production: write to analytics database/warehouse
        # For now, log at info level
        logger.info(f"Token consumption: {log_data}")
        
        # Track in memory
        cls.track_tokens(user_id, input_tokens, output_tokens)


# Convenience functions for use in services
def track_usage(user_id: str, input_tokens: int, output_tokens: int = 0):
    """Track token usage for a user."""
    TokenBudgetManager.track_tokens(user_id, input_tokens, output_tokens)


def get_user_budget_status(user_id: str, plan: str) -> Dict:
    """Get budget status for a user."""
    return TokenBudgetManager.get_usage(user_id, plan)


def can_use_tokens(user_id: str, plan: str, estimated_tokens: int) -> bool:
    """Check if user has budget for estimated token count."""
    return TokenBudgetManager.check_budget(user_id, plan, estimated_tokens)