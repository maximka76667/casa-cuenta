from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request, HTTPException
from dependencies import get_redis
import redis.asyncio as redis
from middlewares.logger import get_logger
from typing import Optional
import asyncio
import hashlib

logger = get_logger()


class RedisStorage:
    """Custom Redis storage for SlowAPI"""

    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client

    async def get(self, key: str) -> Optional[int]:
        """Get current count for rate limit key"""
        try:
            value = await self.redis_client.get(key)
            return int(value) if value else None
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return None

    async def set(self, key: str, value: int, expire: int):
        """Set rate limit count with expiration"""
        try:
            await self.redis_client.setex(key, expire, value)
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")

    async def incr(self, key: str, expire: int) -> int:
        """Increment rate limit count"""
        try:
            # Use pipeline for atomic operations
            async with self.redis_client.pipeline() as pipe:
                await pipe.incr(key)
                await pipe.expire(key, expire)
                results = await pipe.execute()
                return results[0]
        except Exception as e:
            logger.error(f"Redis incr error for key {key}: {e}")
            return 1


# Custom key function to identify clients
def get_client_id(request: Request) -> str:
    """Generate a unique client identifier"""
    # Try to get user ID from headers (if authenticated)
    user_id = request.headers.get("user-id")
    if user_id:
        return f"user:{user_id}"

    # Fall back to IP address
    client_ip = get_remote_address(request)
    return f"ip:{client_ip}"


def get_endpoint_key(request: Request) -> str:
    """Generate rate limit key based on endpoint and client"""
    client_id = get_client_id(request)
    endpoint = f"{request.method}:{request.url.path}"

    # Create a hash for long URLs
    endpoint_hash = hashlib.md5(endpoint.encode()).hexdigest()[:8]

    return f"rate_limit:{client_id}:{endpoint_hash}"


# Initialize with a placeholder - will be updated with Redis client
limiter = Limiter(key_func=get_endpoint_key, default_limits=["1000/hour", "100/minute"])


async def init_rate_limiter():
    """Initialize rate limiter with Redis storage"""
    redis_client = get_redis()
    storage = RedisStorage(redis_client)
    limiter.storage = storage
    logger.info("Rate limiter initialized with Redis storage")


# Custom rate limit exceeded handler
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    client_id = get_client_id(request)
    endpoint = f"{request.method}:{request.url.path}"

    logger.warning(
        f"RATE_LIMIT_EXCEEDED | Client: {client_id} | Endpoint: {endpoint} | "
        f"Limit: {exc.detail}"
    )

    return HTTPException(
        status_code=429,
        detail={
            "error": "Rate limit exceeded",
            "message": f"Too many requests. Limit: {exc.detail}",
            "retry_after": getattr(exc, "retry_after", 60),
        },
    )


# Rate limiting decorators for different tiers
def basic_rate_limit():
    """Basic rate limiting: 60 requests per minute"""
    return limiter.limit("60/minute")


def strict_rate_limit():
    """Strict rate limiting: 20 requests per minute"""
    return limiter.limit("20/minute")


def auth_rate_limit():
    """Authentication endpoint rate limiting: 5 requests per minute"""
    return limiter.limit("5/minute")


def expensive_rate_limit():
    """Expensive operation rate limiting: 10 requests per minute"""
    return limiter.limit("10/minute")
