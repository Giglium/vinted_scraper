from dataclasses import dataclass
from typing import Optional


@dataclass
class VintedPaymentMethod:
    id: Optional[int] = None
    code: Optional[str] = None
    requires_credit_card: Optional[bool] = None
    event_tracking_code: Optional[str] = None
    icon: Optional[str] = None
    enabled: Optional[bool] = None
    translated_name: Optional[str] = None
    note: Optional[str] = None
    method_change_possible: Optional[bool] = None

    def __init__(self, json_data=None):
        if json_data is not None:
            self.__dict__.update(json_data)
