# Vinted Scraper

[![Package Version](https://img.shields.io/pypi/v/vinted_scraper.svg)](https://pypi.org/project/vinted_scraper/)
[![Python Version](https://img.shields.io/pypi/pyversions/vinted_scraper.svg)](https://pypi.org/project/vinted_scraper/)
[![codecov](https://codecov.io/gh/Giglium/vinted_scraper/graph/badge.svg?token=EB36V1AO72)](https://codecov.io/gh/Giglium/vinted_scraper)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/4722ef5a944a495394acb1b7cf88f3ae)](https://app.codacy.com/gh/Giglium/vinted_scraper?utm_source=github.com&utm_medium=referral&utm_content=Giglium/vinted_scraper&utm_campaign=Badge_Grade)
[![License](https://img.shields.io/pypi/l/vinted_scraper.svg)](https://github.com/Giglium/vinted_scraper/blob/main/LICENSE)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FGiglium%2Fvinted_scraper.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2FGiglium%2Fvinted_scraper?ref=badge_shield)

A very simple Python package for scraping Vinted. Supports both synchronous and asynchronous operations with automatic cookie management and typed responses.

📖 **[Full Documentation](https://giglium.github.io/vinted_scraper/vinted_scraper.html)** | 💡 **[Examples](https://github.com/Giglium/vinted_scraper/tree/main/examples)** | 📝 **[Changelog](https://github.com/Giglium/vinted_scraper/releases)**

## Installation

Install using pip:

```shell
pip install vinted_scraper
```

## Functions

The package offers the following methods:

<details>
 <summary><code>search</code> - <code>Gets all items from the listing page based on search parameters.</code></summary>

**Parameters**

> | name   | type     | data type | description                                    |
> | ------ | -------- | --------- | ---------------------------------------------- |
> | params | optional | Dict      | Query parameters like the pagination and so on |

**Returns:** `List[VintedItem]` (VintedScraper) or `Dict[str, Any]` (VintedWrapper)

</details>

<details>
 <summary><code>item</code> - <code>Gets detailed information about a specific item and its seller.</code></summary>

> It returns a 403 error after a few uses. See [#58](https://github.com/Giglium/vinted_scraper/issues/59)).

**Parameters**

> | name   | type     | data type | description                                   |
> | ------ | -------- | --------- | --------------------------------------------- |
> | id     | required | str       | The unique identifier of the item to retrieve |
> | params | optional | Dict      | I don't know if they exist                    |

**Returns:** `VintedItem` (VintedScraper) or `Dict[str, Any]` (VintedWrapper)

</details>

<details>
 <summary><code>curl</code> - <code>Perform an HTTP GET request to the given endpoint.</code></summary>

**Parameters**

> | name     | type     | data type | description                                    |
> | -------- | -------- | --------- | ---------------------------------------------- |
> | endpoint | required | str       | The endpoint to make the request to            |
> | params   | optional | Dict      | Query parameters like the pagination and so on |

**Returns:** `VintedJsonModel` (VintedScraper) or `Dict[str, Any]` (VintedWrapper)

</details>

## Usage

```python
from vinted_scraper import VintedScraper

scraper = VintedScraper("https://www.vinted.com")
items = scraper.search({"search_text": "board games"})

for item in items:
    print(f"{item.title} - {item.price}")
```

> Check out the [examples](https://github.com/Giglium/vinted_scraper/tree/main/examples) for more!

## Debugging

To enable debug logging for troubleshooting:

```python
import logging

# Configure logging BEFORE importing vinted_scraper
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s:%(name)s:%(message)s"
)

from vinted_scraper import VintedScraper

scraper = VintedScraper("https://www.vinted.com")
scraper.search({"search_text": "board games"})
```

<details>
<summary>Debug output (click to expand)</summary>

```bash
DEBUG:vinted_scraper._vinted_wrapper:Initializing VintedScraper(baseurl=https://www.vinted.com, user_agent=None, session_cookie=auto-fetch, config=None)
DEBUG:vinted_scraper._vinted_wrapper:Refreshing session cookie
DEBUG:vinted_scraper._vinted_wrapper:Cookie fetch attempt 1/3
DEBUG:vinted_scraper._vinted_wrapper:Session cookie fetched successfully: eyJraWQiOiJFNTdZZHJ1...
DEBUG:vinted_scraper._vinted_wrapper:Calling search() with params: {'search_text': 'board games'}
DEBUG:vinted_scraper._vinted_wrapper:API Request: GET /api/v2/catalog/items with params {'search_text': 'board games'}
DEBUG:vinted_scraper._vinted_wrapper:API Response: /api/v2/catalog/items - Status: 200
```

</details>

### Common Issues

- **403 Forbidden Error**: The `item()` method frequently return 403 errors ([#58](https://github.com/Giglium/vinted_scraper/issues/59)).

- **Cookie Fetch Failed**: If cookies cannot be fetched:
  - Verify the base URL is correct
  - Check your internet connection, some VPN are banned. Try manually getting the cookie by running the following:

  ```bash
    curl -v -c - -L "<base-url>" | grep access_token_web
  ```

## License

This project is licensed under the MIT License - see
the [LICENSE](https://github.com/Giglium/vinted_scraper/blob/main/LICENSE) file for details.

[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FGiglium%2Fvinted_scraper.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2FGiglium%2Fvinted_scraper?ref=badge_large)
