# jscpd:ignore-start
# pylint: disable=duplicate-code
"""Vinted scraper with typed model support."""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

from ._wrapper import VintedWrapper
from .models import VintedItem, VintedJsonModel

_log = logging.getLogger(__name__)


@dataclass
class VintedScraper(VintedWrapper):
    """Synchronous Vinted scraper with typed model support.

    Returns structured VintedItem objects instead of raw JSON dictionaries.
    Inherits all functionality from VintedWrapper.

    Example:
       See https://github.com/Giglium/vinted_scraper/blob/main/examples/scraper.py
    """

    def search(self, params: Optional[Dict] = None) -> List[VintedItem]:  # type: ignore
        """Search for items on Vinted.

        Args:
            params: Query parameters for the search. Common parameters:
                - search_text: Search query
                - page: Page number
                - per_page: Items per page
                - price_from: Minimum price
                - price_to: Maximum price
                - order: Sort order
                - catalog_ids: Category IDs
                - brand_ids: Brand IDs
                - size_ids : Size IDs

        Returns:
            List of VintedItem objects representing search results.
        """
        return [VintedItem(json_data=item) for item in super().search(params)["items"]]

    def item(self, item_id: str, params: Optional[Dict] = None) -> VintedItem:  # type: ignore
        """Retrieve detailed information about a specific item.

        Args:
            item_id: The unique identifier of the item.
            params: Optional query parameters.

        Returns:
            VintedItem object with detailed item information including seller details.

        Raises:
            RuntimeError: If the item is not found or API returns an error.

        Note:
            It returns a 403 error after a few uses.
            See: https://github.com/Giglium/vinted_scraper/issues/59
        """
        return VintedItem(json_data=super().item(item_id, params)["item"])

    def curl(self, endpoint: str, params: Optional[Dict] = None) -> VintedJsonModel:  # type: ignore
        """Send a custom HTTP GET request to any Vinted API endpoint.

        Args:
            endpoint: The API endpoint path (e.g., "/api/v2/users/username").
            params: Optional query parameters.

        Returns:
            VintedJsonModel containing the JSON response.

        Raises:
            RuntimeError: If the request fails or returns a non-200 status code.
        """
        response = super().curl(endpoint, params)
        return VintedJsonModel(json_data=response)


# jscpd:ignore-end
