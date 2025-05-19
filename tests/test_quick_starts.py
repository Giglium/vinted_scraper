# jscpd:ignore-start
# pylint: disable=broad-exception-caught,duplicate-code
"""
Test the quick starts present on the README
"""
import time
import unittest

from src.vinted_scraper import VintedScraper, VintedWrapper


class TestQuickStarts(unittest.TestCase):
    """
    This class will perform a read API call to Vinted to test if the integration is working
    """

    def setUp(self):
        self.baseurl = "https://www.vinted.com"

    def test_raw_quick_start(self):
        """
        Ensure that the wrapper quickstart doesn't raise any exceptions
        """
        max_retries = 5
        retries = 0

        # retry multiple times since in the CI it sometimes fails due to much parallel requests
        while retries < max_retries:
            try:
                wrapper = VintedWrapper(self.baseurl)
                params = {"search_text": "board games"}
                wrapper.search(params)
                #items = wrapper.search(params)
                # if len(items["items"]) > 0:
                #     wrapper.item(items["items"][0]["id"])
                # else:
                #     time.sleep(
                #         2**retries
                #     )  # when you call multiple times the search sometimes returns an empty result
                #     self.test_raw_quick_start()
                break  # Test was successful

            except Exception as e:
                retries += 1
                if retries == max_retries:
                    self.fail(
                        f"Quick raised an exception after {max_retries} attempts: {e}"
                    )
                else:
                    time.sleep(2**retries)  # Waiting before retrying

    def test_quick_start(self):
        """
        Ensure that the scraper quickstart doesn't raise any exceptions
        """
        max_retries = 5
        retries = 0

        # retry multiple times since in the CI it sometimes fails due to much parallel requests
        while retries < max_retries:
            try:
                scraper = VintedScraper(self.baseurl)
                params = {"search_text": "board games"}
                scraper.search(params)
                # items = scraper.search(params)
                # if len(items) > 0:
                #     scraper.item(items[0].id)
                # else:
                #     time.sleep(
                #         2**retries
                #     )  # when you call multiple times the search sometimes returns an empty result
                #     self.test_quick_start()
                break  # Test was successful

            except Exception as e:
                retries += 1
                if retries == max_retries:
                    self.fail(
                        f"Quick raised an exception after {max_retries} attempts: {e}"
                    )
                else:
                    time.sleep(2**retries)  # Waiting before retrying


if __name__ == "__main__":
    unittest.main()
# jscpd:ignore-end
