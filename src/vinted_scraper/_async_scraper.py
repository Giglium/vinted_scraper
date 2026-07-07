"""Async Vinted scraper with typed model support."""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

from ._async_wrapper import AsyncVintedWrapper
from .models import OgField, VintedItem, VintedJsonModel

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

    async def item(
        self, item_id: str, fields: Optional[List[str]] = None
    ) -> VintedItem:
        """Read item metadata from the public item page (HTML), asynchronously.

        The JSON item endpoint is blocked by the anti-bot protection and returns
        ``403`` (see https://github.com/Giglium/vinted_scraper/issues/59), so the
        data is read from the public item page instead. Only the fields exposed
        by the page's OpenGraph tags are populated (``title``, ``description``,
        ``url``, ``image``).

        Args:
            item_id: The unique identifier of the item.
            fields: List of ``OgField`` values to extract. Defaults to all
                fields (``[OgField.TITLE, OgField.DESCRIPTION, OgField.URL,
                OgField.IMAGE]``).

        Returns:
            A VintedItem built from the page metadata. Always contains ``id``.

        Raises:
            RuntimeError: If the item page cannot be fetched (non-200 status).
        """
        data = await super().item(item_id, fields)
        return VintedItem(json_data=data)

    async def enrich(self, item: VintedItem) -> VintedItem:
        """Enrich an existing VintedItem with description from the item page.

        Fetches the ``og:description`` from the public item page and populates
        the item's ``description`` attribute. Useful for enriching items
        obtained from search results (which lack a full description).

        Args:
            item: A VintedItem to enrich (must have a valid ``id``).

        Returns:
            The same VintedItem instance with ``description`` populated.

        Raises:
            RuntimeError: If the item page cannot be fetched (non-200 status).
        """
        data = await super().item(str(item.id), [OgField.DESCRIPTION])
        if OgField.DESCRIPTION in data:
            item.description = data[OgField.DESCRIPTION]
        return item

    async def curl(
        self, endpoint: str, params: Optional[Dict] = None, *, _retries: int = 0
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
        response = await super().curl(endpoint, params, _retries=_retries)
        return VintedJsonModel(json_data=response)
