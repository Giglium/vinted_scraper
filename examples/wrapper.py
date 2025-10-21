"""
This is an example script for running the VintedWrapper.
Since GitHub Actions perform too many parallel API calls, we added retry logic to handle errors.
"""

from examples._utils import run_with_retries
from vinted_scraper import VintedWrapper


def main() -> None:
    """Run a sample async search using VintedWrapper."""
    scraper = VintedWrapper("https://www.vinted.com")
    params = {"search_text": "board games"}
    _ = scraper.search(params)


if __name__ == "__main__":
    run_with_retries(main)
    print("VintedWrapper completed successfully.")
