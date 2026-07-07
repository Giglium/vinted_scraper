# jscpd:ignore-start
# pylint: disable=duplicate-code
"""Tests for misc utility functions."""

import unittest
from unittest.mock import patch

from src.vinted_scraper.utils import (
    SESSION_COOKIE_NAME,
    get_cookie_headers,
    get_curl_headers,
    get_random_user_agent,
    parse_item_page,
    url_validator,
)
from src.vinted_scraper.utils._og import _extract_og
from src.vinted_scraper.utils._user_agent import _load_agents
from tests.utils import read_html_from_file
from tests.utils._mock import BASE_URL, COOKIE_VALUE, USER_AGENT


class TestMiscUtils(unittest.TestCase):
    """Test suite for miscellaneous utility functions."""

    def test_load_agents_returns_list(self):
        """Test that _load_agents loads agents.json via importlib.resources."""
        _load_agents.cache_clear()
        agents = _load_agents()
        self.assertIsInstance(agents, list)
        self.assertGreater(len(agents), 0)

    def test_load_agents_entries_have_ua_key(self):
        """Test that each agent entry has a 'ua' key with a non-empty string."""
        agents = _load_agents()
        for agent in agents:
            self.assertIn("ua", agent)
            self.assertIsInstance(agent["ua"], str)
            self.assertGreater(len(agent["ua"]), 0)

    def test_load_agents_is_cached(self):
        """Test that _load_agents returns the same object on repeated calls (cached)."""
        _load_agents.cache_clear()
        first_call = _load_agents()
        second_call = _load_agents()
        self.assertIs(first_call, second_call)

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
            "https://fakeurl.com",
            "https://subdomain.fakeurl.com",
        ]
        for url in valid_urls:
            self.assertTrue(url_validator(url))

        # Test invalid URLs
        invalid_urls = [
            "http://fakeurl.com",  # http not allowed
            "http://www.fakeurl.com",  # http not allowed
            "http://subdomain.fakeurl.com",  # http not allowed
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

    def test_load_agents_fallback_path(self):
        """Test _load_agents uses os.path fallback when sys.version_info < (3, 9)."""
        _load_agents.cache_clear()
        with patch("src.vinted_scraper.utils._user_agent.sys") as mock_sys:
            mock_sys.version_info = (3, 8, 0)
            _load_agents.cache_clear()
            agents = _load_agents()
            self.assertIsInstance(agents, list)
            self.assertGreater(len(agents), 0)
            for agent in agents:
                self.assertIn("ua", agent)

        # Restore cache state
        _load_agents.cache_clear()

    def test_parse_item_page_extracts_all_og_fields(self):
        """parse_item_page returns title, description, url and image from og tags."""
        html = read_html_from_file("item_page_dummy")
        result = parse_item_page("123", html)
        self.assertEqual(result["id"], "123")
        self.assertEqual(result["title"], "A game")
        self.assertIn("Jumbling tower game.", result["description"])
        self.assertEqual(result["url"], "https://www.fakeurl.com/item/item_id")
        self.assertEqual(result["image"], "https://www.fakeurl.com/a.jpg")

    def test_parse_item_page_derives_title_from_description(self):
        """The title is the description segment before the first ' - ' separator."""
        html = '<meta property="og:description" content="Nice shoes - size 42">'
        self.assertEqual(parse_item_page("456", html)["title"], "Nice shoes")

    def test_parse_item_page_without_separator_has_no_title(self):
        """No ' - ' separator means no derived title key."""
        html = '<meta property="og:description" content="just a description">'
        result = parse_item_page("789", html)
        self.assertEqual(result["id"], "789")
        self.assertEqual(result["description"], "just a description")
        self.assertNotIn("title", result)

    def test_parse_item_page_unescapes_html_entities(self):
        """og:description content is HTML-unescaped."""
        html = '<meta property="og:description" content="camera &amp; case">'
        self.assertEqual(parse_item_page("101", html)["description"], "camera & case")

    def test_parse_item_page_supports_name_attribute(self):
        """A meta tag using name= instead of property= is also matched."""
        html = '<meta name="og:description" content="via name attr">'
        self.assertEqual(parse_item_page("102", html)["description"], "via name attr")

    def test_parse_item_page_returns_only_id_when_absent(self):
        """parse_item_page returns only id when no og:description is present."""
        result = parse_item_page("999", "<html><head></head><body></body></html>")
        self.assertEqual(result, {"id": "999"})

    def test_extract_og_returns_none_for_unknown_field(self):
        """_extract_og returns None when the field has no pattern in _OG_RE."""
        html = '<meta property="og:title" content="Some Title">'
        result = _extract_og(html, "title")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
# jscpd:ignore-end
