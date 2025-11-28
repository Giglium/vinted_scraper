# pylint: disable=line-too-long
"""
Test the log utils class
"""
import logging
import sys
import unittest

from src.vinted_scraper.utils import (
    log_constructor,
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
            self.assertEqual(
                cm.output,
                [
                    f"DEBUG:{__name__}:Create object {self.__class__.__name__} with baseurl {BASE_URL}, agent {USER_AGENT}, session_cookie {COOKIE_VALUE} and config {config}"  # noqa E501
                ],
            )

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

        for i in range(0, 5):
            # Case DEBUG enabled
            with self.assertLogs(level=logging.DEBUG) as cm:
                log_interaction(log=log, i=i)
                self.assertEqual(
                    cm.output,
                    [f"DEBUG:{__name__}:Interaction {i}"],
                )

            # Case Debug disable
            assert_no_logs(log_interaction, self, log=log, level=logging.INFO, i=i)

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
            log_refresh_cookie(
                log=log,
            )
            self.assertEqual(
                cm.output,
                [f"DEBUG:{__name__}:refreshing the cookie"],
            )

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
        params = {"search_text": "nike shoes"}
        # Case DEBUG enabled
        with self.assertLogs(level=logging.DEBUG) as cm:
            log_search(log=log, params=params)
            self.assertEqual(
                cm.output,
                [f"DEBUG:{__name__}:Searching with params {params}"],
            )

        # Case Debug disable
        assert_no_logs(log_search, self, log=log, level=logging.INFO, params=params)

        # Case with None params
        with self.assertLogs(level=logging.DEBUG) as cm:
            log_search(log=log, params=None)
            self.assertEqual(
                cm.output,
                [f"DEBUG:{__name__}:Searching with params None"],
            )

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
            self.assertEqual(
                cm.output,
                [f"DEBUG:{__name__}:Fetching item {item_id} with params {params}"],
            )

        # Case Debug disable
        assert_no_logs(
            log_item, self, log=log, level=logging.INFO, item_id=item_id, params=params
        )

        # Case with None params
        with self.assertLogs(level=logging.DEBUG) as cm:
            log_item(log=log, item_id=item_id, params=None)
            self.assertEqual(
                cm.output,
                [f"DEBUG:{__name__}:Fetching item {item_id} with params None"],
            )

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
            self.assertEqual(
                cm.output,
                [f"DEBUG:{__name__}:Calling endpoint {endpoint} with params {params}"],
            )

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
            self.assertEqual(
                cm.output,
                [f"DEBUG:{__name__}:Calling endpoint {endpoint} with params None"],
            )

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
        headers = {"User-Agent": USER_AGENT, "Cookie": f"_vinted_fr_session={COOKIE_VALUE}"}
        params = {"search_text": "nike"}

        # Case DEBUG enabled with params
        with self.assertLogs(level=logging.DEBUG) as cm:
            log_curl_request(log=log, base_url=base_url, endpoint=endpoint, headers=headers, params=params)
            self.assertEqual(len(cm.output), 2)
            self.assertIn("API Request: GET /catalog/items with params", cm.output[0])
            self.assertIn("Curl command:", cm.output[1])
            self.assertIn("curl", cm.output[1])
            self.assertIn(USER_AGENT, cm.output[1])

        # Case DEBUG enabled without params
        with self.assertLogs(level=logging.DEBUG) as cm:
            log_curl_request(log=log, base_url=base_url, endpoint=endpoint, headers=headers, params=None)
            self.assertEqual(len(cm.output), 2)
            self.assertIn("API Request: GET /catalog/items with params None", cm.output[0])

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
            log_curl_response(log=log, endpoint=endpoint, status_code=status_code, headers=headers, body=body)
            self.assertEqual(len(cm.output), 3)
            self.assertIn("API Response: /catalog/items - Status: 200", cm.output[0])
            self.assertIn("Response Headers:", cm.output[1])
            self.assertIn("Response Body:", cm.output[2])

        # Case DEBUG enabled without body
        with self.assertLogs(level=logging.DEBUG) as cm:
            log_curl_response(log=log, endpoint=endpoint, status_code=status_code, headers=headers, body=None)
            self.assertEqual(len(cm.output), 2)
            self.assertIn("API Response:", cm.output[0])
            self.assertIn("Response Headers:", cm.output[1])

        # Case with long body (should be truncated)
        long_body = "x" * 2000
        with self.assertLogs(level=logging.DEBUG) as cm:
            log_curl_response(log=log, endpoint=endpoint, status_code=status_code, headers=headers, body=long_body)
            self.assertIn("truncated", cm.output[2])


if __name__ == "__main__":
    unittest.main()
