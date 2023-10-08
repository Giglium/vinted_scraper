import unittest

from src.vinted_scraper.VintedWrapper import VintedWrapper


class TestQuickstarts(unittest.TestCase):
    def test_raw_quick_start(self):
        """
        Ensure that the wrapper quickstart doesn't raise any exceptions
        """
        try:
            wrapper = VintedWrapper("https://www.vinted.com")
            params = {"search_text": "board games"}
            items = wrapper.search(params)
            wrapper.item(items["items"][0]["id"])
        except Exception as e:
            self.fail(f"Quick raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()
