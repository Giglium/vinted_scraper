# pylint: disable=missing-module-docstring,missing-class-docstring
import unittest

from src.vinted_scraper.models import VintedItem

from .utils import read_data_from_file


class TestUtils(unittest.TestCase):

    def setUp(self):
        self.data = read_data_from_file("item_dummy").get("item")
        self.search_data = read_data_from_file("search_item_dummy").get("items")[0]
        self.item = VintedItem(json_data=self.data)
        self.search_item = VintedItem(json_data=self.search_data)


if __name__ == "__main__":
    unittest.main()
