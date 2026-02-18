# pylint: disable=duplicate-code,unused-variable
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
    items = scraper.search(params)  # noqa: F841

    # Items are typed objects with attributes
    # Uncomment to see results:
    # for item in items:
    #     print(f"{item.title} - €{item.price}")


if __name__ == "__main__":
    configure_logging()
    run_with_retries(main)
    print("VintedScraper completed successfully.")
