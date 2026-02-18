"""Base JSON model for Vinted data structures.

This module defines the VintedJsonModel base class used by all Vinted models.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class VintedJsonModel:
    """Base class for all Vinted models with JSON data support.

    Provides automatic attribute population from JSON data and subscript access.
    All Vinted model classes inherit from this base class.

    Attributes:
        json_data: Raw JSON dictionary from API response.
    """

    json_data: Optional[Dict] = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Populate model attributes from json_data after initialization."""
        if self.json_data is not None:
            self.__dict__.update(self.json_data)

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style subscript access to json_data.

        Args:
            key: The key to access in json_data.

        Returns:
            The value associated with the key.

        Raises:
            KeyError: If json_data is None or key doesn't exist.
        """
        if self.json_data is None:
            raise KeyError(key)
        return self.json_data[key]
