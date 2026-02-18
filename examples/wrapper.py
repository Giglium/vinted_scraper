# pylint: disable=duplicate-code,unused-variable
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
    response = wrapper.search(params)  # noqa: F841

    # Response is a dictionary with "items" key
    # Uncomment to see results:
    # for item in response["items"]:
    #     print(f"{item['title']} - €{item['price']}")


if __name__ == "__main__":
    configure_logging()
    run_with_retries(main)
    print("VintedWrapper completed successfully.")
