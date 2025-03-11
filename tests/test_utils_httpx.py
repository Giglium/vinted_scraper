# pylint: disable=protected-access
"""
Test the httpx utils class
"""
import unittest

import httpx
from src.vinted_scraper.utils import (
    SESSION_COOKIE_NAME,
    extract_cookie_from_response,
    get_httpx_config,
)
from tests.utils._mock import BASE_URL, COOKIE_VALUE, USER_AGENT


class TestUtils(unittest.TestCase):
    """
    Test the httpx utils class, all the API call are mocked
    """

    def test_get_httpx_config(self):
        """
        Test the get_httpx_config function to ensure it returns the correct configuration
        for an HTTPX client.

        Test cases include:
        - Default configuration: Verifies the default values are present
            if custom config is missing.
        - Merging with additional config: Checks if additional configuration parameters
            are merged correctly.
        - Overriding default values: Ensures the function allows overriding
            default values.
        """
        # Test default
        config = get_httpx_config(BASE_URL)
        self.assertEqual(config["base_url"], BASE_URL)
        self.assertEqual(config["timeout"], httpx.Timeout(10.0))
        self.assertTrue(config["follow_redirects"])
        # Test merge
        config = {"headers": {"User-Agent": USER_AGENT}}
        merged_config = get_httpx_config(BASE_URL, config)
        self.assertEqual(merged_config["base_url"], BASE_URL)
        self.assertEqual(merged_config["timeout"], httpx.Timeout(10.0))
        self.assertTrue(merged_config["follow_redirects"])
        self.assertEqual(merged_config["headers"], config["headers"])
        # Test Override
        config = {"timeout": httpx.Timeout(5.0)}
        overridden_config = get_httpx_config(BASE_URL, config)
        self.assertEqual(overridden_config["base_url"], BASE_URL)
        self.assertEqual(overridden_config["timeout"], config["timeout"])
        self.assertTrue(overridden_config["follow_redirects"])

    def test_extract_cookie_from_response(self):
        """
        Test the extract_cookie_from_response function to ensure it correctly extracts
        the specified cookie from the HTTPX response headers.

        The test cases cover:
        - Extracting a valid cookie from the Set-Cookie header.
        - Handling a response without a Set-Cookie header.
        - Handling a response where the specified cookie is missing.
        - Extracting a cookie when multiple cookies are present in the Set-Cookie header.
        """
        # set the request parameter, without that, res.raise_for_status() will fail
        request = httpx.Request("GET", BASE_URL)

        # Test cookie extraction
        response = httpx.Response(200, request=request)

        cookies = httpx.Cookies()
        cookies.set(SESSION_COOKIE_NAME, COOKIE_VALUE, domain=BASE_URL)
        response._cookies = cookies

        self.assertEqual(
            extract_cookie_from_response(response, SESSION_COOKIE_NAME), COOKIE_VALUE
        )

        # Test no Set-Cookie header
        response = httpx.Response(200, request=request, headers={})
        self.assertIsNone(extract_cookie_from_response(response, SESSION_COOKIE_NAME))

        # Test missing cookie
        response = httpx.Response(
            200, request=request, headers={"Set-Cookie": "other_cookie=other_value"}
        )
        self.assertIsNone(extract_cookie_from_response(response, SESSION_COOKIE_NAME))

        # Test multiple cookies
        response = httpx.Response(200, request=request)

        cookies = httpx.Cookies()
        cookies.set("another_cookie", "another_value", domain=BASE_URL)
        cookies.set(SESSION_COOKIE_NAME, COOKIE_VALUE, domain=BASE_URL)
        cookies.set("other_cookie", "other_value", domain=BASE_URL)
        response._cookies = cookies

        self.assertEqual(
            extract_cookie_from_response(response, SESSION_COOKIE_NAME), COOKIE_VALUE
        )


if __name__ == "__main__":
    unittest.main()
