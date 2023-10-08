import json
import unittest
from unittest.mock import Mock, patch

# isort: split
from tests.utils import _read_data_from_file, get_200_response, get_wrapper


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.baseurl = "https://fakeurl.com"
        self.response_200 = get_200_response()
        self.wrapper = get_wrapper(self.baseurl)

    def test_search_with_params(self):
        """
        Test if the search call thr curl method with the right params
        """
        obj = {"item": {}}
        item_id = "id"
        self.wrapper._curl = Mock(return_value=obj)

        self.wrapper._curl = Mock(return_value=obj)
        result = self.wrapper.item(item_id)
        self.wrapper._curl.assert_called_once_with(f"/items/{item_id}", params=None)
        self.assertEqual(result, obj)

    def test_raw_search_error(self):
        """
        In this use case we test if the raw search can extract data from the HTML response.
        """
        data = _read_data_from_file("item_dummy")
        self.response_200.content = json.dumps(data)

        with patch("requests.get", return_value=self.response_200):
            self.assertEqual(data, self.wrapper.item("id"))

    def test_status_code_error(self):
        """
        In this use case we test when we receive a response that has not a 200 status code.
        """
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.headers = {}

        with patch("requests.get", return_value=mock_response):
            self.assertRaises(RuntimeError, lambda: self.wrapper.item("id"))
