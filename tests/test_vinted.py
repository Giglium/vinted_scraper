import sys
import unittest
from unittest.mock import patch

from src.vinted_scraper.vintedScraper import VintedScraper

# isort: split
from src.vinted_scraper.vintedWrapper import VintedWrapper
from tests.utils import BASE_URL, get_200_response, get_404_response


class TestVinted(unittest.TestCase):
    def setUp(self):
        self.baseurl = BASE_URL
        self.pyversion = sys.version_info

    def test_init_valid_url(self):
        """
        Ensure that the initializer accepts a valid URL
        """

        with patch("requests.get", return_value=get_200_response()):
            wrapper = VintedWrapper(self.baseurl)
            self.assertEqual(wrapper.baseurl, self.baseurl)

        with patch("requests.get", return_value=get_200_response()):
            wrapper = VintedScraper(self.baseurl)
            self.assertEqual(wrapper.baseurl, self.baseurl)

    def test_init_invalid_url(self):
        """
        Ensure that the initializer raises an error for an invalid URL
        """
        baseurl = "invalid_url"

        with self.assertRaises(RuntimeError):
            VintedWrapper(baseurl)

        with self.assertRaises(RuntimeError):
            VintedScraper(baseurl)

    def test_init_invalid_cookie(self):
        """
        Ensure that the initializer raises an error if it can find the session cookie
        """
        response = get_200_response()
        response.headers = {}  # Reset the headers to force an invalid cookies

        with self.assertRaises(RuntimeError):
            with patch("requests.get", return_value=response):
                VintedWrapper(self.baseurl)

    def test_init_invalid_cookie_status_code(self):
        """
        Ensure that the initializer raises an error if it can find the session cookie because of a status code different
         from 200.
        """
        with self.assertRaises(RuntimeError):
            with patch("requests.get", return_value=get_404_response()):
                VintedWrapper(self.baseurl)

    def test_retry(self):
        with self.assertRaises(RuntimeError):
            with patch("requests.get", return_value=get_404_response()) as mock_get:
                VintedWrapper(self.baseurl)

        # Asserting that requests.get was called 3 times (initial call + 2 retries)
        self.assertEqual(mock_get.call_count, 3)

    def test_ssl_verify_false(self):
        # Run it only if Python 3.8+ due to missing supporto to mock_get.call_args.kwargs
        if self.pyversion.major == 3 and self.pyversion.minor >= 8:
            with patch("requests.get", return_value=get_200_response()) as mock_get:
                VintedWrapper(self.baseurl, ssl_verify=False)

            mock_get.assert_called_once()

            self.assertEqual(mock_get.call_args.kwargs.get("verify"), False)

    def test_ssl_verify_true(self):
        # Run it only if Python 3.8+ due to missing supporto to mock_get.call_args.kwargs
        if self.pyversion.major == 3 and self.pyversion.minor >= 8:
            with patch("requests.get", return_value=get_200_response()) as mock_get:
                VintedWrapper(self.baseurl)

            mock_get.assert_called_once()

            self.assertEqual(mock_get.call_args.kwargs.get("verify"), True)


if __name__ == "__main__":
    unittest.main()
