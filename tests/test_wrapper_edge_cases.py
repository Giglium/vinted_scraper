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
    setup_mock_get,
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
        setup_mock_get(mock_client, {"item": {"id": 123}})

        wrapper = VintedWrapper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})

        # Test with string ID
        result = wrapper.item("123")
        self.assertEqual(result, {"item": {"id": 123}})

        # Test with numeric ID
        result = wrapper.item(123)
        self.assertEqual(result, {"item": {"id": 123}})

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


if __name__ == "__main__":
    unittest.main()
# jscpd:ignore-end
