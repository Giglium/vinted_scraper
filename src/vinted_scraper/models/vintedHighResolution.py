from dataclasses import dataclass
from typing import Optional


@dataclass
class VintedHighResolution:
    id: Optional[str] = None
    timestamp: Optional[int] = None
    orientation: Optional[str] = None

    def __init__(self, json_data=None):
        if json_data is not None:
            self.__dict__.update(json_data)
