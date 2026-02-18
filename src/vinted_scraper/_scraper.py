# jscpd:ignore-start
# pylint: disable=missing-module-docstring,duplicate-code
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

from ._wrapper import VintedWrapper
from .models import VintedItem, VintedJsonModel

_log = logging.getLogger(__name__)


@dataclass
class VintedScraper(VintedWrapper):
    """
    Vinted client with data model support
    """

    def search(self, params: Optional[Dict] = None) -> List[VintedItem]:  # type: ignore
        """
        Search for items on Vinted.

        :param params: an optional Dictionary with all the query parameters to append
            to the request. Vinted supports a search without any parameters, but to
            perform a search, you should add the `search_text` parameter.
            Default value: None.
        :return: A list of VintedItem instances representing search results.
        """
        return [VintedItem(json_data=item) for item in super().search(params)["items"]]

    def item(self, item_id: str, params: Optional[Dict] = None) -> VintedItem:  # type: ignore
        """
        Retrieve details of a specific item on Vinted.

        :param item_id: The unique identifier of the item to retrieve.
        :param params: an optional Dictionary with all the query parameters to append
            to the request. Default value: None.
        :return: A VintedItem instance representing the item's details.
        """
        return VintedItem(json_data=super().item(item_id, params)["item"])

    def curl(self, endpoint: str, params: Optional[Dict] = None) -> VintedJsonModel:  # type: ignore
        """
        Send an HTTP GET request to the specified endpoint.

        :param endpoint: The endpoint to make the request to.
        :param params: An optional dictionary with query parameters to include in the request.
        :return: A VintedJsonModel instance with the JSON response.
        """
        response = super().curl(endpoint, params)
        return VintedJsonModel(json_data=response)


# jscpd:ignore-end
