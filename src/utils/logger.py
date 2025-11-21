"""Logging configuration for BLOCKS MCP Server."""

import logging
import logging.handlers
from datetime import datetime
from pathlib import Path


def get_logger(name: str = "blocks-mcp-server") -> logging.Logger:
    """
    Get a logger instance that logs to both files appropriately.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    return logger

    if not logger.handlers:
        # Create log directory if it doesn't exist
        log_dir = "mcp-server-logs"
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)

        # Get current date for filename
        date_str = datetime.now().strftime("%Y-%m-%d")

        # File paths
        info_file = log_path / f"mcp-info-{date_str}.log"
        error_file = log_path / f"mcp-error-{date_str}.log"

        # Create formatters
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        )

        # Info handler (DEBUG, INFO, WARNING levels)
        info_handler = logging.handlers.TimedRotatingFileHandler(
            info_file, when="midnight", interval=1, backupCount=7, encoding="utf-8"
        )
        info_handler.setLevel(logging.DEBUG)
        info_handler.setFormatter(formatter)

        # Filter to only allow DEBUG, INFO, and WARNING levels
        class InfoFilter(logging.Filter):
            def filter(self, record):
                return record.levelno < logging.ERROR

        info_handler.addFilter(InfoFilter())

        # Error handler (ERROR and CRITICAL levels)
        error_handler = logging.handlers.TimedRotatingFileHandler(
            error_file, when="midnight", interval=1, backupCount=7, encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)

        # Add handlers directly to the logger
        logger.addHandler(info_handler)
        logger.addHandler(error_handler)
        logger.setLevel(logging.DEBUG)

        # Prevent propagation to avoid duplicate logs
        logger.propagate = False

    return logger
