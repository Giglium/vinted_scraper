from .VintedWrapper import VintedWrapper  # noqa: F401

# import json
# import os
# import random
# from typing import Dict, List, Optional
# from urllib.parse import urlparse, urlunparse
#
# import requests
# from bs4 import BeautifulSoup
#
# from .VintedItem import VintedItem
#
# cookie = "ciccio"
#
#
# def raw_search(url: str, params: Optional[Dict] = None) -> List[Dict]:
#     """
#     Retrieves items from a given search url on Vinted.
#     :param url: the Vinted url to fetch
#     :param params: an optional Dictionary with all the query parameters to append at the request.
#         Vinted support a search without any param but to perform a search you should add the `search_text` params.
#         Default value: None.
#     """
#     return list(
#         _parse_html(_curl(url, params), {"data-js-react-on-rails-store": "MainStore"})[
#             "items"
#         ]["catalogItems"]["byId"].values()
#     )
#
#
# def search(url: str, params: Optional[Dict] = None) -> list[VintedItem]:
#     """
#     Retrieves items from a given search url on Vinted.
#     :param url: the Vinted url to fetch
#     :param params: an optional Dictionary with all the query parameters to append at the request.
#         Vinted support a search without any param but to perform a search you should add the `search_text` params.
#         Default value: None.
#     """
#     return [VintedItem(i) for i in raw_search(url, params)]
#
#
# def get_raw_item(url: str) -> Dict:
#     """
#     Retrieves items from a given search url on Vinted.
#     :param url: the url Vinted url to fetch
#     """
#     parsed_url = urlparse(url)
#
#     # Remove query parameters
#     parsed_url = parsed_url._replace(query="")
#
#     # Add "/api/v2" before "/items"
#     path_parts = parsed_url.path.split("/")
#     path_parts.insert(1, "api")
#     path_parts.insert(2, "v2")
#     parsed_url = parsed_url._replace(path="/".join(path_parts))
#
#     modified_url = urlunparse(parsed_url)
#     return json.loads(_curl(modified_url))
#
#
# def get_item(url: str) -> VintedItem:
#     """
#     Retrieves items from a given search url on Vinted.
#     :param url: the url Vinted url to fetch
#     """
#     return VintedItem(get_raw_item(url)["item"])
#
#
#
# def _curl(url: str, params: Optional[Dict] = None) -> bytes:
#     """
#     Perform a request to Vinted and fetch its content.
#     :param url: the Vinted url to fetch
#     :param params: an optional Dictionary with all the query parameters to append at the request. Default value: None.
#     """
#     global cookie
#     headers = {
#         "User-Agent": get_random_user_agent(),
#         "Cookie": f"_vinted_fr_session={cookie}",
#     }
#     response = requests.get(url, params=params, headers=headers)
#
#     session_cookie = response.headers.get("Set-Cookie")
#     if session_cookie and "secure, _vinted_fr_session=" in session_cookie:
#         cookie = session_cookie.split("secure, _vinted_fr_session=")[1].split(";")[0]
#
#     if 200 == response.status_code:
#         return response.content
#     if 401 == response.status_code:
#         # run an empty search to get the cookie
#         raw_search("https://www.vinted.com/catalog")
#         return _curl(url, params)
#     else:
#         raise RuntimeError(f"Cannot perform search, error code: {response.status_code}")
#
#
