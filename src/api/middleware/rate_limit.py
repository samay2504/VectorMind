"""
Rate Limiting Middleware
Protects API from abuse using token bucket algorithm
"""

import logging
import time
from typing import Dict, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from collections import defaultdict
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class TokenBucket:
    """Token bucket for rate limiting"""
    capacity: int
    refill_rate: float  # tokens per second
    tokens: float = field(default=0)
    last_refill: float = field(default_factory=time.time)
    
    def __post_init__(self):
        self.tokens = self.capacity
    
    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens
        
        Args:
            tokens: Number of tokens to consume
        
        Returns:
            True if tokens were consumed
        """
        self.refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def refill(self):
        """Refill tokens based on time elapsed"""
        now = time.time()
        elapsed = now - self.last_refill
        
        # Add tokens based on elapsed time
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def get_wait_time(self, tokens: int = 1) -> float:
        """
        Get time to wait until tokens are available
        
        Args:
            tokens: Number of tokens needed
        
        Returns:
            Seconds to wait
        """
        self.refill()
        
        if self.tokens >= tokens:
            return 0.0
        
        tokens_needed = tokens - self.tokens
        return tokens_needed / self.refill_rate


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using token bucket algorithm
    Limits requests per client based on IP address or user ID
    """
    
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        burst_size: int = 10,
        exclude_paths: list = None,
        key_func: Optional[callable] = None
    ):
        """
        Initialize Rate Limit middleware
        
        Args:
            app: FastAPI application
            requests_per_minute: Sustained request rate
            burst_size: Maximum burst size
            exclude_paths: Paths to exclude from rate limiting
            key_func: Custom function to extract rate limit key from request
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.exclude_paths = exclude_paths or ["/healthz", "/metrics"]
        self.key_func = key_func or self._default_key_func
        
        # Storage for token buckets
        self.buckets: Dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(
                capacity=self.burst_size,
                refill_rate=self.requests_per_minute / 60.0
            )
        )
        
        # Cleanup old buckets periodically
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 minutes
    
    def _default_key_func(self, request: Request) -> str:
        """
        Default function to extract rate limit key
        
        Args:
            request: FastAPI request
        
        Returns:
            Rate limit key (client IP)
        """
        # Try to get real IP from proxy headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Fall back to client IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request and apply rate limiting
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
        
        Returns:
            Response or rate limit error
        """
        # Skip rate limiting for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # Get rate limit key (usually IP address or user ID)
        key = self.key_func(request)
        
        # Get or create token bucket for this key
        bucket = self.buckets[key]
        
        # Try to consume a token
        if bucket.consume(1):
            # Request allowed
            response = await call_next(request)
            
            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
            response.headers["X-RateLimit-Remaining"] = str(int(bucket.tokens))
            response.headers["X-RateLimit-Reset"] = str(int(bucket.last_refill + 60))
            
            return response
        else:
            # Rate limit exceeded
            wait_time = bucket.get_wait_time(1)
            
            logger.warning(
                f"Rate limit exceeded for {key} on {request.method} {request.url.path}"
            )
            
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Please try again in {int(wait_time)} seconds.",
                    "retry_after": int(wait_time)
                },
                headers={
                    "Retry-After": str(int(wait_time)),
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(bucket.last_refill + 60))
                }
            )
    
    def cleanup_old_buckets(self):
        """Remove inactive token buckets to prevent memory leak"""
        now = time.time()
        
        if now - self.last_cleanup < self.cleanup_interval:
            return
        
        # Find buckets that haven't been used in 1 hour
        inactive_threshold = now - 3600
        inactive_keys = [
            key for key, bucket in self.buckets.items()
            if bucket.last_refill < inactive_threshold
        ]
        
        for key in inactive_keys:
            del self.buckets[key]
        
        if inactive_keys:
            logger.info(f"Cleaned up {len(inactive_keys)} inactive rate limit buckets")
        
        self.last_cleanup = now


class RateLimiter:
    """
    Standalone rate limiter (can be used as dependency)
    """
    
    def __init__(self, requests_per_minute: int = 60, burst_size: int = 10):
        """
        Initialize rate limiter
        
        Args:
            requests_per_minute: Sustained request rate
            burst_size: Maximum burst size
        """
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.buckets: Dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(
                capacity=self.burst_size,
                refill_rate=self.requests_per_minute / 60.0
            )
        )
    
    def check_rate_limit(self, key: str) -> tuple[bool, Optional[float]]:
        """
        Check if request should be allowed
        
        Args:
            key: Rate limit key
        
        Returns:
            Tuple of (allowed, wait_time)
        """
        bucket = self.buckets[key]
        
        if bucket.consume(1):
            return True, None
        else:
            wait_time = bucket.get_wait_time(1)
            return False, wait_time
    
    def reset(self, key: str):
        """Reset rate limit for a key"""
        if key in self.buckets:
            del self.buckets[key]
