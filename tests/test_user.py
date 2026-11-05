# jscpd:ignore-start
# pylint: disable=protected-access,duplicate-code
"""Tests for get_raw_user and get_user (sync and async)."""

import unittest
from unittest.mock import patch

from src.vinted_scraper import (
    AsyncVintedScraper,
    AsyncVintedWrapper,
    VintedScraper,
    VintedWrapper,
)
from src.vinted_scraper.models import VintedImage, VintedUser
from tests.utils import (
    BASE_URL,
    make_session,
    read_data_from_file,
    setup_async_mock_cookie_stream,
    setup_async_mock_get,
    setup_mock_get,
    setup_two_clients,
)

TEST_USER_ID = 123
# Full /api/v2/users/{id} response, wrapped in {"user": {...}} like the API.
USER_RESPONSE = read_data_from_file("user_dummy")
PROFILE = USER_RESPONSE["user"]


class TestGetRawUser(unittest.TestCase):
    """Test VintedWrapper.get_raw_user against the user_dummy fixture."""

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_returns_user_object(self, mock_client):
        """get_raw_user unwraps and returns the 'user' object."""
        setup_mock_get(mock_client, USER_RESPONSE)

        wrapper = VintedWrapper(BASE_URL, make_session())
        result = wrapper.get_raw_user(TEST_USER_ID)

        self.assertEqual(result, USER_RESPONSE)
        self.assertEqual(result["user"], PROFILE)

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_uses_site_client_and_profile_endpoint(self, mock_client):
        """get_raw_user routes to the site client and the profile endpoint."""
        site, api = setup_two_clients(mock_client, USER_RESPONSE)

        wrapper = VintedWrapper("https://www.fakeurl.com", make_session())
        wrapper.get_raw_user(TEST_USER_ID)

        site.get.assert_called_once()
        api.get.assert_not_called()
        args, _ = site.get.call_args
        self.assertEqual(args[0], f"/api/v2/users/{TEST_USER_ID}")


class TestGetUser(unittest.TestCase):
    """Test VintedScraper.get_user maps the fixture into a VintedUser."""

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_returns_typed_user(self, mock_client):
        """get_user maps the full profile into typed VintedUser fields."""
        setup_mock_get(mock_client, USER_RESPONSE)

        scraper = VintedScraper(BASE_URL, make_session())
        user = scraper.get_user(TEST_USER_ID)

        self.assertIsInstance(user, VintedUser)
        self.assertEqual(user.id, PROFILE["id"])
        self.assertEqual(user.login, PROFILE["login"])
        self.assertFalse(user.business)
        self.assertEqual(user.country_code, "LU")
        self.assertEqual(user.country_title, "Luxembourg")
        self.assertEqual(user.city, "Luxembourg")
        self.assertEqual(user.item_count, 17)
        self.assertEqual(user.total_items_count, 41)
        self.assertEqual(user.given_item_count, 24)
        self.assertEqual(user.taken_item_count, 5)
        self.assertEqual(user.feedback_count, 4)
        self.assertAlmostEqual(user.feedback_reputation, 1.0, places=2)
        self.assertEqual(user.followers_count, 1)
        self.assertEqual(user.currency, "EUR")
        self.assertEqual(user.locale, "en-us-fr")
        self.assertTrue(user.can_bundle)
        self.assertEqual(user.bundle_discount["minimal_item_count"], 2)
        self.assertTrue(user.verification["email"]["valid"])
        self.assertIsInstance(user.photo, VintedImage)
        self.assertEqual(user.photo.url, "https://www.fakeurl.com/a.jpg")

    @patch("src.vinted_scraper._wrapper.httpx.Client")
    def test_propagates_errors(self, mock_client):
        """A non-200 response surfaces as a RuntimeError from curl."""
        setup_mock_get(mock_client, status_code=404, text="")

        scraper = VintedScraper(BASE_URL, make_session())
        with self.assertRaisesRegex(RuntimeError, "404"):
            scraper.get_user(TEST_USER_ID)


class TestAsyncGetRawUser(unittest.IsolatedAsyncioTestCase):
    """Async counterpart: AsyncVintedWrapper.get_raw_user."""

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_returns_user_object(self, mock_client):
        """get_raw_user unwraps and returns the 'user' object."""
        setup_async_mock_cookie_stream(mock_client)
        setup_async_mock_get(mock_client, USER_RESPONSE)

        wrapper = await AsyncVintedWrapper.create(BASE_URL, session=make_session())
        result = await wrapper.get_raw_user(TEST_USER_ID)

        self.assertEqual(result, USER_RESPONSE)
        self.assertEqual(result["user"], PROFILE)


class TestAsyncGetUser(unittest.IsolatedAsyncioTestCase):
    """Async counterpart: AsyncVintedScraper.get_user."""

    @patch("src.vinted_scraper._async_wrapper.httpx.AsyncClient")
    async def test_returns_typed_user(self, mock_client):
        """get_user maps the full profile into a typed VintedUser."""
        setup_async_mock_cookie_stream(mock_client)
        setup_async_mock_get(mock_client, USER_RESPONSE)

        scraper = await AsyncVintedScraper.create(BASE_URL, session=make_session())
        user = await scraper.get_user(TEST_USER_ID)

        self.assertIsInstance(user, VintedUser)
        self.assertEqual(user.id, PROFILE["id"])
        self.assertEqual(user.login, PROFILE["login"])
        self.assertEqual(user.item_count, 17)
        self.assertEqual(user.currency, "EUR")
        self.assertIsInstance(user.photo, VintedImage)


if __name__ == "__main__":
    unittest.main()
# jscpd:ignore-end
