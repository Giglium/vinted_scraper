# pylint: disable=broad-exception-caught
"""Utility functions for vinted_scraper examples.

This module provides helper functions used across example scripts:
- Logging configuration
- Retry logic with exponential backoff for handling API rate limits
"""

import asyncio
import logging
from time import sleep
from typing import Any, Callable


def configure_logging() -> None:
    """Configure logging for vinted_scraper examples."""
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
    logger = logging.getLogger("vinted_scraper")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.propagate = False


def run_with_retries(
    main_func: Callable[[], Any],
    max_retries: int = 5,
    is_async: bool = False,
    backoff_base: int = 2,
    backoff_cap: int = 32,
) -> None:
    """Run a function with retry logic and exponential backoff.

    Executes the provided function and retries on failure with exponential
    backoff. These utilities are specifically designed for GitHub Actions and CI/CD
    environments where parallel API calls may cause rate limiting.

    Args:
        main_func: The function to execute (sync or async).
        max_retries: Maximum number of retry attempts (default: 5).
        is_async: Set to True if main_func is an async function (default: False).
        backoff_base: Base for exponential backoff calculation (default: 2).
        backoff_cap: Maximum seconds to wait between retries (default: 32).

    Raises:
        Exception: Re-raises the last exception if all retries fail.
    """
    retries = 0
    while retries < max_retries:
        try:
            if is_async:
                asyncio.run(main_func())
            else:
                main_func()
            break  # Exit on success
        except Exception as e:
            retries += 1
            if retries == max_retries:
                raise  # Re-raise after all retries exhausted
            sleep_time = min(backoff_base**retries, backoff_cap)
            logger = logging.getLogger("vinted_scraper")
            logger.warning(
                "Attempt %d failed: %s. Retrying in %d seconds...",
                retries,
                e,
                sleep_time,
            )
            sleep(sleep_time)
