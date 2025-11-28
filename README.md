# Vinted Scraper

[![Package Version](https://img.shields.io/pypi/v/vinted_scraper.svg)](https://pypi.org/project/vinted_scraper/)
[![Python Version](https://img.shields.io/pypi/pyversions/vinted_scraper.svg)](https://pypi.org/project/vinted_scraper/)
[![codecov](https://codecov.io/gh/Giglium/vinted_scraper/graph/badge.svg?token=EB36V1AO72)](https://codecov.io/gh/Giglium/vinted_scraper)
[![License](https://img.shields.io/pypi/l/vinted_scraper.svg)](https://github.com/Giglium/vinted_scraper/blob/main/LICENSE)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FGiglium%2Fvinted_scraper.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2FGiglium%2Fvinted_scraper?ref=badge_shield)

A very simple Python package that scrapes the Vinted site to retrieve information about its items.

## Installation

### Stable

You can install Vinted Scraper using pip:

```shell
    pip install vinted_scraper==2.4.0
```

> If you are on Python 3.6 you also have to install `dataclasses`: `pip install dataclasses`

### Alpha

We move from `requests` to `httpx` to support Async API call. Now, you can await `AsyncVintedScraper` or `AsyncVintedWrapper`.
I haven't finish to update all the docs but you can check [async quick starts](./tests/test_async_quick_starts.py) to understand how they work.

To install the alpha version with pip:

```shell
    pip install vinted_scraper==3.0.0a1
```

> Compatible from python 3.8+

For more info about Alpha check the [roadmap](https://github.com/Giglium/vinted_scraper/issues/73), and please if you find a bug open a issue!

## Functions

The package offers the following functions:

<details>
 <summary><code>search</code> - <code>(gets all the items present on the listing page)</code></summary>

**Parameters**

> | name   | type     | data type | description                                    |
> | ------ | -------- | --------- | ---------------------------------------------- |
> | params | optional | Dict      | Query parameters like the pagination and so on |

</details>

<details>
 <summary><code>item</code> - <code>(gets the information about an item, and its seller present on the item detail page)</code></summary>

**Parameters**

> | name   | type     | data type | description                                   |
> | ------ | -------- | --------- | --------------------------------------------- |
> | id     | required | str       | The unique identifier of the item to retrieve |
> | params | optional | Dict      | I don't know is they exist                    |

</details>

## Usage

To obtain the scraped data as a `vinted_scraper.models.VintedItem`, so you can:

```python
import vinted_scraper.VintedScraper


def main():
    scraper = VintedScraper("https://www.vinted.com")  # init the scraper with the baseurl
    params = {
        "search_text": "board games"
        # Add other query parameters like the pagination and so on
    }
    items = scraper.search(params)  # get all the items
    item = items[0]  # get the first Item of the list
    scraper.item(item.id)  # get more info about a particular item


if __name__ == "__main__":
    main()
```

`VintedScraper` returns structured data that are parsed and converted into a `vinted_scraper.models.VintedItem` object.
If some attributes are `None` means that it wasn't found in the response, maybe because they are returned from other
API.
Also, I discard some attribute that I thought was useless but feel free to open an issue or a PR to add them.

If you want to manage the JSON response directly, you should use the `VintedWrapper` object instead of `VintedScraper`.

Here's the way of how to use it:

```python
import vinted_scraper.VintedWrapper


def main():
    wrapper = VintedWrapper("https://www.vinted.com")  # init the scraper with the baseurl
    params = {
        "search_text": "board games"
        # Add other query parameters like the pagination and so on
    }
    items = wrapper.search(params)  # get all the items
    item = items["items"][0]  # get the first Item of the list
    wrapper.item(item["id"])  # get more info about a particular item


if __name__ == "__main__":
    main()
```

## Debugging

To enable debug logging for troubleshooting, you can configure the logger for the `vinted_scraper` package:

```python
import logging

# Enable debug logging for vinted_scraper only
logging.getLogger("vinted_scraper").setLevel(logging.DEBUG)
logging.basicConfig(format="%(levelname)s:%(name)s:%(message)s")

from vinted_scraper import VintedScraper

scraper = VintedScraper("https://www.vinted.com")
scraper.search({"search_text": "nike"})
```

This will output detailed debug information including:
- API request details with parameters
- A reproducible `curl` command that can be copied and executed in bash
- Response status code, headers, and body (truncated for large responses)

Example output:
```
DEBUG:vinted_scraper._vinted_wrapper:Searching with params {'search_text': 'nike'}
DEBUG:vinted_scraper._vinted_wrapper:API Request: GET /catalog/items with params {'search_text': 'nike'}
DEBUG:vinted_scraper._vinted_wrapper:Curl command:
curl \
  -H 'User-Agent: Mozilla/5.0...' \
  -H 'Cookie: _vinted_fr_session=...' \
  'https://www.vinted.com/api/v2/catalog/items?search_text=nike'
DEBUG:vinted_scraper._vinted_wrapper:API Response: /catalog/items - Status: 200
DEBUG:vinted_scraper._vinted_wrapper:Response Headers: {'content-type': 'application/json', ...}
DEBUG:vinted_scraper._vinted_wrapper:Response Body: {"items": [...]}
```

This is helpful when reporting issues as the curl command can be used to reproduce API calls.

## License

This project is licensed under the MIT License - see
the [LICENSE](https://github.com/Giglium/vinted_scraper/blob/main/LICENSE) file for details.

[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FGiglium%2Fvinted_scraper.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2FGiglium%2Fvinted_scraper?ref=badge_large)
