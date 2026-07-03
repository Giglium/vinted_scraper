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
from src.vinted_scraper.utils._misc import _load_agents
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

    def test_load_agents_fallback_path(self):
        """Test _load_agents uses os.path fallback when sys.version_info < (3, 9)."""
        _load_agents.cache_clear()
        with patch("src.vinted_scraper.utils._misc.sys") as mock_sys:
            mock_sys.version_info = (3, 8, 0)
            _load_agents.cache_clear()
            agents = _load_agents()
            self.assertIsInstance(agents, list)
            self.assertGreater(len(agents), 0)
            for agent in agents:
                self.assertIn("ua", agent)

        # Restore cache state
        _load_agents.cache_clear()

    def test_parse_item_page_json_ld_product(self):
        """parse_item_page returns the schema.org Product from the JSON-LD block."""
        html = read_html_from_file("item_page_dummy")
        product = parse_item_page(html)
        self.assertIsInstance(product, dict)
        self.assertEqual(product["@type"], "Product")
        self.assertEqual(product["name"], "Sony Cybershot DSC-W120")
        self.assertIn("original box", product["description"])
        self.assertIn("\n", product["description"])  # multi-line preserved

    def test_parse_item_page_prefers_json_ld_over_meta(self):
        """The JSON-LD Product wins over the og:description meta tag."""
        html = (
            '<meta property="og:description" content="wrong meta">'
            '<script type="application/ld+json">'
            '{"@type":"Product","description":"right json-ld"}</script>'
        )
        self.assertEqual(parse_item_page(html)["description"], "right json-ld")

    def test_parse_item_page_json_ld_graph(self):
        """A Product nested inside an @graph list is found."""
        html = (
            '<script type="application/ld+json">'
            '{"@graph":[{"@type":"BreadcrumbList"},'
            '{"@type":"Product","description":"in graph"}]}</script>'
        )
        self.assertEqual(parse_item_page(html)["description"], "in graph")

    def test_parse_item_page_meta_fallback(self):
        """Without a JSON-LD Product, og:description is used and HTML-unescaped."""
        html = '<meta property="og:description" content="camera &amp; case">'
        self.assertEqual(parse_item_page(html), {"description": "camera & case"})

    def test_parse_item_page_ignores_malformed_json_ld(self):
        """A broken JSON-LD block is skipped, falling back to the meta tag."""
        html = (
            '<script type="application/ld+json">{not valid json}</script>'
            '<meta property="og:description" content="fallback ok">'
        )
        self.assertEqual(parse_item_page(html), {"description": "fallback ok"})

    def test_parse_item_page_returns_none_when_absent(self):
        """parse_item_page returns None when no description is present."""
        self.assertIsNone(parse_item_page("<html><body>nothing</body></html>"))


if __name__ == "__main__":
    unittest.main()
# jscpd:ignore-end
