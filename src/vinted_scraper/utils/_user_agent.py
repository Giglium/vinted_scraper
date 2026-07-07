"""Random user agent selection."""

import json
import os
import random
import sys
from functools import lru_cache
from typing import Dict, List

if sys.version_info >= (3, 9):
    from importlib.resources import files

__all__ = [
    "get_random_user_agent",
]


@lru_cache(maxsize=1)
def _load_agents() -> List[Dict]:
    """Loads user agents from JSON file (cached).

    Uses importlib.resources for reliable access to package data,
    which works correctly even when the package is installed from
    a wheel, zip, or frozen environment.

    Returns:
        List of user agent dictionaries.
    """
    if sys.version_info >= (3, 9):
        data = files(__package__).joinpath("agents.json").read_text(encoding="utf-8")
    else:
        # Fallback for Python 3.8
        with open(
            os.path.join(os.path.dirname(__file__), "agents.json"),
            "r",
            encoding="utf-8",
        ) as file:
            data = file.read()
    return json.loads(data)


def get_random_user_agent() -> str:
    """Returns a random user agent string.

    Selects from a predefined list of browser user agents, weighted by
    real-world usage percentage to better mimic genuine traffic patterns.

    Returns:
        Random user agent string.
    """
    agents = _load_agents()
    return random.choices(agents, weights=[a["pct"] for a in agents], k=1)[0]["ua"]
