"""Custom error classes for RideGrid services."""

from typing import Any, Dict, Optional

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response format."""

    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None
    request_id: Optional[str] = None


class RideGridError(Exception):
    """Base exception class for RideGrid errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}

    def to_response(self) -> ErrorResponse:
        """Convert to error response format."""
        from .logging import correlation_id, request_id

        return ErrorResponse(
            error=self.error_code,
            message=self.message,
            details=self.details,
            correlation_id=correlation_id.get(),
            request_id=request_id.get(),
        )


class ValidationError(RideGridError):
    """Raised when request validation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=details,
        )


class NotFoundError(RideGridError):
    """Raised when a requested resource is not found."""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} with ID '{identifier}' not found",
            error_code="NOT_FOUND",
            status_code=404,
        )
        self.resource = resource
        self.identifier = identifier


class ConflictError(RideGridError):
    """Raised when there's a conflict (e.g., duplicate resource)."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=409,
            details=details,
        )


class UnauthorizedError(RideGridError):
    """Raised when authentication is required."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            error_code="UNAUTHORIZED",
            status_code=401,
        )


class ForbiddenError(RideGridError):
    """Raised when access is forbidden."""

    def __init__(self, message: str = "Access forbidden"):
        super().__init__(
            message=message,
            error_code="FORBIDDEN",
            status_code=403,
        )


class RateLimitError(RideGridError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
        )


class ServiceUnavailableError(RideGridError):
    """Raised when a service is temporarily unavailable."""

    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(
            message=message,
            error_code="SERVICE_UNAVAILABLE",
            status_code=503,
        )


class DatabaseError(RideGridError):
    """Raised when database operations fail."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=500,
            details=details,
        )


class KafkaError(RideGridError):
    """Raised when Kafka operations fail."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="KAFKA_ERROR",
            status_code=500,
            details=details,
        )


class RedisError(RideGridError):
    """Raised when Redis operations fail."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="REDIS_ERROR",
            status_code=500,
            details=details,
        )


class ExternalServiceError(RideGridError):
    """Raised when external services fail."""

    def __init__(self, service: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"External service '{service}' error: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=502,
            details={"service": service, **(details or {})},
        )




