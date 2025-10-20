"""Redis utilities for caching and geo operations."""

import json
from typing import Any, Dict, List, Optional, Tuple

import redis.asyncio as redis
from redis.asyncio import ConnectionPool, Redis
from tenacity import retry, stop_after_attempt, wait_exponential

from .errors import RedisError
from .logging import get_logger

logger = get_logger(__name__)


class RedisManager:
    """Manages Redis connections and operations."""

    def __init__(self, redis_url: str, max_connections: int = 50):
        self.redis_url = redis_url
        self.max_connections = max_connections
        self.pool: Optional[ConnectionPool] = None
        self.client: Optional[Redis] = None

    async def connect(self) -> None:
        """Establish Redis connection pool."""
        try:
            self.pool = ConnectionPool.from_url(
                self.redis_url,
                max_connections=self.max_connections,
                decode_responses=False,
            )
            self.client = Redis(connection_pool=self.pool, decode_responses=True)
            await self.client.ping()
            logger.info("Redis connection established", max_connections=self.max_connections)
        except Exception as e:
            logger.error("Failed to connect to Redis", error=str(e))
            raise RedisError(f"Failed to connect to Redis: {e}")

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self.client:
            await self.client.close()
            logger.info("Redis connection closed")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def get(self, key: str) -> Optional[str]:
        """Get a value from Redis."""
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error("Redis GET failed", key=key, error=str(e))
            raise RedisError(f"GET failed: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def set(
        self,
        key: str,
        value: str,
        ex: Optional[int] = None,
        nx: bool = False,
    ) -> bool:
        """Set a value in Redis."""
        try:
            return await self.client.set(key, value, ex=ex, nx=nx)
        except Exception as e:
            logger.error("Redis SET failed", key=key, error=str(e))
            raise RedisError(f"SET failed: {e}")

    async def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a JSON value from Redis."""
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None

    async def set_json(
        self,
        key: str,
        value: Dict[str, Any],
        ex: Optional[int] = None,
        nx: bool = False,
    ) -> bool:
        """Set a JSON value in Redis."""
        return await self.set(key, json.dumps(value), ex=ex, nx=nx)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def delete(self, *keys: str) -> int:
        """Delete keys from Redis."""
        try:
            return await self.client.delete(*keys)
        except Exception as e:
            logger.error("Redis DELETE failed", keys=keys, error=str(e))
            raise RedisError(f"DELETE failed: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def exists(self, *keys: str) -> int:
        """Check if keys exist."""
        try:
            return await self.client.exists(*keys)
        except Exception as e:
            logger.error("Redis EXISTS failed", keys=keys, error=str(e))
            raise RedisError(f"EXISTS failed: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def incr(self, key: str, amount: int = 1) -> int:
        """Increment a key."""
        try:
            return await self.client.incrby(key, amount)
        except Exception as e:
            logger.error("Redis INCR failed", key=key, error=str(e))
            raise RedisError(f"INCR failed: {e}")

    # Geo operations
    async def geoadd(
        self,
        key: str,
        longitude: float,
        latitude: float,
        member: str,
    ) -> int:
        """Add a geo location."""
        try:
            return await self.client.geoadd(key, (longitude, latitude, member))
        except Exception as e:
            logger.error("Redis GEOADD failed", key=key, member=member, error=str(e))
            raise RedisError(f"GEOADD failed: {e}")

    async def georadius(
        self,
        key: str,
        longitude: float,
        latitude: float,
        radius: float,
        unit: str = "km",
        withdist: bool = True,
        withcoord: bool = True,
        count: Optional[int] = None,
    ) -> List[Tuple]:
        """Find members within a radius."""
        try:
            return await self.client.georadius(
                key,
                longitude,
                latitude,
                radius,
                unit=unit,
                withdist=withdist,
                withcoord=withcoord,
                count=count,
            )
        except Exception as e:
            logger.error("Redis GEORADIUS failed", key=key, error=str(e))
            raise RedisError(f"GEORADIUS failed: {e}")

    async def geopos(self, key: str, *members: str) -> List[Optional[Tuple[float, float]]]:
        """Get positions of members."""
        try:
            return await self.client.geopos(key, *members)
        except Exception as e:
            logger.error("Redis GEOPOS failed", key=key, error=str(e))
            raise RedisError(f"GEOPOS failed: {e}")

    # Token bucket rate limiting
    async def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
    ) -> Tuple[bool, int]:
        """Check if request is within rate limit using sliding window."""
        try:
            import time

            now = int(time.time())
            window_start = now - window_seconds

            pipe = self.client.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            pipe.zadd(key, {str(now): now})
            pipe.expire(key, window_seconds)

            results = await pipe.execute()
            current_count = results[1]

            allowed = current_count < max_requests
            remaining = max(0, max_requests - current_count - 1)

            return allowed, remaining
        except Exception as e:
            logger.error("Rate limit check failed", key=key, error=str(e))
            # Fail open on Redis errors
            return True, max_requests
