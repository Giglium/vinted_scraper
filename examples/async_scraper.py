# pylint: disable=duplicate-code
"""
This is an example script for running the AsyncVintedScraper.
Since GitHub Actions perform too many parallel API calls, we added retry logic to handle errors.
"""

from vinted_scraper import AsyncVintedScraper

from ._utils import configure_logging, run_with_retries


async def main() -> None:
    """Run a sample async search using AsyncVintedScraper."""
    scraper = await AsyncVintedScraper.create("https://www.vinted.com")
    params = {"search_text": "board games"}
    _ = await scraper.search(params)


if __name__ == "__main__":
    configure_logging()
    run_with_retries(main, is_async=True)
    print("AsyncVintedScraper completed successfully.")
