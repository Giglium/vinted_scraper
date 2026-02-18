# pylint: disable=duplicate-code,unused-variable
"""AsyncVintedScraper asynchronous example."""

from vinted_scraper import AsyncVintedScraper

from ._utils import configure_logging, run_with_retries


async def main() -> None:
    """Run a sample async search using AsyncVintedScraper."""
    # Initialize async scraper using factory method
    scraper = await AsyncVintedScraper.create("https://www.vinted.com")

    # Define search parameters
    params = {"search_text": "board games"}

    # Perform async search - returns List[VintedItem]
    items = await scraper.search(params)  # noqa: F841

    # Items are typed objects with attributes
    # Uncomment to see results:
    # for item in items:
    #     print(f"{item.title} - €{item.price}")


if __name__ == "__main__":
    configure_logging()
    run_with_retries(main, is_async=True)
    print("AsyncVintedScraper completed successfully.")
