# pylint: disable=broad-exception-caught
"""
Test the misc utils class
"""
import unittest

from src.vinted_scraper.utils import (
    SESSION_COOKIE_NAME,
    get_cookie_headers,
    get_curl_headers,
    get_random_user_agent,
    url_validator,
)
from tests.utils._mock import BASE_URL, COOKIE_VALUE, USER_AGENT


class TestUtils(unittest.TestCase):
    """
    Test the misc utils class
    """

    def test_get_random_user_agent(self):
        """
        Test the get_random_user_agent function.

        Test cases include:
        - Ensure that the function doesn't raise any exceptions
        """
        try:
            get_random_user_agent()
        except Exception as e:
            self.fail(f"get_random_user_agent() raised an exception: {e}")

    def test_url_validators(self):
        """
        Test the test_url_validators function.

        Test cases include:
        -  Test that valid URLs are correctly identified by the url_validator function.
        - Test that invalid URLs are correctly identified by the url_validator function.
        """

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
        """
        Test the get_cookie_headers function.

        The test case includes:
        - Verify that the function returns a dictionary.
        - Verify that the function sets the User-Agent header to the provided user agent.
        - Verify that the function sets the Origin and Referer headers to the provided base URL.
        """
        headers = get_cookie_headers(BASE_URL, USER_AGENT)
        self.assertIsInstance(headers, dict)
        self.assertEqual(headers["User-Agent"], USER_AGENT)
        self.assertEqual(headers["Origin"], BASE_URL)
        self.assertEqual(headers["Referer"], BASE_URL)

    def test_get_curl_headers(self):
        """
        Test the get_curl_headers function.

        The test case includes:
        - Verify that the function returns a dictionary.
        - Verify that the function sets the User-Agent header to the provided user agent.
        - Verify that the function sets the Origin and Referer headers to the provided base URL.
        """
        headers = get_curl_headers(BASE_URL, USER_AGENT, COOKIE_VALUE)
        self.assertIsInstance(headers, dict)
        self.assertEqual(headers["User-Agent"], USER_AGENT)
        self.assertEqual(headers["Origin"], BASE_URL)
        self.assertEqual(headers["Referer"], BASE_URL)
        self.assertEqual(headers["Cookie"], f"{SESSION_COOKIE_NAME}={COOKIE_VALUE}")


if __name__ == "__main__":
    unittest.main()
