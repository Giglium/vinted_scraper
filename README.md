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

> If you are on Python 3.6 you also have to install `dataclasses`: `pip install dataclasses`

## Functions

The package offers the following functions:
<details>
 <summary><code>search</code> - <code>(gets all the items present on the listing page)</code></summary>

  **Parameters**

> | name   | type     | data type | description                                    |
> |--------|----------|-----------|------------------------------------------------|
> | params | optional | Dict      | Query parameters like the pagination and so on |
</details>

<details>
 <summary><code>item</code> - <code>(gets the information about an item, and its seller present on the item detail page)</code></summary>

  **Parameters**

> | name   | type     | data type | description                                   |
> |--------|----------|-----------|-----------------------------------------------|
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

## License

This project is licensed under the MIT License - see
the [LICENSE](https://github.com/Giglium/vinted_scraper/blob/main/LICENSE) file for details.