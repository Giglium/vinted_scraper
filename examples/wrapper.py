# pylint: disable=duplicate-code
"""VintedWrapper synchronous example."""

from examples._utils import configure_logging, run_with_retries
from vinted_scraper import VintedWrapper


def main() -> None:
    """Run a sample search using VintedWrapper."""
    # Initialize wrapper with base URL
    wrapper = VintedWrapper("https://www.vinted.com")

    # Define search parameters
    params = {"search_text": "board games"}

    # Perform search - returns Dict[str, Any]
    response = wrapper.search(params)

    # Fetch item details for the first result
    if response["items"]:
        first = response["items"][0]
        item_data = wrapper.item(str(first["id"]))
        print(f"Title: {item_data.get('title')}")
        print(f"Description: {item_data.get('description')}")


if __name__ == "__main__":
    configure_logging()
    run_with_retries(main)
    print("VintedWrapper completed successfully.")
