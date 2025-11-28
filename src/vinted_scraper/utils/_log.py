# pylint: disable=line-too-long, too-many-arguments
"""
Most of the log function will placed here.
If a log function required a specific package it will be putted in that package utils.
Es. httpx logger will be put in the httpx utils.
"""

import logging
from logging import Logger
from typing import Dict, Optional


def log_constructor(
    *,
    log: Logger,
    self: object,
    baseurl: str,
    user_agent: str,
    session_cookie: str,
    config: Dict,
) -> None:
    """
    Construct a log message for the constructor of an object.

    :param log: the logger object to use for the log message
    :param self: the object being created
    :param baseurl: the baseurl to log
    :param user_agent: the user_agent to log
    :param session_cookie: the session cookie to log
    :param config: the configuration to log
    :return: None
    """
    if log.isEnabledFor(logging.DEBUG):
        log.debug(
            f"Create object {self.__class__.__name__} with baseurl {baseurl}, agent {user_agent}, session_cookie {session_cookie} and config {config}"  # noqa E501
        )


def log_interaction(log: Logger, i: int) -> None:
    """
    Construct a log message for log that print the current interaction

    :param log: the logger object to use for the log message
    :param i: the number of the interaction
    :return: None
    """
    if log.isEnabledFor(logging.DEBUG):
        log.debug(f"Interaction {i}")


def log_sleep(log: Logger, time: int) -> None:
    """
    Log a message indicating the duration of sleep.

    :param log: the logger object to use for the log message
    :param time: the duration of sleep in seconds
    :return: None
    """

    if log.isEnabledFor(logging.DEBUG):
        log.debug(f"Sleeping for {time} seconds")


def log_refresh_cookie(log: Logger) -> None:
    """
    Log a message indicating the cookie refresh.

    :param log: the logger object to use for the log message
    :return: None
    """
    if log.isEnabledFor(logging.DEBUG):
        log.debug("refreshing the cookie")


def log_search(log: Logger, params: Optional[Dict]) -> None:
    """
    Log a message indicating a search API call.

    :param log: the logger object to use for the log message
    :param params: the search parameters (can be None)
    :return: None
    """
    if log.isEnabledFor(logging.DEBUG):
        log.debug(f"Searching with params {params}")


def log_item(log: Logger, item_id: str, params: Optional[Dict]) -> None:
    """
    Log a message indicating an item retrieval API call.

    :param log: the logger object to use for the log message
    :param item_id: the item ID to retrieve
    :param params: the query parameters (can be None)
    :return: None
    """
    if log.isEnabledFor(logging.DEBUG):
        log.debug(f"Fetching item {item_id} with params {params}")


def log_curl(log: Logger, endpoint: str, params: Optional[Dict]) -> None:
    """
    Log a message indicating an internal HTTP request.

    :param log: the logger object to use for the log message
    :param endpoint: the endpoint being called
    :param params: the query parameters (can be None)
    :return: None
    """
    if log.isEnabledFor(logging.DEBUG):
        log.debug(f"Calling endpoint {endpoint} with params {params}")
