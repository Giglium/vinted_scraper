import unittest
from unittest.mock import MagicMock, patch

import requests

# isort: split
from src.vinted_scraper.VintedWrapper import VintedWrapper


class TestVintedWrapper(unittest.TestCase):
    def test_init_valid_url(self):
        """
        Ensure that the initializer accepts a valid URL
        """
        baseurl = "https://fakeurl.com"
        response = MagicMock(spec=requests.Response)
        response.headers = {"Set-Cookie": "secure, _vinted_fr_session=test"}

        with patch("requests.get", return_value=response):
            wrapper = VintedWrapper(baseurl)
            self.assertEqual(wrapper.baseurl, baseurl)

    def test_init_invalid_url(self):
        """
        Ensure that the initializer raises an error for an invalid URL
        """
        with self.assertRaises(RuntimeError):
            VintedWrapper("invalid_url")

    def test_init_valid_url2(self):
        """
        Ensure that the initializer accepts a valid URL
        """
        response = MagicMock(spec=requests.Response)
        response.headers = {}

        with self.assertRaises(RuntimeError):
            with patch("requests.get", return_value=response):
                VintedWrapper("https://fakeurl.com")


if __name__ == "__main__":
    unittest.main()
