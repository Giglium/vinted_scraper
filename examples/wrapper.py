from vinted_scraper import VintedWrapper
from time import sleep


def main():
    wrapper = VintedWrapper("https://www.vinted.com")
    params = {"search_text": "board games"}
    _ = wrapper.search(params)


if __name__ == "__main__":
    max_retries = 5
    retries = 0

    # retry multiple times since in the CI it sometimes fails due to much requests
    while retries < max_retries:
        try:
            main()
        except Exception as e:
            retries += 1
            if retries == max_retries:
                raise e
            else:
                sleep(2**retries)  # Waiting before retrying
