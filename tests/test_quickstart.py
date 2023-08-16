import unittest

from src.vinted_scraper import get_item, get_raw_item, raw_search, search


class MyTestCase(unittest.TestCase):
    def test_quick_start(self):
        """
        Ensure that the function doesn't raise any exceptions
        """
        try:
            params = {"search_text": "board games"}
            items = search("https://www.vinted.com/catalog", params)
            item = items[0]
            get_item(item.url)
        except Exception as e:
            self.fail(f"Quick raised an exception: {e}")

    def test_raw_quick_start(self):
        """
        Ensure that the function doesn't raise any exceptions
        """
        try:
            params = {"search_text": "board games"}
            items = raw_search("https://www.vinted.com/catalog", params)
            item = items[0]
            get_raw_item(item["url"])
        except Exception as e:
            self.fail(f"Quick raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()
