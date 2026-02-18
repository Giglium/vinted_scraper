"""Examples package for vinted_scraper.

This package contains example scripts demonstrating how to use vinted_scraper
for both synchronous and asynchronous operations.

Examples:
    - scraper.py: Synchronous VintedScraper usage
    - wrapper.py: Synchronous VintedWrapper usage
    - async_scraper.py: Asynchronous AsyncVintedScraper usage
    - async_wrapper.py: Asynchronous AsyncVintedWrapper usage
"""

import os
import sys

# https://stackoverflow.com/a/59732673
PROJECT_PATH = os.getcwd()
SOURCE_PATH = os.path.join(PROJECT_PATH, "src")
sys.path.append(SOURCE_PATH)
