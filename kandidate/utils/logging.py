"""Centralized logging helpers used throughout the project."""
from __future__ import annotations

import logging
from logging import Logger

from kandidate.models.config import LoggingConfig

_LOGGER_INITIALIZED = False


def configure_logging(config: LoggingConfig) -> Logger:
    """Configure and return the root logger."""

    global _LOGGER_INITIALIZED
    level = getattr(logging, config.level.upper(), logging.INFO)
    format_str = (
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        if not config.json_format
        else '{"time": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}'
    )
    logging.basicConfig(level=level, format=format_str)
    _LOGGER_INITIALIZED = True
    return logging.getLogger("kandidate")


def get_logger(name: str) -> Logger:
    """Return a module-level logger, ensuring configuration happened."""

    if not _LOGGER_INITIALIZED:
        configure_logging(LoggingConfig())
    return logging.getLogger(name)
