import unittest
from unittest.mock import MagicMock, Mock, patch

import requests

# isort: split
from src.vinted_scraper import VintedItem, raw_search, search
from tests.utils import get_dummy_search_data, get_empty_data


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.response_200 = MagicMock(spec=requests.Response)
        self.response_200.status_code = 200
        self.response_200.headers = {}

    def test_raw_search_error(self):
        """
        In this use case we test if the raw search can extract data from the HTML response.
        """
        data, html = get_dummy_search_data()
        self.response_200.content = html

        with patch("requests.get", return_value=self.response_200):
            params = {"search_text": "unit_test"}
            self.assertEqual([data], raw_search("https://www.fakeurl.com", params))

    def test_search_error(self):
        """
        In this use case we test if the search can extract data from the HTML response.
        """
        data, html = get_dummy_search_data()
        self.response_200.content = html

        with patch("requests.get", return_value=self.response_200):
            params = {"search_text": "unit_test"}
            self.assertEqual(
                [VintedItem(data)], search("https://www.fakeurl.com", params)
            )

    def test_missing_tag_error(self):
        """
        In this use case we test when we can't find the right script HTML tag, in the HTML response.
        """
        self.response_200.content = get_empty_data()

        with patch("requests.get", return_value=self.response_200):
            params = {"search_text": "unit_test"}
            self.assertRaises(
                RuntimeError, lambda: raw_search("https://www.fakeurl.com", params)
            )

    def test_status_code_error(self):
        """
        In this use case we test when we receive a response that has not a 200 status code.
        """
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.headers = {}

        with patch("requests.get", return_value=mock_response):
            params = {"search_text": "unit_test"}
            self.assertRaises(
                RuntimeError, lambda: raw_search("https://www.fakeurl.com", params)
            )


if __name__ == "__main__":
    unittest.main()
