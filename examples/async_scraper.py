# jscpd:ignore-start
# pylint: disable=missing-module-docstring,missing-function-docstring,duplicate-code,broad-exception-caught

import asyncio
from time import sleep

from vinted_scraper import AsyncVintedScraper


async def main():
    scraper = await AsyncVintedScraper.create("https://www.vinted.com")
    params = {"search_text": "board games"}
    _ = await scraper.search(params)


if __name__ == "__main__":
    MAX_RETRIES = 5
    retries: int = 0

    # retry multiple times since in the CI it sometimes fails due to much requests
    while retries < MAX_RETRIES:
        try:
            asyncio.run(main())
        except Exception as e:
            retries += 1
            if retries == MAX_RETRIES:
                raise e
            sleep(2**retries)  # Waiting before retrying

# jscpd:ignore-end
