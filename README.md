# Vinted Scraper

[![Package Version](https://img.shields.io/pypi/v/vinted_scraper.svg)](https://pypi.org/project/vinted_scraper/)
[![Python Version](https://img.shields.io/pypi/pyversions/vinted_scraper.svg)](https://pypi.org/project/vinted_scraper/)
[![License](https://img.shields.io/pypi/l/vinted_scraper.svg)](https://github.com/Giglium/vinted_scraper/blob/main/LICENSE)

A very simple Python package that scrapes the Vinted site to retrieve information about its items.

## Installation

You can install Vinted Scraper using pip:

```shell
    pip install vinted_scraper
```

## Usage

The package offers two functions:

1. The `search` function gets all the items present on the listing page
2. The `get_item` function gets more information about an item, and its seller present on the item detail page.

> If you want to parse and manage the scraped data directly you can use the `raw` functions.

Here's the two-way of how to use the package:

### Structured Data

To obtain the scraped data as a `vinted_scraper.VintedItem`, so you can:

```python
import vinted_scraper


def main():
    params = {
        "search_text": "board games"
        # Add other query parameters like the pagination and so on
    }
    items = vinted_scraper.search("https://www.vinted.com/catalog", params)  # get all the items
    item = items[0]  # get the first Item of the list
    vinted_scraper.get_item(item.url)  # get more info about a particular product


if __name__ == "__main__":
    main()
```

> Structured Data are parsed and converted into a `vinted_scraper.VintedItem` object. If some attributes are `None` means
> that it wasn't found in the scrap. Also, I discard some attribute that I thought was useless.

### Raw Data

To obtain the scraped data as a `Dict`, so you can:

```python
import vinted_scraper


def main():
    params = {
        "search_text": "board games"
        # Add other query parameters like the pagination and so on
    }
    items = vinted_scraper.raw_search("https://www.vinted.com/catalog", params)  # get all the items
    item = items[0]  # get the first Item of the list
    vinted_scraper.get_raw_item(item["url"])  # get more info about the item


if __name__ == "__main__":
    main()
```

## License

This project is licensed under the MIT License - see
the [LICENSE](https://github.com/Giglium/vinted_scraper/blob/main/LICENSE) file for details.