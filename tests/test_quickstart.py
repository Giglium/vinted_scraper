import unittest

from src.vinted_scraper.models import VintedItem
from src.vinted_scraper.vintedScraper import VintedScraper
from src.vinted_scraper.vintedWrapper import VintedWrapper


class TestQuickstarts(unittest.TestCase):
    def test_raw_quick_start(self):
        """
        Ensure that the wrapper quickstart doesn't raise any exceptions
        """
        try:
            wrapper = VintedWrapper("https://www.vinted.com")
            params = {"search_text": "board games"}
            items = wrapper.search(params)
            print(VintedItem(items["items"][0]))
            wrapper.item(items["items"][0]["id"])
        except Exception as e:
            self.fail(f"Quick raised an exception: {e}")

    def test_quick_start(self):
        """
        Ensure that the wrapper quickstart doesn't raise any exceptions
        """
        try:
            scraper = VintedScraper("https://www.vinted.com")
            params = {"search_text": "board games"}
            scraper.search(params)
        except Exception as e:
            self.fail(f"Quick raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()
