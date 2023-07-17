import unittest
from unittest.mock import MagicMock, Mock, patch

import requests

# isort: split
from src.vinted_scraper import VintedItem, get_item, get_raw_item
from tests.utils import get_dummy_item_data, get_empty_data


class MyTestCase(unittest.TestCase):
    def test_get_raw_item(self):
        """
        In this use case we test if the raw search can extract data from the HTML response.
        """
        data, html = get_dummy_item_data()
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.content = html
        with patch("requests.get", return_value=mock_response):
            self.assertEqual(data, get_raw_item("https://www.fakeurl.com"))

    def test_get_item(self):
        """
        In this use case we test if the search can extract data from the HTML response.
        """
        data, html = get_dummy_item_data()
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.content = html
        with patch("requests.get", return_value=mock_response):
            self.assertEqual(VintedItem(data), get_item("https://www.fakeurl.com"))

    def test_missing_tag_error(self):
        """
        In this use case we test when we can't find the right script HTML tag, in the HTML response.
        """
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.content = get_empty_data()

        with patch("requests.get", return_value=mock_response):
            self.assertRaises(
                RuntimeError, lambda: get_raw_item("https://www.fakeurl.com")
            )

    def test_status_code_error(self):
        """
        In this use case we test when we receive a response that has not a 200 status code.
        """
        mock_response = Mock()
        mock_response.status_code = 404

        with patch("requests.get", return_value=mock_response):
            self.assertRaises(
                RuntimeError, lambda: get_raw_item("https://www.fakeurl.com")
            )


if __name__ == "__main__":
    unittest.main()
