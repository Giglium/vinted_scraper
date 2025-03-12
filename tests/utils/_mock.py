# pylint: disable=protected-access
"""
Mock utils
"""

from unittest.mock import AsyncMock

import httpx
from src.vinted_scraper.utils import SESSION_COOKIE_NAME, get_random_user_agent

# Change str to final when 3.6+ support is dropped, because final was introduced from 3.8.
BASE_URL: str = "https://fakeurl.com"
USER_AGENT: str = get_random_user_agent()
COOKIE_VALUE: str = "valid_token-123456"


def get_200_response() -> AsyncMock:
    """
    :return: a mocked 200 response using AsyncMock already configured.
    """

    request = httpx.Request("GET", BASE_URL)
    response = httpx.Response(200, request=request, headers={})

    cookies = httpx.Cookies()
    cookies.set(SESSION_COOKIE_NAME, COOKIE_VALUE, domain=BASE_URL)
    cookies.set("Path", "/", domain=BASE_URL)
    response._cookies = cookies

    return AsyncMock(return_value=response)
