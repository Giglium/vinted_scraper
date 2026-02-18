# pylint: disable=no-member
"""
Test the VintedJsonModel class
"""

import unittest

from src.vinted_scraper.models import VintedJsonModel


class TestVintedJsonModel(unittest.TestCase):
    """Test VintedJsonModel class"""

    def test_initialization_with_none(self):
        """Test VintedJsonModel initializes with None json_data"""
        base = VintedJsonModel(json_data=None)
        self.assertIsNone(base.json_data)

    def test_initialization_with_data(self):
        """Test VintedJsonModel initializes with json_data"""
        data = {"key": "value", "number": 42}
        base = VintedJsonModel(json_data=data)
        self.assertEqual(base.json_data, data)

    def test_post_init_updates_dict(self):
        """Test __post_init__ updates instance __dict__ with json_data"""
        data = {"custom_field": "test_value", "another_field": 123}
        base = VintedJsonModel(json_data=data)
        self.assertEqual(base.custom_field, "test_value")
        self.assertEqual(base.another_field, 123)

    def test_no_repr_for_json_data(self):
        """Test json_data is not included in repr"""
        data = {"key": "value"}
        base = VintedJsonModel(json_data=data)
        repr_str = repr(base)
        self.assertNotIn("json_data", repr_str)

    def test_no_compare_for_json_data(self):
        """Test json_data is not used in comparison"""
        base1 = VintedJsonModel(json_data={"key": "value1"})
        base2 = VintedJsonModel(json_data={"key": "value2"})
        self.assertEqual(base1, base2)

    def test_getitem_access(self):
        """Test subscript access to json_data"""
        data = {"key": "value", "number": 42}
        base = VintedJsonModel(json_data=data)
        self.assertEqual(base["key"], "value")
        self.assertEqual(base["number"], 42)

    def test_getitem_raises_keyerror(self):
        """Test subscript access raises KeyError when json_data is None"""
        base = VintedJsonModel(json_data=None)
        with self.assertRaises(KeyError):
            _ = base["key"]


if __name__ == "__main__":
    unittest.main()
