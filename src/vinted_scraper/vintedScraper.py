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
        verify_ssl: bool = True,
    ):
        """
        Vinted scraping client with data model support
        
        :param baseurl: (required) Base Vinted site url to use in the requests
        :param agent: (optional) User agent to use on the requests
        :param session_cookie: (optional) Vinted session cookie
        :param proxies: (optional) Proxy configuration for requests
        :param verify_ssl: (optional) Verify SSL certificates. Recommended for security.
        """
        super().__init__(
            baseurl=baseurl,
            agent=agent,
            session_cookie=session_cookie,
            proxies=proxies,
            verify_ssl=verify_ssl,
        )

    def search(self, params: Optional[Dict] = None) -> List[VintedItem]:  # type: ignore
        """
        Search for items on Vinted with model conversion
        
        :param params: Dictionary with search parameters
        :return: List of VintedItem objects
        """
        raw_results = super().search(params)
        return [VintedItem(item) for item in raw_results.get("items", [])]

    def item(self, item_id: str, params: Optional[Dict] = None) -> VintedItem:  # type: ignore
        """
        Get detailed item information with model conversion
        
        :param item_id: Vinted item ID
        :param params: Additional query parameters
        :return: VintedItem object
        """
        raw_data = super().item(item_id, params)
        return VintedItem(raw_data.get("item", {}))
