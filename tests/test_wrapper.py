# jscpd:ignore-start
# pylint: disable=protected-access,duplicate-code
"""
Test the Vinted Wrapper class
"""

import logging
import unittest
from unittest.mock import patch

from src.vinted_scraper import VintedScraper, VintedWrapper
from src.vinted_scraper.models import VintedItem, VintedJsonModel
from src.vinted_scraper.utils import SESSION_COOKIE_NAME
from tests.utils import (
    BASE_URL,
    COOKIE_VALUE,
    USER_AGENT,
    create_mock,
    make_session,
    read_html_from_file,
    setup_mock_cookie_stream,
    setup_mock_get,
    setup_mock_stream,
    setup_two_clients,
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
        wrapper = VintedWrapper(BASE_URL, make_session(), USER_AGENT)
        # baseurl is normalized to its www. site form
        self.assertEqual(wrapper.baseurl, "https://www.fakeurl.com")
        self.assertEqual(wrapper.session.cookies, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        self.assertEqual(wrapper.user_agent, USER_AGENT)
        self.assertEqual(mock_client.return_value.get.call_count, 0)

        with self.assertLogs(level=logging.INFO) as cm:
            wrong_url = "wrong url"
            with self.assertRaises(RuntimeError):
                VintedWrapper(wrong_url)

            self.assertEqual(
                cm.output,
                [
                    f"ERROR:src.vinted_scraper._base_wrapper:'{wrong_url}' is not a valid url"
                ],
            )

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_search(self, mock_client):
        """Test search method"""
        setup_mock_get(mock_client, {"items": []})

        wrapper = VintedWrapper(BASE_URL, make_session())
        result = wrapper.search({"search_text": "test"})

        self.assertEqual(result, {"items": []})
        mock_client.return_value.get.assert_called_once()
        self.assertIn("search_text", str(mock_client.return_value.get.call_args))

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_search_uses_api_client_with_tokens(self, mock_client):
        """search() routes to the api. client and forwards the tokens."""
        site, api = setup_two_clients(mock_client, {"items": []})

        wrapper = VintedWrapper(
            "https://www.fakeurl.com",
            make_session(csrf_token="the-csrf", anon_id="the-anon"),
        )
        wrapper.search({"search_text": "test"})

        # the api client was used, not the site client
        api.get.assert_called_once()
        site.get.assert_not_called()
        args, kwargs = api.get.call_args
        # the endpoint stays relative; the api client base_url supplies the host
        self.assertEqual(args[0], "/svc-catalogue/items")
        headers = kwargs["headers"]
        self.assertEqual(headers["X-Csrf-Token"], "the-csrf")
        self.assertEqual(headers["X-Anon-Id"], "the-anon")
        self.assertEqual(headers["X-Next-App"], "marketplace-web")

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_search_logs_catalog_host(self, mock_client):
        """The request log shows the api. catalog host + relative endpoint."""
        _, _ = setup_two_clients(mock_client, {"items": []})

        wrapper = VintedWrapper("https://www.fakeurl.com", make_session())
        with self.assertLogs(level=logging.DEBUG) as cm:
            wrapper.search({"search_text": "test"})

        request_lines = [ln for ln in cm.output if "API Request: GET" in ln]
        self.assertTrue(request_lines)
        for line in request_lines:
            self.assertIn("/svc-catalogue/items", line)

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_item(self, mock_client):
        """item reads metadata from the public item page head."""
        setup_mock_stream(mock_client, text=read_html_from_file("item_page_dummy"))

        wrapper = VintedWrapper(BASE_URL, make_session())
        result = wrapper.item("123")

        self.assertEqual(result["title"], "A game")
        self.assertIn("Jumbling tower game.", result["description"])
        self.assertEqual(result["url"], "https://www.fakeurl.com/item/item_id")
        self.assertEqual(result["image"], "https://www.fakeurl.com/a.jpg")
        # the item endpoint is a document navigation, not the JSON API
        self.assertIn("/items/123", str(mock_client.return_value.stream.call_args))

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_item_raises_on_error(self, mock_client):
        """item raises RuntimeError when the page cannot be fetched."""
        setup_mock_stream(mock_client, status_code=403, text="")

        wrapper = VintedWrapper(BASE_URL, make_session())
        with self.assertRaises(RuntimeError):
            wrapper.item("123")

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_curl_401_retry(self, mock_client):
        """Test curl method with 401 response triggers cookie refresh.

        The API call uses ``.get`` while the cookie refresh streams the landing
        page via ``.stream``, so the two paths use different mocked methods.
        """
        mock_client.return_value.get.side_effect = [
            create_mock(status_code=401, text=""),
            create_mock({"success": True}),
        ]
        setup_mock_cookie_stream(mock_client)

        wrapper = VintedWrapper(BASE_URL, make_session())
        result = wrapper.curl("/test")

        self.assertEqual(result, {"success": True})
        self.assertEqual(mock_client.return_value.get.call_count, 2)
        mock_client.return_value.stream.assert_called_once()

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_curl_error(self, mock_client):
        """Test curl method with non-200/401 response"""
        setup_mock_get(mock_client, status_code=500, text="")

        wrapper = VintedWrapper(BASE_URL, make_session())
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

        wrapper = VintedWrapper(BASE_URL, make_session())
        with self.assertRaises(RuntimeError) as ctx:
            with self.assertLogs(level=logging.ERROR):
                wrapper.curl("/test")
        self.assertIn("JSON", str(ctx.exception))
        self.assertIsInstance(ctx.exception, RuntimeError)

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_refresh_session_no_cookie_in_response(self, mock_client):
        """A 200 without a cookie is unusable: it warns and then raises."""
        setup_mock_cookie_stream(mock_client, with_cookie=False)
        mock_client.return_value.base_url = BASE_URL

        wrapper = VintedWrapper(BASE_URL, make_session())
        with self.assertLogs(level=logging.WARNING) as cm:
            with self.assertRaises(RuntimeError):
                wrapper.refresh_session(retries=1)
        self.assertTrue(any("cookies" in line for line in cm.output))

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_refresh_session_non_200_status(self, mock_client):
        """refresh_session raises on a non-200 landing-page status."""
        setup_mock_cookie_stream(mock_client, status_code=500, with_cookie=False)
        mock_client.return_value.base_url = BASE_URL

        wrapper = VintedWrapper(BASE_URL, make_session())
        with self.assertRaises(RuntimeError) as ctx:
            with self.assertLogs(level=logging.ERROR):
                wrapper.refresh_session(retries=1)
        self.assertIn("500", str(ctx.exception))
        self.assertIsInstance(ctx.exception, RuntimeError)

    @patch("src.vinted_scraper._wrapper.time.sleep")
    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_refresh_session_retries_with_sleep(self, mock_client, mock_sleep):
        """refresh_session sleeps between retries on non-200 responses."""
        setup_mock_cookie_stream(mock_client, status_code=500, with_cookie=False)
        mock_client.return_value.base_url = BASE_URL

        wrapper = VintedWrapper(BASE_URL, make_session())
        with self.assertRaises(RuntimeError):
            with self.assertLogs(level=logging.ERROR):
                wrapper.refresh_session(retries=2)
        mock_sleep.assert_called_once()

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_fetch_session_returns_all_identifiers(self, mock_client):
        """fetch_session returns cookies and anon id (CSRF is not auto-fetched)."""
        setup_mock_cookie_stream(mock_client, headers={"X-Anon-Id": "anon-42"})
        mock_client.return_value.base_url = BASE_URL

        session = VintedWrapper.fetch_session(
            mock_client.return_value, {}, [SESSION_COOKIE_NAME]
        )
        self.assertEqual(session.cookies, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        self.assertEqual(session.anon_id, "anon-42")
        # The CSRF token is intentionally not parsed from the landing page.
        self.assertIsNone(session.csrf_token)

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_fetch_session_without_cookie_raises(self, mock_client):
        """A 200 without a cookie is unusable, so fetch_session raises."""
        setup_mock_cookie_stream(mock_client, with_cookie=False)
        mock_client.return_value.base_url = BASE_URL

        with self.assertLogs(level=logging.WARNING):
            with self.assertRaises(RuntimeError):
                VintedWrapper.fetch_session(
                    mock_client.return_value, {}, [SESSION_COOKIE_NAME], retries=1
                )

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_refresh_session_stores_tokens_and_returns_session(self, mock_client):
        """refresh_session stores the cookies + anon id and returns the session."""
        setup_mock_cookie_stream(mock_client, headers={"X-Anon-Id": "anon-42"})
        mock_client.return_value.base_url = BASE_URL

        wrapper = VintedWrapper(BASE_URL, make_session())
        session = wrapper.refresh_session()

        self.assertEqual(wrapper.session.anon_id, "anon-42")
        self.assertEqual(session.anon_id, "anon-42")
        self.assertIsNone(session.csrf_token)
        self.assertEqual(session.cookies, {SESSION_COOKIE_NAME: COOKIE_VALUE})
        self.assertEqual(wrapper.session.cookies, {SESSION_COOKIE_NAME: COOKIE_VALUE})

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_fetch_session_missing_anon_warns_and_raises(self, mock_client):
        """A 200 with a cookie but no anon id is unusable: it warns and raises."""
        setup_mock_cookie_stream(mock_client, headers={})
        mock_client.return_value.base_url = BASE_URL

        wrapper = VintedWrapper(BASE_URL, make_session())
        with self.assertLogs(level=logging.WARNING) as cm:
            with self.assertRaises(RuntimeError):
                wrapper.refresh_session(retries=1)
        self.assertTrue(any("anon_id" in line for line in cm.output))

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_context_manager(self, mock_client):
        """Test context manager __enter__ and __exit__ close both clients."""
        site, api = setup_two_clients(mock_client)
        with VintedWrapper(BASE_URL, make_session()) as wrapper:
            self.assertIsInstance(wrapper, VintedWrapper)
        site.close.assert_called_once()
        api.close.assert_called_once()


class TestVintedScraper(unittest.TestCase):
    """Test VintedScraper class"""

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_search_returns_vinted_items(self, mock_client):
        """Test search method returns VintedItem objects"""
        setup_mock_get(mock_client, {"items": [{"id": 1, "title": "Test"}]})

        scraper = VintedScraper(BASE_URL, make_session())
        result = scraper.search({"search_text": "test"})

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, 1)
        self.assertEqual(result[0].title, "Test")

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_item_returns_vinted_item(self, mock_client):
        """Test item method returns VintedItem object"""
        setup_mock_stream(mock_client, text=read_html_from_file("item_page_dummy"))

        scraper = VintedScraper(BASE_URL, make_session())
        result = scraper.item("123")

        self.assertEqual(result.title, "A game")
        self.assertIn("Jumbling tower game.", result.description)
        mock_client.return_value.stream.assert_called_once()

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_curl_returns_vinted_base(self, mock_client):
        """Test curl method returns VintedJsonModel object"""
        setup_mock_get(mock_client, {"data": "test", "value": 42})

        scraper = VintedScraper(BASE_URL, make_session())
        result = scraper.curl("/test/endpoint")

        self.assertIsInstance(result, VintedJsonModel)
        self.assertEqual(result.json_data["data"], "test")
        self.assertEqual(result.json_data["value"], 42)
        mock_client.return_value.get.assert_called_once()

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_enrich_populates_description(self, mock_client):
        """Test enrich method fetches description and populates item."""
        html = '<meta property="og:description" content="Nice shoes - size 42 leather">'
        setup_mock_stream(mock_client, text=html)

        scraper = VintedScraper(BASE_URL, make_session())
        item = VintedItem(json_data={"id": 456, "title": "Nice shoes"})
        result = scraper.enrich(item)

        self.assertIs(result, item)
        self.assertEqual(result.description, "size 42 leather")

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_enrich_no_description_found(self, mock_client):
        """Test enrich does not set description when og:description is missing."""
        html = "<html><head></head><body></body></html>"
        setup_mock_stream(mock_client, text=html)

        scraper = VintedScraper(BASE_URL, make_session())
        item = VintedItem(json_data={"id": 789, "title": "Some item"})
        result = scraper.enrich(item)

        self.assertIs(result, item)
        self.assertIsNone(result.description)


if __name__ == "__main__":
    unittest.main()
# jscpd:ignore-end
