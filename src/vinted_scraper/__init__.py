import json
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from .VintedItem import VintedItem


def raw_search(url: str, params: Optional[Dict] = None) -> List[Dict]:
    """
    Retrieves items from a given search url on Vinted.
    :param url: the Vinted url to fetch
    :param params: an optional Dictionary with all the query parameters to append at the request.
        Vinted support a search without any param but to perform a search you should add the `search_text` params.
        Default value: None.
    """
    return list(
        _parse_html(_curl(url, params), {"data-js-react-on-rails-store": "MainStore"})[
            "items"
        ]["catalogItems"]["byId"].values()
    )


def search(url: str, params: Optional[Dict] = None) -> list[VintedItem]:
    """
    Retrieves items from a given search url on Vinted.
    :param url: the Vinted url to fetch
    :param params: an optional Dictionary with all the query parameters to append at the request.
        Vinted support a search without any param but to perform a search you should add the `search_text` params.
        Default value: None.
    """
    return [VintedItem(i) for i in raw_search(url, params)]


def get_raw_item(url: str) -> Dict:
    """
    Retrieves items from a given search url on Vinted.
    :param url: the url Vinted url to fetch
    """
    return _parse_html(_curl(url), {"data-component-name": "ItemDetails"})["item"]


def get_item(url: str) -> VintedItem:
    """
    Retrieves items from a given search url on Vinted.
    :param url: the url Vinted url to fetch
    """
    return VintedItem(get_raw_item(url))


def _parse_html(html_content: bytes, attrs: dict[str, str]):
    """
    Utils function that scraps the given HTML and find `<script>` tags with the given `attrs`
    :param html_content: html content, you can get it from requests.get() call or by "<html><!-- --></html>".encode()
    :param attrs: an attribute to search, for example {"class": "foo"} it will search for a html like <div class="foo">
    """
    soup = BeautifulSoup(html_content, "html.parser")
    script_tag = soup.find("script", attrs)

    if script_tag is not None:
        return json.loads(script_tag.string)
    else:
        raise RuntimeError(f"Cannot parse the content. Script tag `{attrs}` not found.")


def _curl(url: str, params: Optional[Dict] = None) -> bytes:
    """
    Perform a request to Vinted and fetch its content.
    :param url: the Vinted url to fetch
    :param params: an optional Dictionary with all the query parameters to append at the request. Default value: None.
    """
    headers = {
        # This one is the most common user agent right now
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    response = requests.get(url, params=params, headers=headers)
    if 200 == response.status_code:
        return response.content
    else:
        raise RuntimeError(f"Cannot perform search, error code: {response.status_code}")
