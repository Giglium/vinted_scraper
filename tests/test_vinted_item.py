import json
import unittest
from unittest.mock import Mock, patch

from src.vinted_scraper.models import VintedItem

# isort: split
from tests.utils import _read_data_from_file, get_200_response, get_scraper, get_wrapper


class TestItem(unittest.TestCase):
    def setUp(self):
        self.baseurl = "https://fakeurl.com"
        self.response_200 = get_200_response()
        self.wrapper = get_wrapper(self.baseurl)
        self.scraper = get_scraper(self.baseurl)

    def test_item_with_params(self):
        """
        Test if the item method call the _curl method with the right params
        """
        obj = {"item": {}}
        item_id = "id"
        self.wrapper._curl = Mock(return_value=obj)

        self.wrapper._curl = Mock(return_value=obj)
        result = self.wrapper.item(item_id)
        self.wrapper._curl.assert_called_once_with(f"/items/{item_id}", params=None)
        self.assertEqual(result, obj)

    def test_get_item(self):
        """
        Test the item method
        """
        data = _read_data_from_file("item_dummy")
        self.response_200.content = json.dumps(data)

        with patch("requests.get", return_value=self.response_200):
            self.assertEqual(data, self.wrapper.item("id"))

        with patch("requests.get", return_value=self.response_200):
            self.assertEqual(VintedItem(data["item"]), self.scraper.item("id"))

    def test_status_code_error(self):
        """
        Test the case when a status code different from 200 is returned by the web service
        """
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.headers = {}

        with patch("requests.get", return_value=mock_response):
            self.assertRaises(RuntimeError, lambda: self.wrapper.item("id"))
