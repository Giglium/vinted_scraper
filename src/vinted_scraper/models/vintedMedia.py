from dataclasses import dataclass
from typing import Optional


@dataclass
class VintedMedia:
    type: Optional[str] = None
    url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    original_size: Optional[str] = None

    def __init__(self, json_data=None):
        if json_data is not None:
            self.__dict__.update(json_data)
