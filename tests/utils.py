import json
import os
from typing import Dict
from unittest.mock import MagicMock, patch

import requests

# isort: split
from src.vinted_scraper import VintedScraper, VintedWrapper


def get_200_response() -> MagicMock:
    """
    :return: a mocked 200 response using MagicMock already configured
    """
    response_200 = MagicMock(spec=requests.Response)
    response_200.status_code = 200
    response_200.headers = {"Set-Cookie": "secure, _vinted_fr_session=test"}
    return response_200


def get_wrapper(url: str) -> VintedWrapper:
    """
    :param url: a valid https url like: "https://fakeurl.com"
    :return: a VintedWrapper instance for testing
    """
    with patch("requests.get", return_value=get_200_response()):
        return VintedWrapper(url)


def get_scraper(url: str) -> VintedWrapper:
    """
    :param url: a valid https url like: "https://fakeurl.com"
    :return: a VintedScraper instance for testing
    """
    with patch("requests.get", return_value=get_200_response()):
        return VintedScraper(url)


def _read_data_from_file(filename: str) -> Dict:
    """
    Read the test item from the samples' folder.
    """
    root_dir = os.getcwd()
    # Test are supposed to run from the makefile on the repository root.
    # `FROM_ROOT` is an env variable that I inject to understand if I have to apply this fix or not.
    if not os.getenv("FROM_ROOT", False):
        # If you run it from the `/test` folder I need to add `/../` to the path.
        root_dir = os.path.join(root_dir, "..")
    with open(
        os.path.join(root_dir, "tests", "samples", f"{filename}.json"), "r"
    ) as file:
        return json.load(file)
