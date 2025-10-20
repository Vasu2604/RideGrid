"""Structured logging with OTel integration."""

import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Optional

import structlog
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Status, StatusCode

# Context variables for correlation tracking
correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)
request_id: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id: ContextVar[Optional[str]] = ContextVar("user_id", default=None)


def setup_logging(
    service_name: str,
    log_level: str = "INFO",
    otel_endpoint: Optional[str] = None,
    enable_json: bool = True,
) -> None:
    """Set up structured logging with OTel integration."""

    # Set up OTel tracing if endpoint provided
    if otel_endpoint:
        resource = Resource.create({"service.name": service_name})
        tracer_provider = TracerProvider(resource=resource)
        otel_exporter = OTLPSpanExporter(endpoint=otel_endpoint, insecure=True)
        span_processor = BatchSpanProcessor(otel_exporter)
        tracer_provider.add_span_processor(span_processor)
        trace.set_tracer_provider(tracer_provider)

    # Configure structlog
    if enable_json:
        # JSON logging for production
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            context_class=dict,
            cache_logger_on_first_use=True,
        )
    else:
        # Human-readable logging for development
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
                structlog.dev.ConsoleRenderer(colors=True),
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            context_class=dict,
            cache_logger_on_first_use=True,
        )

    # Configure Python's standard logging to use structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class TracingLogger:
    """Logger that automatically creates spans for operations."""

    def __init__(self, logger: structlog.stdlib.BoundLogger, operation_name: str):
        self.logger = logger
        self.operation_name = operation_name
        self.span = None

    def __enter__(self):
        tracer = trace.get_tracer(__name__)
        self.span = tracer.start_span(self.operation_name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.span:
            if exc_type:
                self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
                self.span.record_exception(exc_val)
            else:
                self.span.set_status(Status(StatusCode.OK))
            self.span.end()

    def log(self, level: str, message: str, **kwargs):
        """Log with span context."""
        if self.span:
            self.span.add_event(message, kwargs)

        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(message, span_id=self.span.get_span_context().span_id if self.span else None, **kwargs)


def with_correlation_id(correlation_id_value: str):
    """Set correlation ID in context."""
    correlation_id.set(correlation_id_value)


def with_request_id(request_id_value: str):
    """Set request ID in context."""
    request_id.set(request_id_value)


def with_user_id(user_id_value: str):
    """Set user ID in context."""
    user_id.set(user_id_value)


def generate_correlation_id() -> str:
    """Generate a new correlation ID."""
    return str(uuid.uuid4())


def generate_request_id() -> str:
    """Generate a new request ID."""
    return str(uuid.uuid4())



