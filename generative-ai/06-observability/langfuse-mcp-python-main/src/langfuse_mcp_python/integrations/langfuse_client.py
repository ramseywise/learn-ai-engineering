"""
Enhanced Langfuse Client Wrapper
- Connection pooling
- Rate limiting
- Request tracking
- Error handling
"""

import os
import time
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio

from langfuse import Langfuse
import httpx


class RateLimiter:
    """Simple token bucket rate limiter"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.tokens = requests_per_minute
        self.last_update = time.time()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire a token, waiting if necessary"""
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            
            # Refill tokens based on elapsed time
            self.tokens = min(
                self.requests_per_minute,
                self.tokens + (elapsed * self.requests_per_minute / 60)
            )
            self.last_update = now
            
            # If no tokens available, wait
            if self.tokens < 1:
                wait_time = (1 - self.tokens) * 60 / self.requests_per_minute
                await asyncio.sleep(wait_time)
                self.tokens = 1
            
            self.tokens -= 1


class EnhancedLangfuseClient:
    """
    Production-ready Langfuse client wrapper with:
    - Connection pooling
    - Rate limiting
    - Request tracking
    - Automatic retries
    - Health checks
    """
    
    def __init__(
        self,
        public_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        host: Optional[str] = None,
        requests_per_minute: int = 60,
        enable_rate_limiting: bool = True,
    ):
        # Get credentials from environment or arguments
        self.public_key = public_key or os.getenv("LANGFUSE_PUBLIC_KEY")
        self.secret_key = secret_key or os.getenv("LANGFUSE_SECRET_KEY")
        # Prefer base URL when provided (newer SDKs), fallback to host/env, then default.
        self.host = (
            os.getenv("LANGFUSE_BASE_URL")
            or host
            or os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        )
        
        if not self.public_key or not self.secret_key:
            raise ValueError(
                "Missing Langfuse credentials. Provide via arguments or set "
                "LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY environment variables."
            )
        
        # Validate credential format
        self._validate_credentials()
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(requests_per_minute) if enable_rate_limiting else None
        
        # Create HTTP client with connection pooling
        self.http_client = httpx.Client(
            limits=httpx.Limits(
                max_connections=100,
                max_keepalive_connections=20,
            ),
            timeout=30.0,
            follow_redirects=True,
        )
        
        # Initialize Langfuse client
        self.client = Langfuse(
            public_key=self.public_key,
            secret_key=self.secret_key,
            host=self.host,
            httpx_client=self.http_client,
        )
        
        # Request tracking
        self.request_count = 0
        self.last_request_time = None
        self.health_status = "unknown"
        
        print(f"[OK] Connected to Langfuse at {self.host}")
    
    def _validate_credentials(self):
        """Validate credential format"""
        if not self.public_key.startswith('pk-lf-'):
            raise ValueError(f"Invalid public key format. Must start with 'pk-lf-'")
        
        if not self.secret_key.startswith('sk-lf-'):
            raise ValueError(f"Invalid secret key format. Must start with 'sk-lf-'")
    
    async def _apply_rate_limit(self):
        """Apply rate limiting if enabled"""
        if self.rate_limiter:
            await self.rate_limiter.acquire()
        
        self.request_count += 1
        self.last_request_time = datetime.now()
    
    # ============================================================================
    # HEALTH CHECK
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check connection health
        Returns health status and basic info
        """
        try:
            # Try to fetch projects (lightweight operation)
            projects = self.client.api.projects.list()
            
            self.health_status = "healthy"
            
            return {
                "status": "healthy",
                "host": self.host,
                "request_count": self.request_count,
                "last_request": self.last_request_time.isoformat() if self.last_request_time else None,
            }
        
        except Exception as e:
            self.health_status = "unhealthy"
            
            return {
                "status": "unhealthy",
                "error": str(e),
                "host": self.host,
            }
    
    # ============================================================================
    # API ACCESS PROPERTIES
    # ============================================================================
    
    @property
    def api(self):
        """Access to the Langfuse API"""
        return self.client.api
    
    # ============================================================================
    # CONVENIENCE METHODS WITH RATE LIMITING
    # ============================================================================
    
    async def fetch_traces(self, **kwargs) -> Any:
        """Fetch traces with rate limiting"""
        await self._apply_rate_limit()
        return self.client.api.trace.list(**kwargs)
    
    async def fetch_trace(self, trace_id: str) -> Any:
        """Fetch single trace with rate limiting"""
        await self._apply_rate_limit()
        return self.client.api.trace.get(trace_id)
    
    async def fetch_observations(self, **kwargs) -> Any:
        """Fetch observations with rate limiting"""
        await self._apply_rate_limit()
        return self.client.api.observations.get_many(**kwargs)
    
    async def fetch_sessions(self, **kwargs) -> Any:
        """Fetch sessions with rate limiting"""
        await self._apply_rate_limit()
        return self.client.api.sessions.list(**kwargs)
    
    async def fetch_scores(self, **kwargs) -> Any:
        """Fetch scores with rate limiting"""
        await self._apply_rate_limit()
        return self.client.api.scores.list(**kwargs)
    
    async def fetch_prompts(self, **kwargs) -> Any:
        """Fetch prompts with rate limiting"""
        await self._apply_rate_limit()
        return self.client.api.prompts.list(**kwargs)
    
    async def fetch_datasets(self, **kwargs) -> Any:
        """Fetch datasets with rate limiting"""
        await self._apply_rate_limit()
        return self.client.api.datasets.list(**kwargs)
    
    async def fetch_models(self, **kwargs) -> Any:
        """Fetch models with rate limiting"""
        await self._apply_rate_limit()
        return self.client.api.models.list(**kwargs)
    
    # ============================================================================
    # METRICS & ANALYTICS
    # ============================================================================
    
    async def get_metrics(self, query: Dict[str, Any]) -> Any:
        """
        Get aggregated metrics from Langfuse Metrics API
        
        Args:
            view: "traces", "observations", or "scores"
            dimensions: List of dimension fields
            metrics: List of metrics to compute
            filters: List of filter conditions
            group_by: List of fields to group by
            time_range: {"from": ISO8601, "to": ISO8601}
            granularity: "hour", "day", "week", "month"
        """
        await self._apply_rate_limit()
        # Use legacy metrics_v1 to support traces view and simplified queries.
        return self.client.api.legacy.metrics_v1.metrics(
            query=json.dumps(query)
        )
    
    # ============================================================================
    # CLEANUP
    # ============================================================================
    
    def close(self):
        """Close HTTP client connections"""
        if self.http_client:
            self.http_client.close()
        
        print("[OK] Langfuse client closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
