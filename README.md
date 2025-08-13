# Vinted Scraper

[![Package Version](https://img.shields.io/pypi/v/vinted_scraper.svg)](https://pypi.org/project/vinted_scraper/)
[![Python Version](https://img.shields.io/pypi/pyversions/vinted_scraper.svg)](https://pypi.org/project/vinted_scraper/)
[![codecov](https://codecov.io/gh/Giglium/vinted_scraper/graph/badge.svg?token=EB36V1AO72)](https://codecov.io/gh/Giglium/vinted_scraper)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/4722ef5a944a495394acb1b7cf88f3ae)](https://app.codacy.com/gh/Giglium/vinted_scraper?utm_source=github.com&utm_medium=referral&utm_content=Giglium/vinted_scraper&utm_campaign=Badge_Grade)
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

> It is currently not working and will throw a 404 status code (see [#78](https://github.com/Giglium/vinted_scraper/issues/78)). Vinted has changed this endpoint, and we didn't find a replacement.

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


if __name__ == "__main__":
    main()
```

## License

This project is licensed under the MIT License - see
the [LICENSE](https://github.com/Giglium/vinted_scraper/blob/main/LICENSE) file for details.

[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FGiglium%2Fvinted_scraper.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2FGiglium%2Fvinted_scraper?ref=badge_large)
