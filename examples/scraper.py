# pylint: disable=duplicate-code
"""VintedScraper synchronous example."""

from examples._utils import configure_logging, run_with_retries
from vinted_scraper import VintedScraper


def main() -> None:
    """Run a sample search using VintedScraper."""
    # Initialize scraper with base URL
    scraper = VintedScraper("https://www.vinted.com")

    # Define search parameters
    params = {"search_text": "board games"}

    # Perform search - returns List[VintedItem]
    items = scraper.search(params)

    # Enrich first item with description from the item page
    if items:
        first = items[0]
        scraper.enrich(first)
        print(f"Title: {first.title}")
        print(f"Description: {first.description}")


if __name__ == "__main__":
    configure_logging()
    run_with_retries(main)
    print("VintedScraper completed successfully.")
