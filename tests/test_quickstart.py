import unittest
from time import sleep

from src.vinted_scraper.vintedScraper import VintedScraper
from src.vinted_scraper.vintedWrapper import VintedWrapper


class TestQuickstarts(unittest.TestCase):
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
                items = wrapper.search(params)
                if len(items["items"]) > 0:
                    wrapper.item(items["items"][0]["id"])
                else:
                    sleep(
                        2**retries
                    )  # when you call multiple times the search sometimes returns an empty result
                    self.test_raw_quick_start()
                break  # Test was successful

            except Exception as e:
                retries += 1
                if retries == max_retries:
                    self.fail(
                        f"Quick raised an exception after {max_retries} attempts: {e}"
                    )
                else:
                    sleep(2**retries)  # Waiting before retrying

    def test_quick_start(self):
        """
        Ensure that the scrapper quickstart doesn't raise any exceptions
        """
        max_retries = 5
        retries = 0

        # retry multiple times since in the CI it sometimes fails due to much parallel requests
        while retries < max_retries:
            try:
                scraper = VintedScraper(self.baseurl)
                params = {"search_text": "board games"}
                items = scraper.search(params)
                if len(items) > 0:
                    scraper.item(items[0].id)
                else:
                    # when you call multiple times the search sometimes returns an empty result
                    sleep(2)
                    self.test_raw_quick_start()
                break  # Test was successful

            except Exception as e:
                retries += 1
                if retries == max_retries:
                    self.fail(
                        f"Quick raised an exception after {max_retries} attempts: {e}"
                    )
                else:
                    sleep(2**retries)  # Waiting before retrying

    def test_cookies_retry(self):
        try:
            wrapper = VintedWrapper(self.baseurl, session_cookie="invalid_cookie")
            wrapper.search()
        except Exception as e:
            self.fail(f"exception: {e}")


if __name__ == "__main__":
    unittest.main()
