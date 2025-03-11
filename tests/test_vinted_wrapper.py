# jscpd:ignore-start
# pylint: disable=protected-access
"""
Test the Vinted Wrapper class
"""
import logging
import unittest
from unittest.mock import patch

from src.vinted_scraper import VintedWrapper
from tests.utils._mock import BASE_URL, COOKIE_VALUE, USER_AGENT


class TestVintedWrapper(unittest.TestCase):
    """
    Test the Vinted Wrapper class with a Mock for the API call
    """

    @patch("src.vinted_scraper._vinted_wrapper.httpx.Client")
    def test_constructor(self, mock_client):
        """
        Ensure that the constructor:
         - correctly sets the session cookie and user agent
         - raises an error if the base URL is not valid
         - logs the correct error message
        """
        wrapper = VintedWrapper(BASE_URL, COOKIE_VALUE, USER_AGENT)
        self.assertEqual(wrapper._base_url, BASE_URL)
        self.assertEqual(wrapper._session_cookie, COOKIE_VALUE)
        self.assertEqual(wrapper._user_agent, USER_AGENT)
        self.assertEqual(mock_client.return_value.get.call_count, 0)

        with self.assertLogs(level=logging.INFO) as cm:
            wrong_url = "wrong url"
            with self.assertRaises(RuntimeError):
                VintedWrapper(wrong_url)

            self.assertEqual(
                cm.output,
                [f"ERROR:{VintedWrapper.__module__}:'{wrong_url}' is not a valid url"],
            )


if __name__ == "__main__":
    unittest.main()
# jscpd:ignore-end
