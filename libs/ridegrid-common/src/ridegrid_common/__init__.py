"""RideGrid Common Library

Shared utilities, middleware, and abstractions for all RideGrid services.
"""

from .logging import setup_logging, get_logger
from .metrics import MetricsCollector, Timer
from .middleware import (
    create_middleware_stack,
    correlation_id_middleware,
    metrics_middleware,
    tracing_middleware,
)
from .errors import RideGridError, ValidationError, NotFoundError, ConflictError
from .database import DatabaseManager, OutboxManager, InboxManager
from .redis import RedisManager
from .kafka import KafkaProducer, KafkaConsumer
from .config import Settings

__version__ = "1.0.0"

__all__ = [
    "setup_logging",
    "get_logger",
    "MetricsCollector",
    "Timer",
    "create_middleware_stack",
    "correlation_id_middleware",
    "metrics_middleware",
    "tracing_middleware",
    "RideGridError",
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    "DatabaseManager",
    "OutboxManager",
    "InboxManager",
    "RedisManager",
    "KafkaProducer",
    "KafkaConsumer",
    "Settings",
]



