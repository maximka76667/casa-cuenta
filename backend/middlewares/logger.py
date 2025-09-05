import sys
import os
from loguru import logger
from datetime import datetime


class LoggerConfig:
    def __init__(self):
        # Remove default handler
        logger.remove()

        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)

        # Console handler with colors
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="INFO",
            colorize=True,
        )

        # File handler for all logs
        logger.add(
            "logs/app_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation="00:00",  # Rotate daily
            retention="30 days",  # Keep logs for 30 days
            compression="zip",  # Compress old logs
        )

        # Error file handler
        logger.add(
            "logs/error_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="ERROR",
            rotation="00:00",
            retention="90 days",  # Keep error logs longer
            compression="zip",
        )

        # Performance/monitoring logs
        logger.add(
            "logs/performance_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="INFO",
            rotation="00:00",
            retention="7 days",
            compression="zip",
            filter=lambda record: "PERFORMANCE" in record["message"],
        )


# Initialize logger configuration
config = LoggerConfig()

# Create a custom logger instance
app_logger = logger.bind(name="casa-cuenta")


def log_performance(endpoint: str, duration: float, status_code: int, method: str):
    """Log performance metrics"""
    app_logger.info(
        f"PERFORMANCE | {method} {endpoint} | Duration: {duration:.3f}s | Status: {status_code}"
    )


def log_cache_operation(operation: str, cache_key: str, hit: bool = None):
    """Log cache operations"""
    if hit is not None:
        app_logger.info(f"CACHE | {operation} | Key: {cache_key} | Hit: {hit}")
    else:
        app_logger.info(f"CACHE | {operation} | Key: {cache_key}")


def log_database_operation(operation: str, table: str, duration: float = None):
    """Log database operations"""
    if duration:
        app_logger.info(
            f"DATABASE | {operation} | Table: {table} | Duration: {duration:.3f}s"
        )
    else:
        app_logger.info(f"DATABASE | {operation} | Table: {table}")


def log_rate_limit(client_id: str, endpoint: str, remaining: int):
    """Log rate limiting events"""
    if remaining <= 5:  # Log when close to limit
        app_logger.warning(
            f"RATE_LIMIT | Client: {client_id} | Endpoint: {endpoint} | Remaining: {remaining}"
        )


def log_auth_event(event: str, user_id: str = None, success: bool = True):
    """Log authentication events"""
    level = "info" if success else "warning"
    getattr(app_logger, level)(f"AUTH | {event} | User: {user_id} | Success: {success}")


def get_logger():
    """Get the configured logger instance"""
    return app_logger
