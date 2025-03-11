# jscpd:ignore-start
# pylint: disable=broad-exception-caught,duplicate-code
"""
Test the async quick starts present on the README
"""
import asyncio
import unittest

from src.vinted_scraper import AsyncVintedScraper, AsyncVintedWrapper


class TestAsyncQuickStarts(unittest.IsolatedAsyncioTestCase):
    """
    This class will perform a read API call to Vinted to test if the integration is working
    """

    def setUp(self):
        self.baseurl = "https://www.vinted.com"

    async def test_raw_async_quick_start(self):
        """
        Ensure that the wrapper quickstart doesn't raise any exceptions
        """
        max_retries = 5
        retries = 0

        # retry multiple times since in the CI it sometimes fails due to much parallel requests
        while retries < max_retries:
            try:
                wrapper = await AsyncVintedWrapper.create(self.baseurl)
                params = {"search_text": "board games"}
                items = await wrapper.search(params)
                if len(items["items"]) > 0:
                    await wrapper.item(items["items"][0]["id"])
                else:
                    await asyncio.sleep(
                        2**retries
                    )  # when you call multiple times the search sometimes returns an empty result
                    self.test_raw_async_quick_start()
                break  # Test was successful

            except Exception as e:
                retries += 1
                if retries == max_retries:
                    self.fail(
                        f"Quick raised an exception after {max_retries} attempts: {e}"
                    )
                else:
                    await asyncio.sleep(2**retries)  # Waiting before retrying

    async def test_async_quick_start(self):
        """
        Ensure that the scraper quickstart doesn't raise any exceptions
        """
        max_retries = 5
        retries = 0

        # retry multiple times since in the CI it sometimes fails due to much parallel requests
        while retries < max_retries:
            try:
                scraper = await AsyncVintedScraper.create(self.baseurl)
                params = {"search_text": "board games"}
                items = await scraper.search(params)
                if len(items) > 0:
                    await scraper.item(items[0].id)
                else:
                    await asyncio.sleep(
                        2**retries
                    )  # when you call multiple times the search sometimes returns an empty result
                    self.test_async_quick_start()
                break  # Test was successful

            except Exception as e:
                retries += 1
                if retries == max_retries:
                    self.fail(
                        f"Quick raised an exception after {max_retries} attempts: {e}"
                    )
                else:
                    await asyncio.sleep(2**retries)  # Waiting before retrying


if __name__ == "__main__":
    unittest.main()
# jscpd:ignore-end
