"""
Structured logging infrastructure for SIH26138 Platform.
Ensures transparent, non-fabricated diagnostic outputs across all execution phases.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "sih26138",
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
) -> logging.Logger:
    """
    Configure and return a structured logger.

    Args:
        name: Name of the logger (typically module name or package root).
        level: Logging level (e.g. logging.INFO, logging.DEBUG).
        log_file: Optional path to write log outputs.

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers if already configured
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.propagate = False
    return logger


def get_logger(name: str = "sih26138") -> logging.Logger:
    """Retrieve an existing logger or create one with default settings."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger
