from fastapi import Request, Response
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
import time
from middlewares.logger import get_logger, log_performance
from typing import Callable

logger = get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status_code"]
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

ACTIVE_REQUESTS = Gauge("http_requests_active", "Number of active HTTP requests")

CACHE_OPERATIONS = Counter(
    "cache_operations_total", "Total cache operations", ["operation", "result"]
)

DATABASE_OPERATIONS = Counter(
    "database_operations_total", "Total database operations", ["operation", "table"]
)

DATABASE_DURATION = Histogram(
    "database_operation_duration_seconds",
    "Database operation duration in seconds",
    ["operation", "table"],
)

RATE_LIMIT_HITS = Counter(
    "rate_limit_hits_total", "Total rate limit hits", ["endpoint"]
)


async def monitoring_middleware(request: Request, call_next: Callable) -> Response:
    """Middleware to collect metrics and log performance"""
    start_time = time.time()

    # Track active requests
    ACTIVE_REQUESTS.inc()

    try:
        # Process the request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Extract metrics
        method = request.method
        endpoint = request.url.path
        status_code = response.status_code

        # Update Prometheus metrics
        REQUEST_COUNT.labels(
            method=method, endpoint=endpoint, status_code=status_code
        ).inc()

        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

        # Log performance
        log_performance(endpoint, duration, status_code, method)

        # Log slow requests
        if duration > 1.0:  # Log requests taking more than 1 second
            logger.warning(
                f"SLOW_REQUEST | {method} {endpoint} | Duration: {duration:.3f}s | Status: {status_code}"
            )

        return response

    except Exception as e:
        # Log errors
        duration = time.time() - start_time
        logger.error(
            f"REQUEST_ERROR | {request.method} {request.url.path} | "
            f"Duration: {duration:.3f}s | Error: {str(e)}"
        )

        # Update error metrics
        REQUEST_COUNT.labels(
            method=request.method, endpoint=request.url.path, status_code=500
        ).inc()

        raise

    finally:
        # Decrement active requests
        ACTIVE_REQUESTS.dec()


def track_cache_operation(operation: str, hit: bool):
    """Track cache operations for monitoring"""
    result = "hit" if hit else "miss"
    CACHE_OPERATIONS.labels(operation=operation, result=result).inc()


def track_database_operation(operation: str, table: str, duration: float):
    """Track database operations for monitoring"""
    DATABASE_OPERATIONS.labels(operation=operation, table=table).inc()
    DATABASE_DURATION.labels(operation=operation, table=table).observe(duration)


def track_rate_limit_hit(endpoint: str):
    """Track rate limit hits"""
    RATE_LIMIT_HITS.labels(endpoint=endpoint).inc()


async def metrics_endpoint():
    """Endpoint to expose Prometheus metrics"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
