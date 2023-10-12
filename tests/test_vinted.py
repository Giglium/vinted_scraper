import unittest
from unittest.mock import patch

from src.vinted_scraper.vintedScraper import VintedScraper

# isort: split
from src.vinted_scraper.vintedWrapper import VintedWrapper
from tests.utils import get_200_response


class TestVinted(unittest.TestCase):
    def test_init_valid_url(self):
        """
        Ensure that the initializer accepts a valid URL
        """
        baseurl = "https://fakeurl.com"

        with patch("requests.get", return_value=get_200_response()):
            wrapper = VintedWrapper(baseurl)
            self.assertEqual(wrapper.baseurl, baseurl)

        with patch("requests.get", return_value=get_200_response()):
            wrapper = VintedScraper(baseurl)
            self.assertEqual(wrapper.baseurl, baseurl)

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
        baseurl = "https://fakeurl.com"
        response = get_200_response()
        response.headers = {}

        with self.assertRaises(RuntimeError):
            with patch("requests.get", return_value=response):
                VintedWrapper(baseurl)


if __name__ == "__main__":
    unittest.main()
