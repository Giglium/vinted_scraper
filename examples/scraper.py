# pylint: disable=duplicate-code
"""
This is an example script for running the VintedScraper.
Since GitHub Actions perform too many parallel API calls, we added retry logic to handle errors.
"""

from examples._utils import configure_logging, run_with_retries
from vinted_scraper import VintedScraper


def main() -> None:
    """Run a sample async search using VintedScraper."""
    scraper = VintedScraper("https://www.vinted.com")
    params = {"search_text": "board games"}
    _ = scraper.search(params)


if __name__ == "__main__":
    configure_logging()
    run_with_retries(main)
    print("VintedScraper completed successfully.")
