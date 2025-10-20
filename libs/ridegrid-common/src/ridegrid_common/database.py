"""Database utilities with outbox/inbox pattern support."""

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import asyncpg
from asyncpg import Connection, Pool
from tenacity import retry, stop_after_attempt, wait_exponential

from .errors import DatabaseError
from .logging import get_logger
from .metrics import get_metrics_collector

logger = get_logger(__name__)


class DatabaseManager:
    """Manages database connections and operations."""

    def __init__(self, database_url: str, min_size: int = 5, max_size: int = 20):
        self.database_url = database_url
        self.min_size = min_size
        self.max_size = max_size
        self.pool: Optional[Pool] = None

    async def connect(self) -> None:
        """Establish database connection pool."""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=self.min_size,
                max_size=self.max_size,
                command_timeout=60,
            )
            logger.info("Database pool created", min_size=self.min_size, max_size=self.max_size)
        except Exception as e:
            logger.error("Failed to create database pool", error=str(e))
            raise DatabaseError(f"Failed to connect to database: {e}")

    async def disconnect(self) -> None:
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Database pool closed")

    async def acquire(self) -> Connection:
        """Acquire a connection from the pool."""
        if not self.pool:
            raise DatabaseError("Database pool not initialized")
        return await self.pool.acquire()

    async def release(self, connection: Connection) -> None:
        """Release a connection back to the pool."""
        if self.pool:
            await self.pool.release(connection)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def execute(self, query: str, *args: Any) -> str:
        """Execute a query with retry logic."""
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def fetch(self, query: str, *args: Any) -> List[asyncpg.Record]:
        """Fetch multiple rows with retry logic."""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def fetchrow(self, query: str, *args: Any) -> Optional[asyncpg.Record]:
        """Fetch a single row with retry logic."""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def fetchval(self, query: str, *args: Any) -> Any:
        """Fetch a single value with retry logic."""
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)


class OutboxManager:
    """Manages transactional outbox pattern for reliable event publishing."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    async def insert_message(
        self,
        connection: Connection,
        topic: str,
        key: str,
        payload: Dict[str, Any],
        message_id: Optional[str] = None,
    ) -> str:
        """Insert a message into the outbox table within a transaction."""
        if not message_id:
            message_id = str(uuid.uuid4())

        await connection.execute(
            """
            INSERT INTO outbox_messages (message_id, topic, key, payload, created_at)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (message_id) DO NOTHING
            """,
            message_id,
            topic,
            key,
            json.dumps(payload),
            datetime.now(timezone.utc),
        )

        logger.info("Outbox message inserted", message_id=message_id, topic=topic, key=key)
        return message_id

    async def get_pending_messages(self, limit: int = 100) -> List[asyncpg.Record]:
        """Get pending messages from outbox."""
        return await self.db_manager.fetch(
            """
            SELECT message_id, topic, key, payload, created_at
            FROM outbox_messages
            WHERE published_at IS NULL
            ORDER BY created_at
            LIMIT $1
            FOR UPDATE SKIP LOCKED
            """,
            limit,
        )

    async def mark_published(self, connection: Connection, message_id: str) -> None:
        """Mark a message as published."""
        await connection.execute(
            """
            UPDATE outbox_messages
            SET published_at = $1
            WHERE message_id = $2
            """,
            datetime.now(timezone.utc),
            message_id,
        )

    async def cleanup_old_messages(self, days: int = 7) -> int:
        """Clean up old published messages."""
        result = await self.db_manager.execute(
            """
            DELETE FROM outbox_messages
            WHERE published_at IS NOT NULL
            AND published_at < NOW() - INTERVAL '%s days'
            """,
            days,
        )
        count = int(result.split()[-1]) if result else 0
        logger.info("Outbox cleanup completed", deleted_count=count)
        return count


class InboxManager:
    """Manages inbox pattern for exactly-once message processing."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    async def is_duplicate(
        self,
        connection: Connection,
        message_id: str,
        source: str,
    ) -> bool:
        """Check if a message has already been processed."""
        result = await connection.fetchval(
            """
            SELECT EXISTS(
                SELECT 1 FROM inbox_messages
                WHERE message_id = $1 AND source = $2
            )
            """,
            message_id,
            source,
        )
        return bool(result)

    async def mark_processed(
        self,
        connection: Connection,
        message_id: str,
        source: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Mark a message as processed."""
        await connection.execute(
            """
            INSERT INTO inbox_messages (message_id, source, payload, processed_at)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (message_id, source) DO NOTHING
            """,
            message_id,
            source,
            json.dumps(payload) if payload else None,
            datetime.now(timezone.utc),
        )

    async def cleanup_old_messages(self, days: int = 7) -> int:
        """Clean up old processed messages."""
        result = await self.db_manager.execute(
            """
            DELETE FROM inbox_messages
            WHERE processed_at < NOW() - INTERVAL '%s days'
            """,
            days,
        )
        count = int(result.split()[-1]) if result else 0
        logger.info("Inbox cleanup completed", deleted_count=count)
        return count
