from typing import Dict, List, Optional

from .models import VintedItem
from .vintedWrapper import VintedWrapper


class VintedScraper(VintedWrapper):
    def __init__(
        self,
        baseurl: str,
        agent: Optional[str] = None,
        session_cookie: Optional[str] = None,
        proxies: Optional[Dict] = None,
    ):
        """
        :param baseurl: (required) Base Vinted site url to use in the requests
        :param agent: (optional) User agent to use on the requests
        :param session_cookie: (optional) Vinted session cookie
        :param proxies: (optional) Dictionary mapping protocol or protocol and
        hostname to the URL of the proxy. For more info see:
        https://requests.readthedocs.io/en/latest/user/advanced/#proxies
        """
        super().__init__(baseurl, agent, session_cookie, proxies)

    def search(self, params: Optional[Dict] = None) -> List[VintedItem]:  # type: ignore
        """
        Search for items on Vinted.

        :param params: an optional Dictionary with all the query parameters to append to the request.
            Vinted supports a search without any parameters, but to perform a search,
            you should add the `search_text` parameter.
            Default value: None.
        :return: A list of VintedItem instances representing search results.
        """
        return [VintedItem(item) for item in super().search(params)["items"]]

    def item(self, item_id: str, params: Optional[Dict] = None) -> VintedItem:  # type: ignore
        """
        Retrieve details of a specific item on Vinted.

        :param item_id: The unique identifier of the item to retrieve.
        :param params: an optional Dictionary with all the query parameters to append to the request.
            Default value: None.
        :return: A VintedItem instance representing the item's details.
        """
        return VintedItem(super().item(item_id, params)["item"])
