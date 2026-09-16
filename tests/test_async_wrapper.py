# jscpd:ignore-start
# pylint: disable=protected-access,duplicate-code
"""
Test the Async Vinted Wrapper class
"""

import logging
import unittest
from unittest.mock import AsyncMock, patch

from src.vinted_scraper import AsyncVintedScraper, AsyncVintedWrapper
from src.vinted_scraper.models import VintedItem, VintedJsonModel
from src.vinted_scraper.utils import SESSION_COOKIE_NAME
from tests.utils import (
    BASE_URL,
    COOKIE_VALUE,
    USER_AGENT,
    create_mock,
    make_session,
    read_html_from_file,
    setup_async_mock_cookie_stream,
    setup_async_mock_get,
    setup_async_mock_stream,
    setup_two_clients,
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
        session = make_session()
        wrapper = AsyncVintedWrapper(BASE_URL, session, USER_AGENT)
        # baseurl is normalized to its www. site form
        self.assertEqual(wrapper.baseurl, "https://www.fakeurl.com")
        self.assertEqual(wrapper.session, session)
        self.assertEqual(wrapper.user_agent, USER_AGENT)

        with self.assertLogs(level=logging.INFO) as cm:
            wrong_url = "wrong url"
            with self.assertRaises(RuntimeError):
                AsyncVintedWrapper(wrong_url)

            self.assertEqual(
                cm.output,
                [
                    f"ERROR:src.vinted_scraper._base_wrapper:'{wrong_url}' is not a valid url"
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
        setup_async_mock_cookie_stream(mock_client)

        wrapper = await AsyncVintedWrapper.create(BASE_URL)

        self.assertIsInstance(wrapper, AsyncVintedWrapper)
        self.assertEqual(wrapper.session.cookies, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        self.assertIsNotNone(wrapper.user_agent)
        self.assertEqual(mock_client.return_value.stream.call_count, 1)

        wrapper = await AsyncVintedWrapper.create(BASE_URL, user_agent=USER_AGENT)
        self.assertEqual(wrapper.user_agent, USER_AGENT)

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_factory_create_with_session_skips_fetch(self, mock_client):
        """create() with a provided session does not fetch a new one."""
        setup_async_mock_cookie_stream(mock_client)
        session = make_session(csrf_token="x", anon_id="y")

        wrapper = await AsyncVintedWrapper.create(BASE_URL, session=session)

        self.assertIs(wrapper.session, session)
        mock_client.return_value.stream.assert_not_called()

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_search(self, mock_client):
        """Test search method"""
        setup_async_mock_get(mock_client, {"items": []})

        wrapper = AsyncVintedWrapper(BASE_URL, make_session())
        result = await wrapper.search({"search_text": "test"})
        self.assertEqual(result, {"items": []})
        mock_client.return_value.get.assert_called_once()

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_search_uses_api_client_with_tokens(self, mock_client):
        """search() routes to the api. client and forwards the tokens."""
        site, api = setup_two_clients(mock_client, {"items": []}, is_async=True)

        wrapper = AsyncVintedWrapper(
            "https://www.fakeurl.com",
            make_session(csrf_token="the-csrf", anon_id="the-anon"),
        )
        await wrapper.search({"search_text": "test"})

        api.get.assert_awaited_once()
        site.get.assert_not_awaited()
        args, kwargs = api.get.call_args
        self.assertEqual(args[0], "/svc-catalogue/items")
        self.assertEqual(kwargs["headers"]["X-Csrf-Token"], "the-csrf")
        self.assertEqual(kwargs["headers"]["X-Anon-Id"], "the-anon")

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_item(self, mock_client):
        """item reads metadata from the public item page head."""
        setup_async_mock_stream(
            mock_client, text=read_html_from_file("item_page_dummy")
        )

        wrapper = AsyncVintedWrapper(BASE_URL, make_session())
        result = await wrapper.item("123")

        self.assertEqual(result["title"], "A game")
        self.assertIn("Jumbling tower game.", result["description"])
        self.assertEqual(result["url"], "https://www.fakeurl.com/item/item_id")
        self.assertEqual(result["image"], "https://www.fakeurl.com/a.jpg")
        self.assertIn("/items/123", str(mock_client.return_value.stream.call_args))

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_item_raises_on_error(self, mock_client):
        """item raises RuntimeError when the page cannot be fetched."""
        setup_async_mock_stream(mock_client, status_code=403, text="")

        wrapper = AsyncVintedWrapper(BASE_URL, make_session())
        with self.assertRaises(RuntimeError):
            await wrapper.item("123")

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_curl_401_retry(self, mock_client):
        """Test curl method with 401 response triggers cookie refresh"""
        mock_client.return_value.get = AsyncMock(
            side_effect=[
                create_mock(status_code=401, text=""),
                create_mock({"success": True}),
            ]
        )
        setup_async_mock_cookie_stream(mock_client)

        wrapper = AsyncVintedWrapper(BASE_URL, make_session())
        result = await wrapper.curl("/test")
        self.assertEqual(result, {"success": True})
        self.assertEqual(mock_client.return_value.get.call_count, 2)
        self.assertEqual(mock_client.return_value.stream.call_count, 1)

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_curl_error(self, mock_client):
        """Test curl method with non-200/401 response"""
        setup_async_mock_get(mock_client, status_code=500, text="")

        wrapper = AsyncVintedWrapper(BASE_URL, make_session())
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

        wrapper = AsyncVintedWrapper(BASE_URL, make_session())
        with self.assertRaises(RuntimeError) as ctx:
            with self.assertLogs(level=logging.ERROR):
                await wrapper.curl("/test")
        self.assertIn("JSON", str(ctx.exception))
        self.assertIsInstance(ctx.exception, RuntimeError)

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_refresh_session_no_cookie_in_response(self, mock_client):
        """A 200 without a cookie is unusable: it warns and then raises."""
        setup_async_mock_cookie_stream(mock_client, with_cookie=False)
        mock_client.return_value.base_url = BASE_URL

        wrapper = AsyncVintedWrapper(BASE_URL, make_session())
        with self.assertLogs(level=logging.WARNING) as cm:
            with self.assertRaises(RuntimeError):
                await wrapper.refresh_session(retries=1)
        self.assertTrue(any("cookies" in line for line in cm.output))

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_refresh_session_non_200_status(self, mock_client):
        """refresh_session raises on a non-200 landing-page status."""
        setup_async_mock_cookie_stream(mock_client, status_code=500, with_cookie=False)
        mock_client.return_value.base_url = BASE_URL

        wrapper = AsyncVintedWrapper(BASE_URL, make_session())
        with self.assertRaises(RuntimeError) as ctx:
            with self.assertLogs(level=logging.ERROR):
                await wrapper.refresh_session(retries=1)
        self.assertIn("500", str(ctx.exception))
        self.assertIsInstance(ctx.exception, RuntimeError)

    @patch("src.vinted_scraper._async_wrapper.asyncio.sleep", new_callable=AsyncMock)
    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_refresh_session_retries_with_sleep(self, mock_client, mock_sleep):
        """refresh_session sleeps between retries on non-200 responses."""
        setup_async_mock_cookie_stream(mock_client, status_code=500, with_cookie=False)
        mock_client.return_value.base_url = BASE_URL

        wrapper = AsyncVintedWrapper(BASE_URL, make_session())
        with self.assertRaises(RuntimeError):
            with self.assertLogs(level=logging.ERROR):
                await wrapper.refresh_session(retries=2)
        mock_sleep.assert_called_once()

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_fetch_session_returns_all_identifiers(self, mock_client):
        """fetch_session returns cookies and anon id (CSRF is not auto-fetched)."""
        setup_async_mock_cookie_stream(mock_client, headers={"X-Anon-Id": "anon-42"})
        mock_client.return_value.base_url = BASE_URL

        session = await AsyncVintedWrapper.fetch_session(
            mock_client.return_value, {}, [SESSION_COOKIE_NAME]
        )
        self.assertEqual(session.cookies, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        self.assertEqual(session.anon_id, "anon-42")
        # The CSRF token is intentionally not parsed from the landing page.
        self.assertIsNone(session.csrf_token)

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_fetch_session_without_cookie_raises(self, mock_client):
        """A 200 without a cookie is unusable, so fetch_session raises."""
        setup_async_mock_cookie_stream(mock_client, with_cookie=False)
        mock_client.return_value.base_url = BASE_URL

        with self.assertLogs(level=logging.WARNING):
            with self.assertRaises(RuntimeError):
                await AsyncVintedWrapper.fetch_session(
                    mock_client.return_value, {}, [SESSION_COOKIE_NAME], retries=1
                )

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_refresh_session_stores_tokens_and_returns_session(self, mock_client):
        """refresh_session stores the cookies + anon id and returns the session."""
        setup_async_mock_cookie_stream(mock_client, headers={"X-Anon-Id": "anon-42"})
        mock_client.return_value.base_url = BASE_URL

        wrapper = AsyncVintedWrapper(BASE_URL, make_session())
        session = await wrapper.refresh_session()

        self.assertEqual(wrapper.session.anon_id, "anon-42")
        self.assertEqual(session.anon_id, "anon-42")
        self.assertIsNone(session.csrf_token)
        self.assertEqual(session.cookies, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        self.assertEqual(wrapper.session.cookies, {SESSION_COOKIE_NAME: COOKIE_VALUE})


class TestAsyncVintedScraper(unittest.IsolatedAsyncioTestCase):
    """Test AsyncVintedScraper class"""

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_search_returns_vinted_items(self, mock_client):
        """Test search method returns VintedItem objects"""
        setup_async_mock_get(mock_client, {"items": [{"id": 1, "title": "Test"}]})

        scraper = AsyncVintedScraper(BASE_URL, make_session())
        result = await scraper.search({"search_text": "test"})
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, 1)
        self.assertEqual(result[0].title, "Test")

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_item_returns_vinted_item(self, mock_client):
        """Test item method returns VintedItem object"""
        setup_async_mock_stream(
            mock_client, text=read_html_from_file("item_page_dummy")
        )

        scraper = AsyncVintedScraper(BASE_URL, make_session())
        result = await scraper.item("123")
        self.assertEqual(result.title, "A game")
        self.assertIn("Jumbling tower game.", result.description)
        mock_client.return_value.stream.assert_called_once()

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_curl_returns_vinted_base(self, mock_client):
        """Test curl method returns VintedJsonModel object"""
        setup_async_mock_get(mock_client, {"data": "test", "value": 42})

        scraper = AsyncVintedScraper(BASE_URL, make_session())
        result = await scraper.curl("/test/endpoint")
        self.assertIsInstance(result, VintedJsonModel)
        self.assertEqual(result.json_data["data"], "test")
        self.assertEqual(result.json_data["value"], 42)
        mock_client.return_value.get.assert_called_once()

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_enrich_populates_description(self, mock_client):
        """Test enrich method fetches description and populates item."""
        html = '<meta property="og:description" content="Nice shoes - size 42 leather">'
        setup_async_mock_stream(mock_client, text=html)

        scraper = AsyncVintedScraper(BASE_URL, make_session())
        item = VintedItem(json_data={"id": 456, "title": "Nice shoes"})
        result = await scraper.enrich(item)

        self.assertIs(result, item)
        self.assertEqual(result.description, "size 42 leather")

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_enrich_no_description_found(self, mock_client):
        """Test enrich does not set description when og:description is missing."""
        html = "<html><head></head><body></body></html>"
        setup_async_mock_stream(mock_client, text=html)

        scraper = AsyncVintedScraper(BASE_URL, make_session())
        item = VintedItem(json_data={"id": 789, "title": "Some item"})
        result = await scraper.enrich(item)

        self.assertIs(result, item)
        self.assertIsNone(result.description)


class TestAsyncVintedWrapperEdgeCases(unittest.IsolatedAsyncioTestCase):
    """Test async edge cases and error scenarios"""

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_search_with_empty_params(self, mock_client):
        """Test search with empty parameters"""
        setup_async_mock_get(mock_client, {"items": []})

        wrapper = AsyncVintedWrapper(BASE_URL, make_session())
        result = await wrapper.search({})
        self.assertEqual(result, {"items": []})

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_search_with_none_params(self, mock_client):
        """Test search with None parameters"""
        setup_async_mock_get(mock_client, {"items": []})

        wrapper = AsyncVintedWrapper(BASE_URL, make_session())
        result = await wrapper.search(None)
        self.assertEqual(result, {"items": []})

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_multiple_401_retries_then_success(self, mock_client):
        """Test multiple 401 responses before success"""
        mock_client.return_value.get = AsyncMock(
            side_effect=[
                create_mock(status_code=401, text=""),
                create_mock(status_code=401, text=""),
                create_mock({"success": True}),
            ]
        )
        setup_async_mock_cookie_stream(mock_client)

        wrapper = AsyncVintedWrapper(BASE_URL, make_session())
        result = await wrapper.curl("/test")
        self.assertEqual(result, {"success": True})
        self.assertEqual(mock_client.return_value.get.call_count, 3)
        self.assertEqual(mock_client.return_value.stream.call_count, 2)

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_401_retry_exhaustion(self, mock_client):
        """Test that curl raises after DEFAULT_RETRIES consecutive 401s"""
        mock_client.return_value.get = AsyncMock(
            return_value=create_mock(status_code=401, text="")
        )
        setup_async_mock_cookie_stream(mock_client)

        wrapper = AsyncVintedWrapper(BASE_URL, make_session())
        with self.assertRaises(RuntimeError) as ctx:
            await wrapper.curl("/test")
        self.assertIn("401", str(ctx.exception))

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_scraper_with_empty_items_list(self, mock_client):
        """Test AsyncVintedScraper with empty items list"""
        setup_async_mock_get(mock_client, {"items": []})

        scraper = AsyncVintedScraper(BASE_URL, make_session())
        result = await scraper.search({"search_text": "nonexistent"})
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_scraper_with_malformed_item_data(self, mock_client):
        """Test AsyncVintedScraper handles malformed item data gracefully"""
        setup_async_mock_get(
            mock_client,
            {
                "items": [
                    {"id": 1},
                    {"title": "Test"},
                    {},
                ]
            },
        )

        scraper = AsyncVintedScraper(BASE_URL, make_session())
        result = await scraper.search({"search_text": "test"})
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_item_head_tag_split_across_chunks(self, mock_client):
        """item() detects </head> even when it spans two async chunks."""
        html = read_html_from_file("item_page_dummy")
        # Split so "</head>" is broken across boundaries: "</he" | "ad>..."
        split_idx = html.lower().index("</head>") + 4  # after "</he"
        chunk1 = html[:split_idx]
        chunk2 = html[split_idx:]
        setup_async_mock_stream(mock_client, chunks=[chunk1, chunk2])

        wrapper = AsyncVintedWrapper(BASE_URL, make_session())
        result = await wrapper.item("123")

        self.assertEqual(result["title"], "A game")
        self.assertIn("Jumbling tower game.", result["description"])

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_item_head_tag_split_single_char_boundary(self, mock_client):
        """item() detects </head> split at each possible single-char boundary."""
        html = read_html_from_file("item_page_dummy")
        head_idx = html.lower().index("</head>")

        # Split right after "<" — the rest "/head>..." is in chunk2
        chunk1 = html[: head_idx + 1]
        chunk2 = html[head_idx + 1 :]
        setup_async_mock_stream(mock_client, chunks=[chunk1, chunk2])

        wrapper = AsyncVintedWrapper(BASE_URL, make_session())
        result = await wrapper.item("123")

        self.assertEqual(result["title"], "A game")


if __name__ == "__main__":
    unittest.main()
# jscpd:ignore-end
