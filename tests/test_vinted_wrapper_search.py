import json
import unittest
from unittest.mock import MagicMock, Mock, patch

import requests

# isort: split
from src.vinted_scraper.VintedWrapper import VintedWrapper
from tests.utils import _read_data_from_file


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.baseurl = "https://fakeurl.com"
        self.response_200 = MagicMock(spec=requests.Response)
        self.response_200.status_code = 200
        self.response_200.headers = {"Set-Cookie": "secure, _vinted_fr_session=test"}

        with patch("requests.get", return_value=self.response_200):
            self.wrapper = VintedWrapper(self.baseurl)

    def test_search_with_params(self):
        """
        Test if the search call thr curl method with the right params
        """
        obj = {"items": []}
        self.wrapper._curl = Mock(return_value=obj)

        params = {"search_text": "games"}

        for x in [params, None]:
            self.wrapper._curl = Mock(return_value=obj)
            result = self.wrapper.search(x)
            self.wrapper._curl.assert_called_once_with("/catalog/items", params=x)
            self.assertEqual(result, obj)

    def test_raw_search_error(self):
        """
        In this use case we test if the raw search can extract data from the HTML response.
        """
        data = _read_data_from_file("search_item_dummy")
        self.response_200.content = json.dumps(data)

        with patch("requests.get", return_value=self.response_200):
            params = {"search_text": "unit_test"}
            self.assertEqual(data, self.wrapper.search(params))

    def test_status_code_error(self):
        """
        In this use case we test when we receive a response that has not a 200 status code.
        """
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.headers = {}

        with patch("requests.get", return_value=mock_response):
            self.assertRaises(RuntimeError, lambda: self.wrapper.search())

    # TODO: implement retry
    # def test_fetch_token_retry(self):
    #     try:
    #         wrapper = VintedWrapper(self.baseurl, session_cookie="invalid_cookie")
    #         wrapper.search()
    #     except Exception as e:
    #         self.fail(f"exception: {e}")
