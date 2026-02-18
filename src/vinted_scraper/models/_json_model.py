# pylint: disable=missing-module-docstring,missing-class-docstring
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class VintedJsonModel:
    """Base class for all Vinted models with json_data support."""

    json_data: Optional[Dict] = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        if self.json_data is not None:
            self.__dict__.update(self.json_data)

    def __getitem__(self, key: str) -> Any:
        """Allow subscript access to json_data."""
        if self.json_data is None:
            raise KeyError(key)
        return self.json_data[key]
