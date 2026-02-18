# jscpd:ignore-start
# pylint: disable=duplicate-code
"""Async Vinted scraper with typed model support."""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

from ._async_wrapper import AsyncVintedWrapper
from .models import VintedItem, VintedJsonModel

_log = logging.getLogger(__name__)


@dataclass
class AsyncVintedScraper(AsyncVintedWrapper):
    """Asynchronous Vinted scraper with typed model support.

    Returns structured VintedItem objects instead of raw JSON dictionaries.
    Inherits all functionality from AsyncVintedWrapper.

    Example:
        See https://github.com/Giglium/vinted_scraper/blob/main/examples/async_scraper.py
    """

    async def search(self, params: Optional[Dict] = None) -> List[VintedItem]:
        """Search for items on Vinted asynchronously.

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
                - size_ids: Size IDs

        Returns:
            List of VintedItem objects representing search results.
        """
        response = await super().search(params)
        return [VintedItem(json_data=item) for item in response["items"]]

    async def item(self, item_id: str, params: Optional[Dict] = None) -> VintedItem:
        """Retrieve detailed information about a specific item asynchronously.

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
        response = await super().item(item_id, params)
        return VintedItem(json_data=response["item"])

    async def curl(
        self, endpoint: str, params: Optional[Dict] = None
    ) -> VintedJsonModel:
        """Send an async HTTP GET request to any Vinted API endpoint.

        Args:
            endpoint: The API endpoint path (e.g., "/api/v2/users/username").
            params: Optional query parameters.

        Returns:
            VintedJsonModel containing the JSON response.

        Raises:
            RuntimeError: If the request fails or returns a non-200 status code.

        """
        response = await super().curl(endpoint, params)
        return VintedJsonModel(json_data=response)


# jscpd:ignore-end
