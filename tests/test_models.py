# jscpd:ignore-start
# pylint: disable=duplicate-code
"""Tests for VintedItem and related model classes."""

import unittest

from src.vinted_scraper.models import VintedBrand, VintedImage, VintedItem, VintedUser

from .utils import read_data_from_file

# Test constants
TEST_USER_ID = 123
TEST_BRAND_ID = 456
TEST_IMAGE_ID = 789
TEST_ITEM_ID = 1


class TestVintedModels(unittest.TestCase):
    """Test suite for VintedItem model and related models."""

    def setUp(self):
        """Set up test fixtures with sample item data."""
        self.data = read_data_from_file("item_dummy").get("item")
        self.search_data = read_data_from_file("search_items_dummy").get("items")[0]
        self.item = VintedItem(json_data=self.data)
        self.search_item = VintedItem(json_data=self.search_data)

    def test_vinted_item_with_none(self):
        """Test VintedItem handles None input gracefully."""
        item = VintedItem(json_data=None)
        self.assertIsNone(item.id)

    def test_vinted_item_with_user(self):
        """Test VintedItem correctly parses user data into VintedUser object."""
        data = {"id": TEST_ITEM_ID, "user": {"id": TEST_USER_ID, "login": "testuser"}}
        item = VintedItem(json_data=data)
        self.assertIsInstance(item.user, VintedUser)
        self.assertEqual(item.user.id, TEST_USER_ID)

    def test_vinted_item_with_photo(self):
        """Test VintedItem converts single photo to list of VintedImage."""
        data = {
            "id": TEST_ITEM_ID,
            "photo": {"id": TEST_IMAGE_ID, "url": "http://example.com/photo.jpg"},
        }
        item = VintedItem(json_data=data)
        self.assertIsInstance(item.photos, list)
        self.assertEqual(len(item.photos), 1)
        self.assertIsInstance(item.photos[0], VintedImage)
        self.assertEqual(item.photos[0].id, TEST_IMAGE_ID)

    def test_vinted_item_with_photos(self):
        """Test VintedItem correctly parses multiple photos."""
        data = {
            "id": TEST_ITEM_ID,
            "photos": [
                {"id": TEST_IMAGE_ID, "url": "http://example.com/photo1.jpg"},
                {"id": TEST_IMAGE_ID + 1, "url": "http://example.com/photo2.jpg"},
            ],
        }
        item = VintedItem(json_data=data)
        self.assertIsInstance(item.photos, list)
        self.assertEqual(len(item.photos), 2)
        self.assertEqual(item.photos[0].id, TEST_IMAGE_ID)
        self.assertEqual(item.photos[1].id, TEST_IMAGE_ID + 1)

    def test_vinted_item_with_brand_dto(self):
        """Test VintedItem parses brand_dto into VintedBrand object."""
        data = {"id": TEST_ITEM_ID, "brand_dto": {"id": TEST_BRAND_ID, "title": "Nike"}}
        item = VintedItem(json_data=data)
        self.assertIsInstance(item.brand, VintedBrand)
        self.assertEqual(item.brand.id, TEST_BRAND_ID)
        self.assertEqual(item.brand.title, "Nike")

    def test_vinted_item_with_brand_title(self):
        """Test VintedItem creates VintedBrand from brand_title string."""
        data = {"id": TEST_ITEM_ID, "brand_title": "Adidas"}
        item = VintedItem(json_data=data)
        self.assertIsInstance(item.brand, VintedBrand)
        self.assertEqual(item.brand.title, "Adidas")

    def test_vinted_item_price_dict(self):
        """Test VintedItem extracts price and currency from dict."""
        data = {
            "id": TEST_ITEM_ID,
            "price": {"amount": "10.50", "currency_code": "EUR"},
        }
        item = VintedItem(json_data=data)
        self.assertAlmostEqual(item.price, 10.50, places=2)
        self.assertEqual(item.currency, "EUR")

    def test_vinted_item_price_string(self):
        """Test VintedItem parses price from string."""
        data = {"id": TEST_ITEM_ID, "price": "15.99"}
        item = VintedItem(json_data=data)
        self.assertAlmostEqual(item.price, 15.99, places=2)

    def test_vinted_item_service_fee_dict(self):
        """Test VintedItem extracts service_fee from dict."""
        data = {"id": TEST_ITEM_ID, "service_fee": {"amount": "1.50"}}
        item = VintedItem(json_data=data)
        self.assertAlmostEqual(item.service_fee, 1.50, places=2)

    def test_vinted_item_service_fee_string(self):
        """Test VintedItem parses service_fee from string."""
        data = {"id": TEST_ITEM_ID, "service_fee": "2.00"}
        item = VintedItem(json_data=data)
        self.assertAlmostEqual(item.service_fee, 2.00, places=2)

    def test_vinted_item_total_item_price_dict(self):
        """Test VintedItem extracts total_item_price from dict."""
        data = {"id": TEST_ITEM_ID, "total_item_price": {"amount": "12.00"}}
        item = VintedItem(json_data=data)
        self.assertAlmostEqual(item.total_item_price, 12.00, places=2)

    def test_vinted_item_total_item_price_string(self):
        """Test VintedItem parses total_item_price from string."""
        data = {"id": TEST_ITEM_ID, "total_item_price": "13.50"}
        item = VintedItem(json_data=data)
        self.assertAlmostEqual(item.total_item_price, 13.50, places=2)

    def test_vinted_user_initialization(self):
        """Test VintedUser initializes correctly from JSON data."""
        user_data = {"id": TEST_USER_ID, "login": "testuser", "business": True}
        user = VintedUser(json_data=user_data)
        self.assertEqual(user.id, TEST_USER_ID)
        self.assertEqual(user.login, "testuser")

    def test_vinted_brand_initialization(self):
        """Test VintedBrand initializes correctly from JSON data."""
        brand_data = {"id": TEST_BRAND_ID, "title": "TestBrand"}
        brand = VintedBrand(json_data=brand_data)
        self.assertEqual(brand.id, TEST_BRAND_ID)
        self.assertEqual(brand.title, "TestBrand")

    def test_vinted_image_initialization(self):
        """Test VintedImage initializes correctly from JSON data."""
        image_data = {"id": TEST_IMAGE_ID, "url": "http://example.com/image.jpg"}
        image = VintedImage(json_data=image_data)
        self.assertEqual(image.id, TEST_IMAGE_ID)
        self.assertEqual(image.url, "http://example.com/image.jpg")

    def test_vinted_item_with_empty_photos_list(self):
        """Test VintedItem handles empty photos list."""
        data = {"id": TEST_ITEM_ID, "photos": []}
        item = VintedItem(json_data=data)
        self.assertIsInstance(item.photos, list)
        self.assertEqual(len(item.photos), 0)

    def test_vinted_item_price_invalid_format(self):
        """Test VintedItem raises ValueError for invalid price format."""
        data = {"id": TEST_ITEM_ID, "price": "invalid"}
        with self.assertRaises(ValueError) as ctx:
            VintedItem(json_data=data)
        self.assertIsNotNone(ctx.exception)


if __name__ == "__main__":
    unittest.main()
# jscpd:ignore-end
