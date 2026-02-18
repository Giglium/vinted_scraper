# jscpd:ignore-start
# pylint: disable=protected-access,duplicate-code
"""
Test the Async Vinted Wrapper class
"""

import logging
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
from src.vinted_scraper import AsyncVintedScraper, AsyncVintedWrapper
from src.vinted_scraper.models import VintedJsonModel
from src.vinted_scraper.utils import SESSION_COOKIE_NAME
from tests.utils import (
    BASE_URL,
    COOKIE_VALUE,
    USER_AGENT,
    create_cookie_response,
    create_mock,
    setup_async_mock_get,
)


class TestAsyncVintedWrapper(unittest.IsolatedAsyncioTestCase):
    """
    Test the Async Vinted Wrapper class with a Mock for the API call
    """

    def test_constructor(self):
        """
        Ensure that the constructor:
         - correctly sets the session cookie and user agent
         - raises an error if the base URL is not valid
         - logs the correct error message
        """
        wrapper = AsyncVintedWrapper(BASE_URL, {"cookie": COOKIE_VALUE}, USER_AGENT)
        self.assertEqual(wrapper.baseurl, BASE_URL)
        self.assertEqual(wrapper.session_cookie, {"cookie": COOKIE_VALUE})
        self.assertEqual(wrapper.user_agent, USER_AGENT)

        with self.assertLogs(level=logging.INFO) as cm:
            wrong_url = "wrong url"
            with self.assertRaises(RuntimeError):
                AsyncVintedWrapper(wrong_url)

            self.assertEqual(
                cm.output,
                [
                    f"ERROR:{AsyncVintedWrapper.__module__}:'{wrong_url}' is not a valid url"
                ],
            )

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_factory_create(self, mock_client):
        """
        Test the factory `create` method of `AsyncVintedWrapper`.

        This method ensures that the factory method `create`:
        - Successfully creates an instance of `AsyncVintedWrapper`.
        - Properly sets the session cookie if not provided.
        - Makes a single GET request to fetch the session cookie.
        - Correctly sets the user agent
        """
        mock_response = create_mock()
        mock_response.cookies = httpx.Cookies()
        mock_response.cookies.set(SESSION_COOKIE_NAME, COOKIE_VALUE, domain=BASE_URL)
        mock_client.return_value.get = AsyncMock(return_value=mock_response)

        wrapper = await AsyncVintedWrapper.create(BASE_URL)

        self.assertIsInstance(wrapper, AsyncVintedWrapper)
        self.assertEqual(wrapper.session_cookie, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        self.assertIsNotNone(wrapper.user_agent)
        self.assertEqual(mock_client.return_value.get.call_count, 1)

        wrapper = await AsyncVintedWrapper.create(BASE_URL, user_agent=USER_AGENT)
        self.assertEqual(wrapper.user_agent, USER_AGENT)

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_search(self, mock_client):
        """Test search method"""
        setup_async_mock_get(mock_client, {"items": []})

        wrapper = AsyncVintedWrapper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        result = await wrapper.search({"search_text": "test"})
        self.assertEqual(result, {"items": []})
        mock_client.return_value.get.assert_called_once()

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_item(self, mock_client):
        """Test item method"""
        setup_async_mock_get(mock_client, {"item": {}})

        wrapper = AsyncVintedWrapper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        result = await wrapper.item("123")
        self.assertEqual(result, {"item": {}})
        mock_client.return_value.get.assert_called_once()

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_curl_401_retry(self, mock_client):
        """Test curl method with 401 response triggers cookie refresh"""
        mock_client.return_value.get = AsyncMock(
            side_effect=[
                create_mock(status_code=401, text=""),
                create_cookie_response(),
                create_mock({"success": True}),
            ]
        )

        wrapper = AsyncVintedWrapper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        result = await wrapper.curl("/test")
        self.assertEqual(result, {"success": True})
        self.assertEqual(mock_client.return_value.get.call_count, 3)

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_curl_error(self, mock_client):
        """Test curl method with non-200/401 response"""
        setup_async_mock_get(mock_client, status_code=500, text="")

        wrapper = AsyncVintedWrapper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        with self.assertRaises(RuntimeError) as ctx:
            await wrapper.curl("/test")
        self.assertIn("500", str(ctx.exception))
        self.assertIsInstance(ctx.exception, RuntimeError)

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_curl_invalid_json(self, mock_client):
        """Test curl method with invalid JSON response"""
        setup_async_mock_get(mock_client, text="invalid")
        mock_client.return_value.get.return_value.json.side_effect = ValueError(
            "Invalid JSON"
        )

        wrapper = AsyncVintedWrapper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        with self.assertRaises(RuntimeError) as ctx:
            with self.assertLogs(level=logging.ERROR):
                await wrapper.curl("/test")
        self.assertIn("JSON", str(ctx.exception))
        self.assertIsInstance(ctx.exception, RuntimeError)

    async def test_fetch_cookie_no_cookie_in_response(self):
        """Test fetch_cookie when response doesn't contain cookie"""
        mock_client = MagicMock()
        mock_response = create_mock()
        mock_response.cookies = {}
        mock_client.get = AsyncMock(return_value=mock_response)

        with self.assertRaises(RuntimeError) as ctx:
            with self.assertLogs(level=logging.ERROR):
                await AsyncVintedWrapper.fetch_cookie(
                    mock_client, {}, [SESSION_COOKIE_NAME], retries=1
                )
        self.assertIn("cookie", str(ctx.exception).lower())
        self.assertIsInstance(ctx.exception, RuntimeError)

    async def test_fetch_cookie_non_200_status(self):
        """Test fetch_cookie with non-200 status code"""
        mock_client = MagicMock()
        mock_response = create_mock(status_code=500)
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.base_url = BASE_URL

        with self.assertRaises(RuntimeError) as ctx:
            with self.assertLogs(level=logging.ERROR):
                await AsyncVintedWrapper.fetch_cookie(
                    mock_client, {}, [SESSION_COOKIE_NAME], retries=1
                )
        self.assertIn("500", str(ctx.exception))
        self.assertIsInstance(ctx.exception, RuntimeError)


class TestAsyncVintedScraper(unittest.IsolatedAsyncioTestCase):
    """Test AsyncVintedScraper class"""

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_search_returns_vinted_items(self, mock_client):
        """Test search method returns VintedItem objects"""
        setup_async_mock_get(mock_client, {"items": [{"id": 1, "title": "Test"}]})

        scraper = AsyncVintedScraper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        result = await scraper.search({"search_text": "test"})
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, 1)
        self.assertEqual(result[0].title, "Test")

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_item_returns_vinted_item(self, mock_client):
        """Test item method returns VintedItem object"""
        setup_async_mock_get(mock_client, {"item": {"id": 123, "title": "Test Item"}})

        scraper = AsyncVintedScraper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        result = await scraper.item("123")
        self.assertEqual(result.id, 123)
        self.assertEqual(result.title, "Test Item")
        mock_client.return_value.get.assert_called_once()

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_curl_returns_vinted_base(self, mock_client):
        """Test curl method returns VintedJsonModel object"""
        setup_async_mock_get(mock_client, {"data": "test", "value": 42})

        scraper = AsyncVintedScraper(BASE_URL, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        result = await scraper.curl("/test/endpoint")
        self.assertIsInstance(result, VintedJsonModel)
        self.assertEqual(result.json_data["data"], "test")
        self.assertEqual(result.json_data["value"], 42)
        mock_client.return_value.get.assert_called_once()


if __name__ == "__main__":
    unittest.main()
# jscpd:ignore-end
