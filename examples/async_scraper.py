import asyncio
from vinted_scraper import AsyncVintedScraper
from time import sleep


async def main():
    scraper = await AsyncVintedScraper.create("https://www.vinted.com")
    params = {"search_text": "board games"}
    _ = await scraper.search(params)


if __name__ == "__main__":
    max_retries = 5
    retries = 0

    # retry multiple times since in the CI it sometimes fails due to much requests
    while retries < max_retries:
        try:
            asyncio.run(main())
        except Exception as e:
            retries += 1
            if retries == max_retries:
                raise e
            else:
                sleep(2**retries)  # Waiting before retrying
