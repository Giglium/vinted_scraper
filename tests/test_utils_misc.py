# jscpd:ignore-start
# pylint: disable=duplicate-code
"""Tests for misc utility functions."""

import unittest

from src.vinted_scraper.utils import (
    SESSION_COOKIE_NAME,
    get_cookie_headers,
    get_curl_headers,
    get_random_user_agent,
    url_validator,
)
from tests.utils._mock import BASE_URL, COOKIE_VALUE, USER_AGENT


class TestMiscUtils(unittest.TestCase):
    """Test suite for miscellaneous utility functions."""

    def test_get_random_user_agent(self):
        """Test that get_random_user_agent returns a valid non-empty string."""
        user_agent = get_random_user_agent()
        self.assertIsInstance(user_agent, str)
        self.assertGreater(len(user_agent), 0)

    def test_url_validators(self):
        """Test url_validator correctly identifies valid and invalid URLs."""

        # Test valid URLs
        valid_urls = [
            BASE_URL,
            "https://www.fakeurl.com",
            "http://fakeurl.com",
            "https://fakeurl.com",
            "http://www.fakeurl.com",
            "https://subdomain.fakeurl.com",
            "http://subdomain.fakeurl.com",
        ]
        for url in valid_urls:
            self.assertTrue(url_validator(url))

        # Test invalid URLs
        invalid_urls = [
            "ftp://fakeurl.com",  # wrong scheme
            "https://fakeurl",  # wrong host
            "https://.com",  # wrong host
            "https://fakeurl.com:8080/path",  # path
            "https://fakeurl.com/path?query=string",  # query params
            "https://fakeurl.com.",  # trailing dot
            "http://fakeurl.com..",  # double trailing dot
            "https://fakeurl.com:80",  # port number
            "http://fakeurl.com:443",  # port number
        ]

        for url in invalid_urls:
            self.assertFalse(url_validator(url))

    def test_get_cookie_headers(self):
        """Test get_cookie_headers returns correct headers with User-Agent, Origin, and Referer."""
        headers = get_cookie_headers(BASE_URL, USER_AGENT)
        self.assertIsInstance(headers, dict)
        self.assertEqual(headers["User-Agent"], USER_AGENT)
        self.assertEqual(headers["Origin"], BASE_URL)
        self.assertEqual(headers["Referer"], BASE_URL)

    def test_get_curl_headers(self):
        """Test get_curl_headers returns correct headers including Cookie."""
        headers = get_curl_headers(
            BASE_URL, USER_AGENT, {SESSION_COOKIE_NAME: COOKIE_VALUE}
        )
        self.assertIsInstance(headers, dict)
        self.assertEqual(headers["User-Agent"], USER_AGENT)
        self.assertEqual(headers["Origin"], BASE_URL)
        self.assertEqual(headers["Referer"], BASE_URL)
        self.assertEqual(headers["Cookie"], f"{SESSION_COOKIE_NAME}={COOKIE_VALUE}")


if __name__ == "__main__":
    unittest.main()
# jscpd:ignore-end
