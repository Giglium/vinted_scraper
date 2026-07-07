# pylint: disable=duplicate-code
"""AsyncVintedWrapper asynchronous example."""

from examples._utils import configure_logging, run_with_retries
from vinted_scraper import AsyncVintedWrapper


async def main() -> None:
    """Run a sample async search using AsyncVintedWrapper."""
    # Initialize async wrapper using factory method
    wrapper = await AsyncVintedWrapper.create("https://www.vinted.com")

    # Define search parameters
    params = {"search_text": "board games"}

    # Perform async search - returns Dict[str, Any]
    response = await wrapper.search(params)

    # Fetch item details for the first result
    if response["items"]:
        first = response["items"][0]
        item_data = await wrapper.item(str(first["id"]))
        print(f"Title: {item_data.get('title')}")
        print(f"Description: {item_data.get('description')}")


if __name__ == "__main__":
    configure_logging()
    run_with_retries(main, is_async=True)
    print("AsyncVintedWrapper completed successfully.")
