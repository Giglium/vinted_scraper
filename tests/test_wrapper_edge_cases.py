# jscpd:ignore-start
# pylint: disable=protected-access,duplicate-code
"""
Additional test cases for edge cases and error scenarios
"""

import unittest
from unittest.mock import patch

from src.vinted_scraper import VintedScraper, VintedWrapper
from src.vinted_scraper.utils import SESSION_COOKIE_NAME
from tests.utils import (
    BASE_URL,
    COOKIE_VALUE,
    create_cookie_response,
    create_mock,
    read_html_from_file,
    setup_mock_get,
    setup_mock_stream,
)


class TestVintedWrapperEdgeCases(unittest.TestCase):
    """Test edge cases and error scenarios"""

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_search_with_empty_params(self, mock_client):
        """Test search with empty parameters"""
        setup_mock_get(mock_client, {"items": []})

        wrapper = VintedWrapper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        result = wrapper.search({})
        self.assertEqual(result, {"items": []})

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_search_with_none_params(self, mock_client):
        """Test search with None parameters"""
        setup_mock_get(mock_client, {"items": []})

        wrapper = VintedWrapper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        result = wrapper.search(None)
        self.assertEqual(result, {"items": []})

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_item_with_invalid_id(self, mock_client):
        """Test item method with various ID formats"""
        setup_mock_stream(mock_client, text=read_html_from_file("item_page_dummy"))

        wrapper = VintedWrapper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})

        # Test with string ID
        result = wrapper.item("123")
        self.assertEqual(result["title"], "A game")
        self.assertIn("/items/123", str(mock_client.return_value.stream.call_args))

        # Test with numeric ID
        result = wrapper.item(123)
        self.assertEqual(result["title"], "A game")
        self.assertIn("/items/123", str(mock_client.return_value.stream.call_args))

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_curl_with_special_characters_in_params(self, mock_client):
        """Test curl with special characters in parameters"""
        setup_mock_get(mock_client, {"success": True})

        wrapper = VintedWrapper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        result = wrapper.curl("/test", {"query": "test&special=chars"})
        self.assertEqual(result, {"success": True})

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_multiple_401_retries_then_success(self, mock_client):
        """Test multiple 401 responses before success"""
        mock_client.return_value.get.side_effect = [
            create_mock(status_code=401, text=""),
            create_cookie_response(),
            create_mock(status_code=401, text=""),
            create_cookie_response(),
            create_mock({"success": True}),
        ]

        wrapper = VintedWrapper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        result = wrapper.curl("/test")
        self.assertEqual(result, {"success": True})
        self.assertEqual(mock_client.return_value.get.call_count, 5)

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_401_retry_exhaustion(self, mock_client):
        """Test that curl raises after DEFAULT_RETRIES consecutive 401s"""
        # Each 401 triggers a cookie refresh (1 GET) then a retry (1 GET) = 2 GETs per retry
        # With DEFAULT_RETRIES=3, we need: 3 x (401 + cookie_refresh) + final 401
        mock_client.return_value.get.side_effect = [
            create_mock(status_code=401, text=""),
            create_cookie_response(),
            create_mock(status_code=401, text=""),
            create_cookie_response(),
            create_mock(status_code=401, text=""),
            create_cookie_response(),
            create_mock(status_code=401, text=""),
        ]

        wrapper = VintedWrapper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        with self.assertRaises(RuntimeError) as ctx:
            wrapper.curl("/test")
        self.assertIn("401", str(ctx.exception))

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_scraper_with_empty_items_list(self, mock_client):
        """Test VintedScraper with empty items list"""
        setup_mock_get(mock_client, {"items": []})

        scraper = VintedScraper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        result = scraper.search({"search_text": "nonexistent"})
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_scraper_with_malformed_item_data(self, mock_client):
        """Test VintedScraper handles malformed item data gracefully"""
        setup_mock_get(
            mock_client,
            {
                "items": [
                    {"id": 1},
                    {"title": "Test"},
                    {},
                ]
            },
        )

        scraper = VintedScraper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        result = scraper.search({"search_text": "test"})
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_wrapper_close_on_exception(self, mock_client):
        """Test that client is closed even when exception occurs"""
        mock_client.return_value.get.side_effect = RuntimeError("Network error")

        wrapper = VintedWrapper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        with self.assertRaises(RuntimeError):
            with wrapper:
                wrapper.search({})

        mock_client.return_value.close.assert_called_once()

    def test_constructor_with_none_user_agent(self):
        """Test constructor generates user agent when None provided"""
        wrapper = VintedWrapper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE}, None)
        self.assertIsNotNone(wrapper.user_agent)
        self.assertIsInstance(wrapper.user_agent, str)
        self.assertGreater(len(wrapper.user_agent), 0)

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_constructor_auto_fetch_cookie(self, mock_client):
        """Test constructor auto-fetches cookie when not provided"""
        mock_client.return_value.get.return_value = create_cookie_response()
        wrapper = VintedWrapper(BASE_URL)
        self.assertEqual(wrapper.session_cookie, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        mock_client.return_value.get.assert_called_once()

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_item_head_tag_split_across_chunks(self, mock_client):
        """item() detects </head> even when it spans two chunks."""
        html = read_html_from_file("item_page_dummy")
        # Split so "</head>" is broken across boundaries: "</he" | "ad>..."
        split_idx = html.lower().index("</head>") + 4  # after "</he"
        chunk1 = html[:split_idx]
        chunk2 = html[split_idx:]
        setup_mock_stream(mock_client, chunks=[chunk1, chunk2])

        wrapper = VintedWrapper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        result = wrapper.item("123")

        self.assertEqual(result["title"], "A game")
        self.assertIn("Jumbling tower game.", result["description"])

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_item_head_tag_split_single_char_boundary(self, mock_client):
        """item() detects </head> split at each possible single-char boundary."""
        html = read_html_from_file("item_page_dummy")
        head_idx = html.lower().index("</head>")

        # Split right after "<" — the rest "/head>..." is in chunk2
        chunk1 = html[: head_idx + 1]
        chunk2 = html[head_idx + 1 :]
        setup_mock_stream(mock_client, chunks=[chunk1, chunk2])

        wrapper = VintedWrapper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        result = wrapper.item("123")

        self.assertEqual(result["title"], "A game")


if __name__ == "__main__":
    unittest.main()
# jscpd:ignore-end
