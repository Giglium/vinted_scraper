"""Vinted Scraper - A Python package for scraping Vinted marketplace.

This package provides both synchronous and asynchronous clients for interacting
with the Vinted API. Choose between typed model responses (Scraper) or raw JSON
responses (Wrapper).

Classes:
    VintedScraper: Synchronous client with typed VintedItem responses.
    VintedWrapper: Synchronous client with raw JSON responses.
    AsyncVintedScraper: Asynchronous client with typed VintedItem responses.
    AsyncVintedWrapper: Asynchronous client with raw JSON responses.

    Examples:
        See https://github.com/Giglium/vinted_scraper/tree/main/examples
"""

from ._async_scraper import AsyncVintedScraper
from ._async_wrapper import AsyncVintedWrapper
from ._scraper import VintedScraper
from ._wrapper import VintedWrapper

__all__ = ["AsyncVintedWrapper", "VintedWrapper", "AsyncVintedScraper", "VintedScraper"]
