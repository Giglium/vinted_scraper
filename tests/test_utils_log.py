# pylint: disable=line-too-long
"""
Test the log utils class
"""

import logging
import sys
import unittest

from src.vinted_scraper.utils import (
    log_constructor,
    log_cookie_fetch_failed,
    log_cookie_fetched,
    log_cookie_retry,
    log_curl,
    log_curl_request,
    log_curl_response,
    log_interaction,
    log_item,
    log_refresh_cookie,
    log_search,
    log_sleep,
)
from tests.utils import BASE_URL, COOKIE_VALUE, USER_AGENT, assert_no_logs


class TestUtils(unittest.TestCase):
    """
    Test the log utils class print a correct log in DEBUG mode and no log on INFO
    """

    def setUp(self):
        self.pyversion = sys.version_info

    def test_log_constructor(self):
        """
        Test the log_constructor function.

        Test cases include:
        - Checking that the message is logged when the DEBUG level is enabled
        - Checking that the message is not logged when the DEBUG level is disabled
        """
        log = logging.getLogger(__name__)
        # Case DEBUG enabled
        config = {"headers": {"User-Agent": USER_AGENT}}
        with self.assertLogs(level=logging.DEBUG) as cm:
            log_constructor(
                log=log,
                self=self,
                baseurl=BASE_URL,
                user_agent=USER_AGENT,
                session_cookie=COOKIE_VALUE,
                config=config,
            )
            self.assertEqual(len(cm.output), 1)
            self.assertIn(f"Initializing {self.__class__.__name__}", cm.output[0])
            self.assertIn(BASE_URL, cm.output[0])
            self.assertIn("provided", cm.output[0])

        # Case with auto-fetch cookie
        with self.assertLogs(level=logging.DEBUG) as cm:
            log_constructor(
                log=log,
                self=self,
                baseurl=BASE_URL,
                user_agent=USER_AGENT,
                session_cookie=None,
                config=config,
            )
            self.assertIn("auto-fetch", cm.output[0])

        # Case Debug disable
        assert_no_logs(
            log_constructor,
            self,
            log=log,
            level=logging.INFO,
            self=self,
            baseurl=BASE_URL,
            user_agent=USER_AGENT,
            session_cookie=COOKIE_VALUE,
            config=config,
        )

    def test_log_interaction(self):
        """
        Test the log_interaction function.

        Test cases include:
        - Checking that the message is logged when the DEBUG level is enabled
        - Checking that the message is not logged when the DEBUG level is disabled
        """
        log = logging.getLogger(__name__)

        for i in range(0, 3):
            # Case DEBUG enabled
            with self.assertLogs(level=logging.DEBUG) as cm:
                log_interaction(log=log, i=i, retries=3)
                self.assertIn(f"Cookie fetch attempt {i+1}/3", cm.output[0])

            # Case Debug disable
            assert_no_logs(
                log_interaction, self, log=log, level=logging.INFO, i=i, retries=3
            )

    def test_log_sleep(self):
        """
        Test the log_sleep function.

        Test cases include:
        - Checking that the message is logged when the DEBUG level is enabled
        - Checking that the message is not logged when the DEBUG level is disabled
        """
        log = logging.getLogger(__name__)
        # Case DEBUG enabled
        time = 1000
        with self.assertLogs(level=logging.DEBUG) as cm:
            log_sleep(log=log, time=time)
            self.assertEqual(
                cm.output,
                [f"DEBUG:{__name__}:Sleeping for {time} seconds"],
            )

        # Case Debug disable
        assert_no_logs(log_sleep, self, log=log, level=logging.INFO, time=time)

    def test_log_refresh_cookie(self):
        """
        Test the log_refresh_cookie function.

        Test cases include:
        - Checking that the message is logged when the DEBUG level is enabled
        - Checking that the message is not logged when the DEBUG level is disabled
        """
        log = logging.getLogger(__name__)
        # Case DEBUG enabled
        with self.assertLogs(level=logging.DEBUG) as cm:
            log_refresh_cookie(log=log)
            self.assertIn("Refreshing session cookie", cm.output[0])

        # Case Debug disable
        assert_no_logs(
            log_refresh_cookie,
            self,
            log=log,
            level=logging.INFO,
        )

    def test_log_search(self):
        """
        Test the log_search function.

        Test cases include:
        - Checking that the message is logged when the DEBUG level is enabled
        - Checking that the message is not logged when the DEBUG level is disabled
        """
        log = logging.getLogger(__name__)
        params = {"search_text": "board games"}
        # Case DEBUG enabled
        with self.assertLogs(level=logging.DEBUG) as cm:
            log_search(log=log, params=params)
            self.assertIn("Calling search()", cm.output[0])
            self.assertIn(str(params), cm.output[0])

        # Case Debug disable
        assert_no_logs(log_search, self, log=log, level=logging.INFO, params=params)

        # Case with None params
        with self.assertLogs(level=logging.DEBUG) as cm:
            log_search(log=log, params=None)
            self.assertIn("Calling search()", cm.output[0])
            self.assertIn("None", cm.output[0])

    def test_log_item(self):
        """
        Test the log_item function.

        Test cases include:
        - Checking that the message is logged when the DEBUG level is enabled
        - Checking that the message is not logged when the DEBUG level is disabled
        """
        log = logging.getLogger(__name__)
        item_id = "123456"
        params = {"locale": "en"}
        # Case DEBUG enabled
        with self.assertLogs(level=logging.DEBUG) as cm:
            log_item(log=log, item_id=item_id, params=params)
            self.assertIn("Calling item", cm.output[0])
            self.assertIn(item_id, cm.output[0])
            self.assertIn(str(params), cm.output[0])

        # Case Debug disable
        assert_no_logs(
            log_item, self, log=log, level=logging.INFO, item_id=item_id, params=params
        )

        # Case with None params
        with self.assertLogs(level=logging.DEBUG) as cm:
            log_item(log=log, item_id=item_id, params=None)
            self.assertIn("Calling item", cm.output[0])
            self.assertIn(item_id, cm.output[0])

    def test_log_curl(self):
        """
        Test the log_curl function.

        Test cases include:
        - Checking that the message is logged when the DEBUG level is enabled
        - Checking that the message is not logged when the DEBUG level is disabled
        """
        log = logging.getLogger(__name__)
        endpoint = "/catalog/items"
        params = {"page": 1}
        # Case DEBUG enabled
        with self.assertLogs(level=logging.DEBUG) as cm:
            log_curl(log=log, endpoint=endpoint, params=params)
            self.assertIn("Calling endpoint", cm.output[0])
            self.assertIn(endpoint, cm.output[0])

        # Case Debug disable
        assert_no_logs(
            log_curl,
            self,
            log=log,
            level=logging.INFO,
            endpoint=endpoint,
            params=params,
        )

        # Case with None params
        with self.assertLogs(level=logging.DEBUG) as cm:
            log_curl(log=log, endpoint=endpoint, params=None)
            self.assertIn("Calling endpoint", cm.output[0])
            self.assertIn(endpoint, cm.output[0])

    def test_log_curl_request(self):
        """
        Test the log_curl_request function.

        Test cases include:
        - Checking that the message is logged with curl command when DEBUG is enabled
        - Checking that the message is not logged when DEBUG is disabled
        """
        log = logging.getLogger(__name__)
        base_url = BASE_URL
        endpoint = "/catalog/items"
        headers = {
            "User-Agent": USER_AGENT,
            "Cookie": f"_vinted_fr_session={COOKIE_VALUE}",
        }
        params = {"search_text": "board games"}

        # Case DEBUG enabled with params
        with self.assertLogs(level=logging.DEBUG) as cm:
            log_curl_request(
                log=log,
                base_url=base_url,
                endpoint=endpoint,
                headers=headers,
                params=params,
            )
            self.assertEqual(len(cm.output), 2)
            self.assertIn("API Request: GET /catalog/items with params", cm.output[0])
            self.assertIn("Curl command:", cm.output[1])
            self.assertIn("curl", cm.output[1])
            self.assertIn(USER_AGENT, cm.output[1])

        # Case DEBUG enabled without params
        with self.assertLogs(level=logging.DEBUG) as cm:
            log_curl_request(
                log=log,
                base_url=base_url,
                endpoint=endpoint,
                headers=headers,
                params=None,
            )
            self.assertEqual(len(cm.output), 2)
            self.assertIn(
                "API Request: GET /catalog/items with params None", cm.output[0]
            )

        # Case Debug disable (early return)
        assert_no_logs(
            log_curl_request,
            self,
            log=log,
            level=logging.INFO,
            base_url=base_url,
            endpoint=endpoint,
            headers=headers,
            params=params,
        )

    def test_log_curl_response(self):
        """
        Test the log_curl_response function.

        Test cases include:
        - Checking that the response details are logged when DEBUG is enabled
        - Checking that long bodies are truncated
        """
        log = logging.getLogger(__name__)
        endpoint = "/catalog/items"
        status_code = 200
        headers = {"Content-Type": "application/json"}
        body = '{"items": []}'

        # Case DEBUG enabled with body
        with self.assertLogs(level=logging.DEBUG) as cm:
            log_curl_response(
                log=log,
                endpoint=endpoint,
                status_code=status_code,
                headers=headers,
                body=body,
            )
            self.assertEqual(len(cm.output), 3)
            self.assertIn("API Response: /catalog/items - Status: 200", cm.output[0])
            self.assertIn("Response Headers:", cm.output[1])
            self.assertIn("Response Body:", cm.output[2])

        # Case DEBUG enabled without body
        with self.assertLogs(level=logging.DEBUG) as cm:
            log_curl_response(
                log=log,
                endpoint=endpoint,
                status_code=status_code,
                headers=headers,
                body=None,
            )
            self.assertEqual(len(cm.output), 2)
            self.assertIn("API Response:", cm.output[0])
            self.assertIn("Response Headers:", cm.output[1])

        # Case with long body (should be truncated)
        long_body = "x" * 2000
        with self.assertLogs(level=logging.DEBUG) as cm:
            log_curl_response(
                log=log,
                endpoint=endpoint,
                status_code=status_code,
                headers=headers,
                body=long_body,
            )
            self.assertIn("truncated", cm.output[2])

        # Case Debug disable (early return)
        assert_no_logs(
            log_curl_response,
            self,
            log=log,
            level=logging.INFO,
            endpoint=endpoint,
            status_code=status_code,
            headers=headers,
            body=body,
        )

    def test_log_cookie_fetched(self):
        """
        Test the log_cookie_fetched function.
        """
        log = logging.getLogger(__name__)
        cookie_value = "abc123def456ghi789"

        with self.assertLogs(level=logging.DEBUG) as cm:
            log_cookie_fetched(log=log, cookie_value=cookie_value)
            self.assertIn("Session cookie fetched successfully", cm.output[0])
            self.assertIn("abc123def456ghi789"[:20], cm.output[0])

        assert_no_logs(
            log_cookie_fetched,
            self,
            log=log,
            level=logging.INFO,
            cookie_value=cookie_value,
        )

    def test_log_cookie_retry(self):
        """
        Test the log_cookie_retry function.
        """
        log = logging.getLogger(__name__)
        status_code = 401

        with self.assertLogs(level=logging.DEBUG) as cm:
            log_cookie_retry(log=log, status_code=status_code)
            self.assertIn("Received 401 status", cm.output[0])
            self.assertIn("refreshing session cookie", cm.output[0])

        assert_no_logs(
            log_cookie_retry,
            self,
            log=log,
            level=logging.INFO,
            status_code=status_code,
        )

    def test_log_cookie_fetch_failed(self):
        """
        Test the log_cookie_fetch_failed function.
        """
        log = logging.getLogger(__name__)
        status_code = 403
        attempt = 0
        retries = 3

        with self.assertLogs(level=logging.DEBUG) as cm:
            log_cookie_fetch_failed(
                log=log, status_code=status_code, attempt=attempt, retries=retries
            )
            self.assertIn("Cookie fetch failed", cm.output[0])
            self.assertIn("attempt 1/3", cm.output[0])
            self.assertIn("403", cm.output[0])

        # Test with None status_code
        with self.assertLogs(level=logging.DEBUG) as cm:
            log_cookie_fetch_failed(
                log=log, status_code=None, attempt=attempt, retries=retries
            )
            self.assertIn("unknown", cm.output[0])

        assert_no_logs(
            log_cookie_fetch_failed,
            self,
            log=log,
            level=logging.INFO,
            status_code=status_code,
            attempt=attempt,
            retries=retries,
        )


if __name__ == "__main__":
    unittest.main()
