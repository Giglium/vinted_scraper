# jscpd:ignore-start
# pylint: disable=protected-access,duplicate-code
"""
Test the Vinted Wrapper class
"""

import logging
import unittest
from unittest.mock import patch

from src.vinted_scraper import VintedScraper, VintedWrapper
from src.vinted_scraper.models import VintedJsonModel
from src.vinted_scraper.utils import SESSION_COOKIE_NAME
from tests.utils import (
    BASE_URL,
    COOKIE_VALUE,
    USER_AGENT,
    create_cookie_response,
    create_mock,
    setup_mock_get,
)


class TestVintedWrapper(unittest.TestCase):
    """
    Test the Vinted Wrapper class with a Mock for the API call
    """

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_constructor(self, mock_client):
        """
        Ensure that the constructor:
         - correctly sets the session cookie and user agent
         - raises an error if the base URL is not valid
         - logs the correct error message
        """
        wrapper = VintedWrapper(
            BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE}, USER_AGENT
        )
        self.assertEqual(wrapper.baseurl, BASE_URL)
        self.assertEqual(wrapper.session_cookie, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        self.assertEqual(wrapper.user_agent, USER_AGENT)
        self.assertEqual(mock_client.return_value.get.call_count, 0)

        with self.assertLogs(level=logging.INFO) as cm:
            wrong_url = "wrong url"
            with self.assertRaises(RuntimeError):
                VintedWrapper(wrong_url)

            self.assertEqual(
                cm.output,
                [f"ERROR:{VintedWrapper.__module__}:'{wrong_url}' is not a valid url"],
            )

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_search(self, mock_client):
        """Test search method"""
        setup_mock_get(mock_client, {"items": []})

        wrapper = VintedWrapper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        result = wrapper.search({"search_text": "test"})

        self.assertEqual(result, {"items": []})
        mock_client.return_value.get.assert_called_once()
        self.assertIn("search_text", str(mock_client.return_value.get.call_args))

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_item(self, mock_client):
        """Test item method"""
        setup_mock_get(mock_client, {"item": {}})

        wrapper = VintedWrapper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        result = wrapper.item("123")

        self.assertEqual(result, {"item": {}})
        mock_client.return_value.get.assert_called_once()

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_curl_401_retry(self, mock_client):
        """Test curl method with 401 response triggers cookie refresh"""
        mock_client.return_value.get.side_effect = [
            create_mock(status_code=401, text=""),
            create_cookie_response(),
            create_mock({"success": True}),
        ]

        wrapper = VintedWrapper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        result = wrapper.curl("/test")

        self.assertEqual(result, {"success": True})
        self.assertEqual(mock_client.return_value.get.call_count, 3)

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_curl_error(self, mock_client):
        """Test curl method with non-200/401 response"""
        setup_mock_get(mock_client, status_code=500, text="")

        wrapper = VintedWrapper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        with self.assertRaises(RuntimeError) as ctx:
            wrapper.curl("/test")
        self.assertIn("500", str(ctx.exception))
        self.assertIsInstance(ctx.exception, RuntimeError)

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_curl_invalid_json(self, mock_client):
        """Test curl method with invalid JSON response"""
        setup_mock_get(mock_client, text="invalid")
        mock_client.return_value.get.return_value.json.side_effect = ValueError(
            "Invalid JSON"
        )

        wrapper = VintedWrapper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        with self.assertRaises(RuntimeError) as ctx:
            with self.assertLogs(level=logging.ERROR):
                wrapper.curl("/test")
        self.assertIn("JSON", str(ctx.exception))
        self.assertIsInstance(ctx.exception, RuntimeError)

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_fetch_cookie_no_cookie_in_response(self, mock_client):
        """Test fetch_cookie when response doesn't contain cookie"""
        setup_mock_get(mock_client)
        mock_client.return_value.get.return_value.cookies = {}
        mock_client.return_value.base_url = BASE_URL

        with self.assertRaises(RuntimeError) as ctx:
            with self.assertLogs(level=logging.ERROR):
                VintedWrapper.fetch_cookie(
                    mock_client.return_value, {}, [SESSION_COOKIE_NAME], retries=1
                )
        self.assertIn("cookie", str(ctx.exception).lower())
        self.assertIsInstance(ctx.exception, RuntimeError)

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_fetch_cookie_non_200_status(self, mock_client):
        """Test fetch_cookie with non-200 status code"""
        setup_mock_get(mock_client, status_code=500)
        mock_client.return_value.base_url = BASE_URL

        with self.assertRaises(RuntimeError) as ctx:
            with self.assertLogs(level=logging.ERROR):
                VintedWrapper.fetch_cookie(
                    mock_client.return_value, {}, [SESSION_COOKIE_NAME], retries=1
                )
        self.assertIn("500", str(ctx.exception))
        self.assertIsInstance(ctx.exception, RuntimeError)

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_context_manager(self, mock_client):
        """Test context manager __enter__ and __exit__"""
        with VintedWrapper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE}) as wrapper:
            self.assertIsInstance(wrapper, VintedWrapper)
        mock_client.return_value.close.assert_called_once()


class TestVintedScraper(unittest.TestCase):
    """Test VintedScraper class"""

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_search_returns_vinted_items(self, mock_client):
        """Test search method returns VintedItem objects"""
        setup_mock_get(mock_client, {"items": [{"id": 1, "title": "Test"}]})

        scraper = VintedScraper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        result = scraper.search({"search_text": "test"})

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, 1)
        self.assertEqual(result[0].title, "Test")

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_item_returns_vinted_item(self, mock_client):
        """Test item method returns VintedItem object"""
        setup_mock_get(mock_client, {"item": {"id": 123, "title": "Test Item"}})

        scraper = VintedScraper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        result = scraper.item("123")

        self.assertEqual(result.id, 123)
        self.assertEqual(result.title, "Test Item")
        mock_client.return_value.get.assert_called_once()

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_curl_returns_vinted_base(self, mock_client):
        """Test curl method returns VintedJsonModel object"""
        setup_mock_get(mock_client, {"data": "test", "value": 42})

        scraper = VintedScraper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        result = scraper.curl("/test/endpoint")

        self.assertIsInstance(result, VintedJsonModel)
        self.assertEqual(result.json_data["data"], "test")
        self.assertEqual(result.json_data["value"], 42)
        mock_client.return_value.get.assert_called_once()


if __name__ == "__main__":
    unittest.main()
# jscpd:ignore-end
