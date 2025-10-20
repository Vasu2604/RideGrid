"""Configuration management for RideGrid services."""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Base settings for RideGrid services."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service
    service_name: str = Field(default="ridegrid-service")
    environment: str = Field(default="development")
    log_level: str = Field(default="INFO")
    debug: bool = Field(default=False)

    # Database
    database_url: Optional[str] = Field(default=None)
    db_pool_min_size: int = Field(default=5)
    db_pool_max_size: int = Field(default=20)

    # Redis
    redis_url: Optional[str] = Field(default=None)
    redis_max_connections: int = Field(default=50)

    # Kafka
    kafka_bootstrap_servers: Optional[str] = Field(default=None)
    kafka_enable_idempotence: bool = Field(default=True)
    kafka_transactional_id: Optional[str] = Field(default=None)

    # OpenTelemetry
    otel_exporter_otlp_endpoint: Optional[str] = Field(default=None)
    otel_service_name: Optional[str] = Field(default=None)

    # JWT
    jwt_secret: str = Field(default="dev-secret-change-in-production")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiry_minutes: int = Field(default=60)

    # Rate Limiting
    rate_limit_requests: int = Field(default=100)
    rate_limit_window_seconds: int = Field(default=60)

    # CORS
    cors_origins: str = Field(default="*")

    # Health check
    health_check_interval: int = Field(default=30)

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment.lower() == "development"
