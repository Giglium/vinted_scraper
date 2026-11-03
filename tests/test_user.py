# jscpd:ignore-start
"""Tests for get_raw_user and get_user."""

import unittest
from unittest import mock

from src.vinted_scraper import VintedScraper, VintedWrapper
from src.vinted_scraper.models import VintedUser

TEST_USER_ID = 123
# Datos sintéticos: no son de ningún usuario real.
PROFILE = {"id": TEST_USER_ID, "login": "vendedor_ejemplo", "business": False, "item_count": 4}
RESPONSE = {"code": 200, "user": PROFILE}


class GetRawUserTest(unittest.TestCase):
    def test_returns_user_object_and_calls_profile_endpoint(self):
        wrapper = VintedWrapper("https://www.vinted.lu")
        with mock.patch.object(VintedWrapper, "curl", return_value=RESPONSE) as curl:
            self.assertEqual(wrapper.get_raw_user(TEST_USER_ID), PROFILE)
        self.assertEqual(curl.call_args.args[1], f"/api/v2/users/{TEST_USER_ID}")

    def test_missing_user_key_raises(self):
        wrapper = VintedWrapper("https://www.vinted.lu")
        with mock.patch.object(VintedWrapper, "curl", return_value={"code": 200}), \
                self.assertRaisesRegex(RuntimeError, "no 'user' key"):
            wrapper.get_raw_user(TEST_USER_ID)


class GetUserTest(unittest.TestCase):
    def test_returns_typed_user(self):
        scraper = VintedScraper("https://www.vinted.lu")
        with mock.patch.object(VintedWrapper, "curl", return_value=RESPONSE):
            user = scraper.get_user(TEST_USER_ID)
        self.assertIsInstance(user, VintedUser)
        self.assertEqual(user.id, TEST_USER_ID)
        self.assertEqual(user.login, "vendedor_ejemplo")
        self.assertFalse(user.business)

    def test_propagates_errors(self):
        scraper = VintedScraper("https://www.vinted.lu")
        with mock.patch.object(VintedWrapper, "curl", side_effect=RuntimeError("error code: 404")), \
                self.assertRaisesRegex(RuntimeError, "404"):
            scraper.get_user(TEST_USER_ID)


if __name__ == "__main__":
    unittest.main()
# jscpd:ignore-end
