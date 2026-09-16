# jscpd:ignore-start
# pylint: disable=duplicate-code,too-many-public-methods
"""Tests for misc utility functions."""

import unittest
from unittest.mock import patch

from src.vinted_scraper.models._og_field import OgField
from src.vinted_scraper.utils import (
    SESSION_COOKIE_NAME,
    api_base_url,
    get_cookie_headers,
    get_curl_headers,
    get_random_user_agent,
    parse_item_page,
    site_base_url,
    url_validator,
)
from src.vinted_scraper.utils._html import (
    ChunkAccumulator,
    _extract_og,
    extract_csrf_token,
)
from src.vinted_scraper.utils._user_agent import _load_agents
from tests.utils import read_html_from_file
from tests.utils._mock import BASE_URL, COOKIE_VALUE, USER_AGENT, make_session


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
        """Test get_curl_headers returns the catalog-compatible header set."""
        headers = get_curl_headers(BASE_URL, USER_AGENT, make_session())
        self.assertIsInstance(headers, dict)
        self.assertEqual(headers["User-Agent"], USER_AGENT)
        self.assertEqual(headers["Origin"], BASE_URL)
        self.assertEqual(headers["Referer"], BASE_URL)
        self.assertEqual(headers["Cookie"], f"{SESSION_COOKIE_NAME}={COOKIE_VALUE}")
        # marketplace-web headers required by the catalog service
        self.assertEqual(headers["X-Next-App"], "marketplace-web")
        self.assertEqual(headers["Sec-Fetch-Site"], "same-site")
        self.assertEqual(headers["Platform"], "web")
        # headers dropped from the previous lean set must not reappear
        self.assertNotIn("Accept-Encoding", headers)
        self.assertNotIn("Connection", headers)
        # tokens are omitted when not provided
        self.assertNotIn("X-Csrf-Token", headers)
        self.assertNotIn("X-Anon-Id", headers)

    def test_get_curl_headers_without_session(self):
        """A None session yields the base headers with no Cookie/token."""
        headers = get_curl_headers(BASE_URL, USER_AGENT, None)
        self.assertNotIn("Cookie", headers)
        self.assertNotIn("X-Csrf-Token", headers)
        self.assertNotIn("X-Anon-Id", headers)

    def test_get_curl_headers_includes_tokens_when_provided(self):
        """CSRF token and anonymous id are added when available."""
        headers = get_curl_headers(
            BASE_URL,
            USER_AGENT,
            make_session(csrf_token="the-csrf", anon_id="the-anon"),
        )
        self.assertEqual(headers["X-Csrf-Token"], "the-csrf")
        self.assertEqual(headers["X-Anon-Id"], "the-anon")

    def test_get_curl_headers_csrf_without_anon_id(self):
        """A CSRF token is sent while a missing anon id is left out."""
        headers = get_curl_headers(
            BASE_URL,
            USER_AGENT,
            make_session(csrf_token="the-csrf"),
        )
        self.assertEqual(headers["X-Csrf-Token"], "the-csrf")
        self.assertNotIn("X-Anon-Id", headers)

    def test_get_curl_headers_tokens_without_cookies(self):
        """Tokens are still emitted when a session carries no cookies."""
        headers = get_curl_headers(
            BASE_URL,
            USER_AGENT,
            make_session(cookie=False, csrf_token="the-csrf", anon_id="the-anon"),
        )
        self.assertNotIn("Cookie", headers)
        self.assertEqual(headers["X-Csrf-Token"], "the-csrf")
        self.assertEqual(headers["X-Anon-Id"], "the-anon")

    def test_extract_csrf_token(self):
        """extract_csrf_token pulls the UUID next to the CSRF_TOKEN marker."""
        uuid = "11111111-2222-3333-4444-555555555555"
        html = f'window.__data = {{"CSRF_TOKEN":"{uuid}"}};'
        self.assertEqual(extract_csrf_token(html), uuid)

    def test_extract_csrf_token_absent(self):
        """extract_csrf_token returns None when the marker is missing."""
        self.assertIsNone(extract_csrf_token("<html><head></head></html>"))

    def test_api_base_url_rewrites_www_to_api(self):
        """A www. host is rewritten to its api. sibling."""
        self.assertEqual(
            api_base_url("https://www.vinted.com"), "https://api.vinted.com"
        )

    def test_api_base_url_adds_api_to_bare_host(self):
        """A host without www. gets the api. prefix."""
        self.assertEqual(api_base_url("https://vinted.fr"), "https://api.vinted.fr")

    def test_api_base_url_only_strips_leading_www(self):
        """Only the leading www. is replaced, not an embedded one."""
        self.assertEqual(
            api_base_url("https://www.wwwshop.com"), "https://api.wwwshop.com"
        )

    def test_api_base_url_without_scheme(self):
        """A schemeless value is handled without producing a stray separator."""
        self.assertEqual(api_base_url("www.vinted.com"), "api.vinted.com")

    def test_site_base_url_adds_www_to_bare_host(self):
        """site_base_url ensures the www. prefix on a bare host."""
        self.assertEqual(site_base_url("https://vinted.fr"), "https://www.vinted.fr")

    def test_site_base_url_keeps_existing_www(self):
        """site_base_url leaves an already-www. host unchanged."""
        self.assertEqual(
            site_base_url("https://www.vinted.com"), "https://www.vinted.com"
        )

    def test_site_base_url_without_scheme(self):
        """A schemeless value is handled without producing a stray separator."""
        self.assertEqual(site_base_url("vinted.com"), "www.vinted.com")

    def test_chunk_accumulator_stops_on_marker(self):
        """add() returns True once the stop marker appears and keeps the text."""
        acc = ChunkAccumulator("</head>")
        self.assertFalse(acc.add("<html><head><title>x</title>"))
        self.assertTrue(acc.add("</head><body>"))
        self.assertEqual(acc.text, "<html><head><title>x</title></head><body>")

    def test_chunk_accumulator_marker_across_boundary(self):
        """The marker is detected even when split across two chunks."""
        acc = ChunkAccumulator("</head>")
        self.assertFalse(acc.add("...</he"))
        self.assertTrue(acc.add("ad>..."))

    def test_chunk_accumulator_is_case_insensitive(self):
        """Marker matching ignores case."""
        acc = ChunkAccumulator("</head>")
        self.assertTrue(acc.add("<HEAD></HEAD>"))

    def test_chunk_accumulator_handles_chunks_shorter_than_marker(self):
        """A marker split into single-character chunks is still detected."""
        acc = ChunkAccumulator("CSRF_TOKEN")
        result = [acc.add(char) for char in "xxCSRF_TOKEN"]
        self.assertTrue(result[-1])
        self.assertFalse(any(result[:-1]))

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

    def test_parse_item_page_separator_but_title_and_description_not_requested(self):
        """A ' - ' description is skipped when neither title nor description is asked."""
        html = '<meta property="og:description" content="Nice shoes - size 42">'
        result = parse_item_page("456", html, fields=[OgField.URL, OgField.IMAGE])
        self.assertEqual(result, {"id": "456"})

    def test_parse_item_page_no_separator_and_description_not_requested(self):
        """A separator-free description is dropped when description is not requested."""
        html = '<meta property="og:description" content="just a description">'
        result = parse_item_page("789", html, fields=[OgField.URL, OgField.IMAGE])
        self.assertEqual(result, {"id": "789"})

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
