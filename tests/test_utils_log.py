# pylint: disable=line-too-long
"""
Test the log utils class
"""
import logging
import sys
import unittest

from src.vinted_scraper.utils import (
    log_constructor,
    log_interaction,
    log_refresh_cookie,
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
                [f"DEBUG:{__name__}:refrshing the cookie"],
            )

        # Case Debug disable
        assert_no_logs(
            log_refresh_cookie,
            self,
            log=log,
            level=logging.INFO,
        )


if __name__ == "__main__":
    unittest.main()
