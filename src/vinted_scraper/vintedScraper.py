from typing import Dict, List, Optional

from . import VintedWrapper
from .models import VintedItem


class VintedScraper(VintedWrapper):
    def __init__(self, baseurl: str, agent=None, session_cookie=None):
        super().__init__(baseurl, agent, session_cookie)

    def search(self, params: Optional[Dict] = None) -> List[VintedItem]: # type: ignore
        """
        :param params: an optional Dictionary with all the query parameters to append at the request.
            Vinted support a search without any param but to perform a search you should add the `search_text` params.
            Default value: None.
        """
        return [VintedItem(item) for item in super().search(params)["items"]]

    # def item(self, id: str, params: Optional[Dict] = None) -> Dict:
    #     """
    #     :param id:
    #     :param params: an optional Dictionary with all the query parameters to append at the request.
    #         Vinted support a search without any param but to perform a search you should add the `search_text` params.
    #         Default value: None.
    #     """
    #     pass
    #     #return self._curl(f"/items/{id}", params=params)
