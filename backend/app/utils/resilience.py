"""
Resilience Utilities for CreatorIQ Platform
Implements circuit breaker, retry with backoff, and bulkhead patterns.
"""

import asyncio
import time
import logging
from typing import Optional, Callable, Any, TypeVar
from functools import wraps
from enum import Enum
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreaker:
    """
    Circuit breaker implementation for external API calls.
    
    Prevents cascading failures by failing fast when a service is down.
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Service is failing, requests are rejected immediately
    - HALF_OPEN: Testing if service recovered, limited requests pass
    
    Configuration:
    - failure_threshold: Number of failures before opening circuit
    - recovery_timeout: Seconds to wait before testing recovery
    - half_open_max_calls: Number of calls allowed in half-open state
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        half_open_max_calls: int = 3,
        excluded_exceptions: tuple = (KeyboardInterrupt,)
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._half_open_calls = 0
        self._excluded_exceptions = excluded_exceptions
        
        # Metrics
        self._total_calls = 0
        self._successful_calls = 0
        self._failed_calls = 0
        self._rejected_calls = 0
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        if self._state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self._last_failure_time and \
               time.time() - self._last_failure_time >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
                logger.info(f"Circuit breaker '{self.name}' entering HALF_OPEN state")
        return self._state
    
    @property
    def metrics(self) -> dict:
        """Get circuit breaker metrics."""
        return {
            "name": self.name,
            "state": self.state.value,
            "total_calls": self._total_calls,
            "successful_calls": self._successful_calls,
            "failed_calls": self._failed_calls,
            "rejected_calls": self._rejected_calls,
            "failure_count": self._failure_count,
            "last_failure": self._last_failure_time
        }
    
    def _record_success(self):
        """Record a successful call."""
        self._successful_calls += 1
        self._total_calls += 1
        if self._state == CircuitState.HALF_OPEN:
            self._half_open_calls += 1
            if self._half_open_calls >= self.half_open_max_calls:
                # Successful recovery
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                logger.info(f"Circuit breaker '{self.name}' recovered and CLOSED")
        elif self._state == CircuitState.CLOSED:
            # Reset failure count on success
            self._failure_count = 0
    
    def _record_failure(self):
        """Record a failed call."""
        self._failed_calls += 1
        self._total_calls += 1
        self._failure_count += 1
        self._last_failure_time = time.time()
        
        if self._state == CircuitState.HALF_OPEN:
            # Failed during recovery testing, reopen circuit
            self._state = CircuitState.OPEN
            logger.warning(f"Circuit breaker '{self.name}' re-opened after half-open failure")
        elif self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
            logger.warning(f"Circuit breaker '{self.name}' opened after {self._failure_count} failures")
    
    async def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Execute function through circuit breaker.
        
        Raises:
            CircuitBreakerOpen: When circuit is open
            Exception: Original exception from function
        """
        if self.state == CircuitState.OPEN:
            self._rejected_calls += 1
            raise CircuitBreakerOpen(f"Circuit breaker '{self.name}' is OPEN")
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            self._record_success()
            return result
        except self._excluded_exceptions:
            raise
        except Exception as e:
            self._record_failure()
            raise
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator usage of circuit breaker."""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await self.call(func, *args, **kwargs)
        return wrapper


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is open."""
    pass


class CircuitBreakerManager:
    """
    Global manager for circuit breakers.
    Provides centralized circuit breaker instances for different services.
    """
    
    _breakers: dict[str, CircuitBreaker] = {}
    
    @classmethod
    def get_breaker(cls, name: str, **kwargs) -> CircuitBreaker:
        """Get or create a circuit breaker by name."""
        if name not in cls._breakers:
            cls._breakers[name] = CircuitBreaker(name, **kwargs)
        return cls._breakers[name]
    
    @classmethod
    def get_all_metrics(cls) -> dict:
        """Get metrics for all circuit breakers."""
        return {name: cb.metrics for name, cb in cls._breakers.items()}
    
    @classmethod
    def reset_all(cls):
        """Reset all circuit breakers to closed state."""
        for cb in cls._breakers.values():
            cb._state = CircuitState.CLOSED
            cb._failure_count = 0


# Pre-configured circuit breakers for external services
YOUTUBE_CB = CircuitBreakerManager.get_breaker(
    "youtube_api",
    failure_threshold=5,
    recovery_timeout=60
)

OPENAI_CB = CircuitBreakerManager.get_breaker(
    "openai_api",
    failure_threshold=3,
    recovery_timeout=30
)

SCRAPER_CB = CircuitBreakerManager.get_breaker(
    "web_scraper",
    failure_threshold=10,
    recovery_timeout=120
)


class RateLimiter:
    """
    Token bucket rate limiter for API calls.
    
    Thread-safe implementation using deque for sliding window.
    """
    
    def __init__(self, rate: int, per_seconds: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            rate: Maximum number of calls allowed
            per_seconds: Time window in seconds
        """
        self.rate = rate
        self.per_seconds = per_seconds
        self._tokens = deque()
        self._lock = asyncio.Lock()
    
    async def acquire(self, timeout: Optional[float] = None) -> bool:
        """
        Acquire a token, waiting if necessary.
        
        Returns True if token acquired, False if timeout.
        """
        start_time = time.time()
        
        while True:
            async with self._lock:
                now = time.time()
                # Remove expired tokens
                while self._tokens and now - self._tokens[0] >= self.per_seconds:
                    self._tokens.popleft()
                
                if len(self._tokens) < self.rate:
                    self._tokens.append(now)
                    return True
            
            # Check timeout
            if timeout and time.time() - start_time >= timeout:
                return False
            
            # Wait before retrying
            await asyncio.sleep(0.1)
    
    @property
    def available(self) -> int:
        """Get number of available tokens."""
        now = time.time()
        while self._tokens and now - self._tokens[0] >= self.per_seconds:
            self._tokens.popleft()
        return max(0, self.rate - len(self._tokens))


class Bulkhead:
    """
    Bulkhead pattern implementation for resource isolation.
    
    Limits concurrent executions to prevent resource exhaustion.
    """
    
    def __init__(self, max_concurrent: int = 10, max_queue: int = 100):
        self.max_concurrent = max_concurrent
        self.max_queue = max_queue
        self._active = 0
        self._queue_size = 0
        self._lock = asyncio.Lock()
        self._condition = asyncio.Condition(self._lock)
    
    async def __aenter__(self):
        async with self._lock:
            if self._active >= self.max_concurrent:
                if self._queue_size >= self.max_queue:
                    raise BulkheadFull("Bulkhead queue is full")
                self._queue_size += 1
                try:
                    await self._condition.wait_for(
                        lambda: self._active < self.max_concurrent
                    )
                finally:
                    self._queue_size -= 1
            self._active += 1
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        async with self._lock:
            self._active -= 1
            self._condition.notify()
        return False
    
    @property
    def metrics(self) -> dict:
        """Get bulkhead metrics."""
        return {
            "max_concurrent": self.max_concurrent,
            "active": self._active,
            "queue_size": self._queue_size
        }


class BulkheadFull(Exception):
    """Exception raised when bulkhead queue is full."""
    pass


class RetryWithBackoff:
    """
    Configurable retry with exponential backoff.
    
    Better than tenacity for simple retry needs.
    """
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(self.max_attempts):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < self.max_attempts - 1:
                        delay = min(
                            self.base_delay * (self.exponential_base ** attempt),
                            self.max_delay
                        )
                        if self.jitter:
                            import random
                            delay *= (0.5 + random.random())
                        logger.warning(
                            f"Retry {attempt + 1}/{self.max_attempts} for {func.__name__} "
                            f"after {delay:.2f}s: {str(e)}"
                        )
                        await asyncio.sleep(delay)
            
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(self.max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < self.max_attempts - 1:
                        delay = min(
                            self.base_delay * (self.exponential_base ** attempt),
                            self.max_delay
                        )
                        if self.jitter:
                            import random
                            delay *= (0.5 + random.random())
                        logger.warning(
                            f"Retry {attempt + 1}/{self.max_attempts} for {func.__name__} "
                            f"after {delay:.2f}s: {str(e)}"
                        )
                        time.sleep(delay)
            
            raise last_exception
        
        if asyncio.iscoroutinefunction(func):
            return wrapper
        return sync_wrapper