"""
Centralized logging configuration for the application.
"""

import logging
import sys

from app.core.config import settings
from app.core.constants import LOG_FORMAT, DATE_FORMAT


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Create and configure a reusable application logger.

    Args:
        name: The name of the logger, defaults to the project name.

    Returns:
        logging.Logger: A configured logger instance.
    """

    if name is None:
        name = settings.project_name
    logger = logging.getLogger(name)

    # Convert string log level from settings to logging integer constant
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Prevent duplicate handlers if logger is initialized multiple times
    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)

        formatter = logging.Formatter(
            fmt=LOG_FORMAT,
            datefmt=DATE_FORMAT,
        )
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        
        # Prevent propagation to the root logger to avoid double logging
        logger.propagate = False

    return logger


# Default application logger instance
logger = get_logger()
