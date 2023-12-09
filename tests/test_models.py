import unittest

from src.vinted_scraper.models import VintedImage, VintedItem
from tests.utils import _read_data_from_file


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.data = _read_data_from_file("item_dummy").get("item")
        self.search_data = _read_data_from_file("search_item_dummy").get("items")[0]
        self.item = VintedItem(json_data=self.data)
        self.search_item = VintedItem(json_data=self.search_data)

    def test_photo_deprecation_warning(self):
        """
        Test if a deprecation warning is issued when accessing the deprecated 'photo' attribute,
        and check if the correct value is returned from the 'photos' attribute.
        """

        with self.assertWarns(
            DeprecationWarning, msg="The 'photo' attribute is deprecated."
        ):
            result = self.item.photo
            search_result = self.search_item.photo

        self.assertEqual(VintedImage(self.data.get("photos")[0]), result)
        self.assertEqual(VintedImage(self.search_data.get("photo")), search_result)

    def test_photo_empty_photos(self):
        """
        Test if a deprecation warning is issued when accessing the deprecated 'photo' attribute
        with an empty 'photos' attribute, and check if 'None' is returned.
        """

        none_item = self.item
        none_item.photos = []

        with self.assertWarns(
            DeprecationWarning, msg="The 'photo' attribute is deprecated."
        ):
            result = none_item.photo

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
