# pylint: disable=duplicate-code
"""AsyncVintedScraper asynchronous example."""

from examples._utils import configure_logging, run_with_retries
from vinted_scraper import AsyncVintedScraper


async def main() -> None:
    """Run a sample async search using AsyncVintedScraper."""
    # Initialize async scraper using factory method
    scraper = await AsyncVintedScraper.create("https://www.vinted.com")

    # Define search parameters
    params = {"search_text": "board games"}

    # Perform async search - returns List[VintedItem]
    items = await scraper.search(params)

    # Enrich first item with description from the item page
    if items:
        first = items[0]
        await scraper.enrich(first)
        print(f"Title: {first.title}")
        print(f"Description: {first.description}")


if __name__ == "__main__":
    configure_logging()
    run_with_retries(main, is_async=True)
    print("AsyncVintedScraper completed successfully.")
