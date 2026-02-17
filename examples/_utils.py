# pylint: disable=broad-exception-caught
"""
This is a helper function. It helps avoid code duplication.
"""

import asyncio
import logging
from time import sleep
from typing import Any, Callable


def configure_logging():
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
    """
    Run a function with retry logic and exponential backoff.
    The result of the function is not returned!

    Args:
        main_func (Callable[[], Any]): The main function to execute. Can be sync or async.
        max_retries (int): Maximum number of attempts before giving up.
        is_async (bool): Set to True if main_func is an async function.
        backoff_base (int): The base for exponential backoff (default: 2).
        backoff_cap (int): Maximum number of seconds to wait between retries.

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
            break  # Exit the loop with success
        except Exception as e:
            retries += 1
            if retries == max_retries:
                raise  # Exit the loop with error
            sleep_time = min(backoff_base**retries, backoff_cap)
            logger = logging.getLogger("vinted_scraper")
            logger.warning(
                "Attempt %d failed: %s. Retrying in %d seconds...",
                retries,
                e,
                sleep_time,
            )
            sleep(sleep_time)
