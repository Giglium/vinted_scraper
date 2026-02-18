# pylint: disable=duplicate-code,unused-variable
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
    response = await wrapper.search(params)  # noqa: F841

    # Response is a dictionary with "items" key
    # Uncomment to see results:
    # for item in response["items"]:
    #     print(f"{item['title']} - €{item['price']}")


if __name__ == "__main__":
    configure_logging()
    run_with_retries(main, is_async=True)
    print("AsyncVintedWrapper completed successfully.")
