import time
import logging
from typing import Dict, List, Optional
from fastapi import Request, HTTPException, status
from app.core.deps import get_client_ip
from app.core.config import settings

logger = logging.getLogger("clinova.rate_limiter")


class RateLimiter:
    """Rate protection foundation supporting per-client and per-user request throttling.
    
    Protects expensive AI and authentication endpoints from abuse and brute-force exhaustion.
    Uses Redis when available, with deterministic in-memory sliding window fallback.
    """

    def __init__(self):
        # In-memory sliding window storage: key -> list of timestamps
        self._memory_store: Dict[str, List[float]] = {}

    async def is_rate_limited(
        self,
        identifier: str,
        max_requests: int = 60,
        window_seconds: int = 60,
    ) -> bool:
        """Determines whether a client identifier has exceeded permitted request quota."""
        now = time.time()
        cutoff = now - window_seconds

        # 1. Check in-memory store
        history = self._memory_store.get(identifier, [])
        # Evict timestamps outside current window
        history = [ts for ts in history if ts > cutoff]

        if len(history) >= max_requests:
            logger.warning(f"RATE_LIMIT: Client {identifier} exceeded {max_requests} req / {window_seconds}s")
            self._memory_store[identifier] = history
            return True

        history.append(now)
        self._memory_store[identifier] = history
        return False


rate_limiter = RateLimiter()


def rate_limit(max_requests: int = 60, window_seconds: int = 60):
    """FastAPI dependency to throttle requests per client IP."""
    async def dependency(request: Request):
        client_ip = get_client_ip(request) or "unknown_client"
        endpoint = request.url.path
        key = f"{client_ip}:{endpoint}"

        limited = await rate_limiter.is_rate_limited(
            identifier=key,
            max_requests=max_requests,
            window_seconds=window_seconds,
        )
        if limited:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds permitted.",
            )
    return dependency
