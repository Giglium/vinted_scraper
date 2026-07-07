# jscpd:ignore-start
# pylint: disable=duplicate-code
"""Tests for httpx utility functions."""

import unittest

import httpx
from src.vinted_scraper.utils import (
    SESSION_COOKIE_NAME,
    extract_cookie_from_response,
    get_httpx_config,
)
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
        request = httpx.Request("GET", BASE_URL)

        # Test cookie extraction via Set-Cookie header
        response = httpx.Response(
            200,
            request=request,
            headers=[("Set-Cookie", f"{SESSION_COOKIE_NAME}={COOKIE_VALUE}")],
        )
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
        response = httpx.Response(
            200,
            request=request,
            headers=[
                ("Set-Cookie", "another_cookie=another_value"),
                ("Set-Cookie", f"{SESSION_COOKIE_NAME}={COOKIE_VALUE}"),
                ("Set-Cookie", "other_cookie=other_value"),
            ],
        )
        result = extract_cookie_from_response(
            response, [SESSION_COOKIE_NAME, "another_cookie"]
        )
        self.assertEqual(result[SESSION_COOKIE_NAME], COOKIE_VALUE)
        self.assertEqual(result["another_cookie"], "another_value")


if __name__ == "__main__":
    unittest.main()
# jscpd:ignore-end
