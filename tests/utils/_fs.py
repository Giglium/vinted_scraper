"""
Filesystem utils
"""

import json
import os
from typing import Dict


def read_data_from_file(filename: str) -> Dict:
    """
    Read the json file from the samples' folder and it return it as Dict
    """
    with open(
        os.path.join(os.path.dirname(__file__), "..", "samples", f"{filename}.json"),
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)
