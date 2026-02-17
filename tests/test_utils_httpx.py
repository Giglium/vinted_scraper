# jscpd:ignore-start
# pylint: disable=protected-access,duplicate-code
"""Tests for httpx utility functions."""

import logging
import unittest

import httpx
from src.vinted_scraper.utils import (
    SESSION_COOKIE_NAME,
    extract_cookie_from_response,
    get_httpx_config,
)
from src.vinted_scraper.utils._httpx import log_response
from tests.utils._mock import BASE_URL, COOKIE_VALUE, USER_AGENT


class TestHttpxUtils(unittest.TestCase):
    """Test suite for httpx utility functions."""

    def test_get_httpx_config(self):
        """Test get_httpx_config returns correct default and merged configurations."""
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
        """Test extract_cookie_from_response correctly extracts cookies from httpx response."""
        # set the request parameter, without that, res.raise_for_status() will fail
        request = httpx.Request("GET", BASE_URL)

        # Test cookie extraction
        response = httpx.Response(200, request=request)

        cookies = httpx.Cookies()
        cookies.set(SESSION_COOKIE_NAME, COOKIE_VALUE, domain=BASE_URL)
        response._cookies = cookies

        result = extract_cookie_from_response(response, [SESSION_COOKIE_NAME])
        self.assertEqual(result[SESSION_COOKIE_NAME], COOKIE_VALUE)

        # Test no cookies
        response = httpx.Response(200, request=request, headers={})
        result = extract_cookie_from_response(response, [SESSION_COOKIE_NAME])
        self.assertEqual(result, {})

        # Test missing cookie
        response = httpx.Response(
            200, request=request, headers={"Set-Cookie": "other_cookie=other_value"}
        )
        result = extract_cookie_from_response(response, [SESSION_COOKIE_NAME])
        self.assertEqual(result, {})

        # Test multiple cookies
        response = httpx.Response(200, request=request)

        cookies = httpx.Cookies()
        cookies.set("another_cookie", "another_value", domain=BASE_URL)
        cookies.set(SESSION_COOKIE_NAME, COOKIE_VALUE, domain=BASE_URL)
        cookies.set("other_cookie", "other_value", domain=BASE_URL)
        response._cookies = cookies

        result = extract_cookie_from_response(
            response, [SESSION_COOKIE_NAME, "another_cookie"]
        )
        self.assertEqual(result[SESSION_COOKIE_NAME], COOKIE_VALUE)
        self.assertEqual(result["another_cookie"], "another_value")

    def test_log_response(self):
        """Test log_response logs response details at DEBUG level."""
        logger = logging.getLogger("test_logger")
        original_level = logger.level
        logger.setLevel(logging.DEBUG)

        try:
            request = httpx.Request("GET", BASE_URL)
            response = httpx.Response(
                200,
                request=request,
                headers={"Content-Type": "application/json"},
            )
            response._content = b'{"test": "data"}'

            with self.assertLogs(logger, level=logging.DEBUG) as cm:
                log_response(logger, response)
                self.assertTrue(any("Status code: 200" in log for log in cm.output))
        finally:
            logger.setLevel(original_level)


if __name__ == "__main__":
    unittest.main()
# jscpd:ignore-end
