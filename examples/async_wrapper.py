"""
This is an example script for running the AsyncVintedWrapper.
Since GitHub Actions perform too many parallel API calls, we added retry logic to handle errors.
"""

from examples._utils import run_with_retries
from vinted_scraper import AsyncVintedWrapper


async def main() -> None:
    """Run a sample async search using AsyncVintedScraper."""
    scraper = await AsyncVintedWrapper.create("https://www.vinted.com")
    params = {"search_text": "board games"}
    _ = await scraper.search(params)


if __name__ == "__main__":
    run_with_retries(main, is_async=True)
    print("AsyncVintedWrapper completed successfully.")
