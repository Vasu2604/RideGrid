"""Metrics collection for RideGrid services."""

import time
from contextlib import contextmanager
from typing import Dict, Optional

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    Summary,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from prometheus_client.openmetrics.exposition import generate_latest as generate_latest_om


class MetricsCollector:
    """Centralized metrics collection for RideGrid services."""

    def __init__(self, service_name: str, enable_otel: bool = True):
        self.service_name = service_name
        self.enable_otel = enable_otel

        # Prometheus metrics
        self.registry = CollectorRegistry()

        # Request metrics
        self.http_requests_total = Counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status_code"],
            registry=self.registry,
        )

        self.http_request_duration_seconds = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "endpoint"],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
            registry=self.registry,
        )

        # gRPC metrics
        self.grpc_requests_total = Counter(
            "grpc_requests_total",
            "Total gRPC requests",
            ["service", "method", "status"],
            registry=self.registry,
        )

        self.grpc_request_duration_seconds = Histogram(
            "grpc_request_duration_seconds",
            "gRPC request duration in seconds",
            ["service", "method"],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
            registry=self.registry,
        )

        # Business metrics
        self.rides_created_total = Counter(
            "rides_created_total",
            "Total rides created",
            ["ride_type"],
            registry=self.registry,
        )

        self.drivers_active = Gauge(
            "drivers_active",
            "Number of active drivers",
            registry=self.registry,
        )

        self.matching_duration_seconds = Histogram(
            "matching_duration_seconds",
            "Time to find driver matches",
            buckets=[0.001, 0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
            registry=self.registry,
        )

        # Kafka metrics
        self.kafka_messages_produced_total = Counter(
            "kafka_messages_produced_total",
            "Total Kafka messages produced",
            ["topic"],
            registry=self.registry,
        )

        self.kafka_messages_consumed_total = Counter(
            "kafka_messages_consumed_total",
            "Total Kafka messages consumed",
            ["topic", "group_id"],
            registry=self.registry,
        )

        self.kafka_consumer_lag = Gauge(
            "kafka_consumer_lag",
            "Kafka consumer lag",
            ["topic", "partition", "group_id"],
            registry=self.registry,
        )

        # Database metrics
        self.db_connections_active = Gauge(
            "db_connections_active",
            "Active database connections",
            registry=self.registry,
        )

        self.db_query_duration_seconds = Histogram(
            "db_query_duration_seconds",
            "Database query duration",
            ["operation"],
            buckets=[0.001, 0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
            registry=self.registry,
        )

        # Redis metrics
        self.redis_operations_total = Counter(
            "redis_operations_total",
            "Total Redis operations",
            ["operation", "status"],
            registry=self.registry,
        )

        self.redis_operation_duration_seconds = Histogram(
            "redis_operation_duration_seconds",
            "Redis operation duration",
            ["operation"],
            buckets=[0.001, 0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
            registry=self.registry,
        )

        # Error metrics
        self.errors_total = Counter(
            "errors_total",
            "Total errors",
            ["service", "error_type"],
            registry=self.registry,
        )

        # OTel setup
        if enable_otel:
            self._setup_otel()

    def _setup_otel(self):
        """Set up OpenTelemetry metrics."""
        resource = Resource.create({"service.name": self.service_name})
        reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(
                endpoint="http://otel-collector:4317",
                insecure=True,
            ),
            export_interval_millis=5000,
        )
        provider = MeterProvider(resource=resource, metric_readers=[reader])
        metrics.set_meter_provider(provider)

        self.meter = metrics.get_meter(__name__)
        self.otel_request_duration = self.meter.create_histogram(
            name="request.duration",
            description="Request duration in seconds",
            unit="s",
        )

    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics."""
        self.http_requests_total.labels(
            method=method, endpoint=endpoint, status_code=status_code
        ).inc()

        self.http_request_duration_seconds.labels(
            method=method, endpoint=endpoint
        ).observe(duration)

        if self.enable_otel:
            self.otel_request_duration.record(duration)

    def record_grpc_request(self, service: str, method: str, status: str, duration: float):
        """Record gRPC request metrics."""
        self.grpc_requests_total.labels(
            service=service, method=method, status=status
        ).inc()

        self.grpc_request_duration_seconds.labels(
            service=service, method=method
        ).observe(duration)

    def record_ride_created(self, ride_type: str):
        """Record ride creation."""
        self.rides_created_total.labels(ride_type=ride_type).inc()

    def set_drivers_active(self, count: int):
        """Set active drivers count."""
        self.drivers_active.set(count)

    def record_matching_duration(self, duration: float):
        """Record matching duration."""
        self.matching_duration_seconds.observe(duration)

    def record_kafka_message_produced(self, topic: str):
        """Record Kafka message production."""
        self.kafka_messages_produced_total.labels(topic=topic).inc()

    def record_kafka_message_consumed(self, topic: str, group_id: str):
        """Record Kafka message consumption."""
        self.kafka_messages_consumed_total.labels(topic=topic, group_id=group_id).inc()

    def set_kafka_consumer_lag(self, topic: str, partition: int, group_id: str, lag: int):
        """Set Kafka consumer lag."""
        self.kafka_consumer_lag.labels(
            topic=topic, partition=str(partition), group_id=group_id
        ).set(lag)

    def record_db_query(self, operation: str, duration: float):
        """Record database query metrics."""
        self.db_query_duration_seconds.labels(operation=operation).observe(duration)

    def record_redis_operation(self, operation: str, status: str, duration: float):
        """Record Redis operation metrics."""
        self.redis_operations_total.labels(operation=operation, status=status).inc()
        self.redis_operation_duration_seconds.labels(operation=operation).observe(duration)

    def record_error(self, error_type: str):
        """Record error occurrence."""
        self.errors_total.labels(service=self.service_name, error_type=error_type).inc()

    def get_prometheus_metrics(self) -> bytes:
        """Get metrics in Prometheus format."""
        return generate_latest(self.registry)

    def get_openmetrics(self) -> bytes:
        """Get metrics in OpenMetrics format."""
        return generate_latest_om(self.registry)


class Timer:
    """Context manager for timing operations."""

    def __init__(self, metrics_collector: MetricsCollector, operation_name: str):
        self.metrics_collector = metrics_collector
        self.operation_name = operation_name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            if hasattr(self.metrics_collector, f"record_{self.operation_name}"):
                getattr(self.metrics_collector, f"record_{self.operation_name}")(duration)
            else:
                # Generic timing recording
                getattr(self.metrics_collector, "record_generic_duration", lambda d: None)(duration)


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector."""
    if _metrics_collector is None:
        raise RuntimeError("Metrics collector not initialized")
    return _metrics_collector


def init_metrics_collector(service_name: str, enable_otel: bool = True) -> MetricsCollector:
    """Initialize the global metrics collector."""
    global _metrics_collector
    _metrics_collector = MetricsCollector(service_name, enable_otel)
    return _metrics_collector



