# jscpd:ignore-start
# pylint: disable=missing-module-docstring,duplicate-code

import logging
from typing import Dict, List, Optional

from ._async_vinted_wrapper import AsyncVintedWrapper
from .models import VintedItem

_log = logging.getLogger(__name__)


class AsyncVintedScraper(AsyncVintedWrapper):
    """
    Async Vinted client with data model support
    """

    async def search(self, params: Optional[Dict] = None) -> List[VintedItem]:
        """
        Search for items on Vinted.

        :param params: an optional Dictionary with all the query parameters to append
            to the request. Vinted supports a search without any parameters,
            but to perform a search, you should add the `search_text` parameter.
            Default value: None.
        :return: A list of VintedItem instances representing search results.
        """
        response = await super().search(params)
        return [VintedItem(item) for item in response["items"]]

    async def item(self, item_id: str, params: Optional[Dict] = None) -> VintedItem:
        """
        Retrieve details of a specific item on Vinted.

        :param item_id: The unique identifier of the item to retrieve.
        :param params: an optional Dictionary with all the query parameters to append
            to the request. Default value: None.
        :return: A VintedItem instance representing the item's details.
        """
        response = await super().item(item_id, params)
        return VintedItem(response["item"])


# jscpd:ignore-end
