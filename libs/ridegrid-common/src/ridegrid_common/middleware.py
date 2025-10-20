"""FastAPI middleware for RideGrid services."""

import time
import uuid
from typing import Awaitable, Callable

from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware as StarletteBaseHTTPMiddleware

from .logging import (
    correlation_id,
    request_id,
    with_correlation_id,
    with_request_id,
    get_logger,
)
from .metrics import get_metrics_collector


logger = get_logger(__name__)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware to handle correlation IDs."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # Extract correlation ID from headers or generate new one
        corr_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Set context variables
        with_correlation_id(corr_id)
        with_request_id(req_id)

        # Add to response headers
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = corr_id
        response.headers["X-Request-ID"] = req_id

        return response


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect HTTP metrics."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        start_time = time.time()

        # Execute request
        response = await call_next(request)

        # Record metrics
        duration = time.time() - start_time
        try:
            metrics_collector = get_metrics_collector()
            metrics_collector.record_http_request(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                duration=duration,
            )
        except RuntimeError:
            # Metrics collector not initialized
            pass

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to add structured logging to requests."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        logger.bind(
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params),
            correlation_id=correlation_id.get(),
            request_id=request_id.get(),
        )

        logger.info("Request started")

        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        logger.bind(
            status_code=response.status_code,
            duration_ms=round(duration * 1000, 2),
        )

        if response.status_code >= 400:
            logger.error("Request failed")
        else:
            logger.info("Request completed")

        return response


class TracingMiddleware(BaseHTTPMiddleware):
    """Middleware to add distributed tracing to requests."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        from opentelemetry import trace

        tracer = trace.get_tracer(__name__)
        operation_name = f"{request.method} {request.url.path}"

        with tracer.start_as_current_span(operation_name) as span:
            # Add request attributes to span
            span.set_attribute("http.method", request.method)
            span.set_attribute("http.url", str(request.url))
            span.set_attribute("http.user_agent", request.headers.get("user-agent", ""))
            span.set_attribute("correlation.id", correlation_id.get() or "")
            span.set_attribute("request.id", request_id.get() or "")

            # Execute request
            start_time = time.time()
            response = await call_next(request)
            duration = time.time() - start_time

            # Add response attributes to span
            span.set_attribute("http.status_code", response.status_code)
            span.set_attribute("http.duration_ms", round(duration * 1000, 2))

            if response.status_code >= 400:
                span.set_status(trace.Status(trace.StatusCode.ERROR))

            return response


def create_middleware_stack(app: Starlette) -> None:
    """Add all middleware to a FastAPI/Starlette app."""
    # Order matters - middleware is applied in reverse order of addition
    app.add_middleware(TracingMiddleware)
    app.add_middleware(MetricsMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(CorrelationIdMiddleware)


# Convenience function for adding middleware to FastAPI apps
def add_ridegrid_middleware(app: Starlette) -> None:
    """Add all RideGrid middleware to an app."""
    create_middleware_stack(app)



