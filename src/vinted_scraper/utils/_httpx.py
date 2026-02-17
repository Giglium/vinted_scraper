"""
All the functions and the utility that required httpx will be placed here
"""

import logging
from logging import Logger
from typing import Dict, Optional

import httpx


def get_httpx_config(baseurl: str, config: Optional[Dict] = None):
    """
    Returns a config dictionary to be used with httpx.Client.
    The dictionary contains the baseurl, a timeout of 10 seconds and
    follow_redirects set to True.
    If a config dictionary is passed, it will be merged with the defaults. You can also
    override the default configuration!

    :param baseurl: The baseurl to be used by httpx.Client call
    :param config: An optional dictionary to be merged with the defaults configuration.
    :return: A dictionary containing the config for a httpx.Client
    """
    default_config = {
        "base_url": baseurl,
        "timeout": httpx.Timeout(10.0),
        "follow_redirects": True,
    }

    return {**default_config, **(config or {})}


def extract_cookie_from_response(
    response: httpx.Response, cookie_names: list[str]
) -> Dict[str, str]:
    """
    Extracts the required cookies from the response object.

    :param response: The httpx response object.
    :param cookie_names: The list of cookie names to extract.
    :return: A dictionary with cookie names as keys and values.
    """
    return {
        name: response.cookies.get(name)
        for name in cookie_names
        if response.cookies.get(name)
    }


def log_response(log: Logger, response: httpx.Response) -> None:
    """
    Log a message indicating the status code of the response.

    :param log: the logger object to use for the log message
    :param response: the response object
    :return: None
    """
    if log.isEnabledFor(logging.DEBUG):
        log.debug(
            f"Url is {response.url}"  # print url
            f"Status code: {response.status_code}"  # print status code
            f"Headers: {response.headers}"  # print headers
            f"Content: {response.text}"  # Print content
        )
