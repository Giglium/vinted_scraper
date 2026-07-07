# pylint: disable=protected-access
"""
Mock utils
"""

from typing import Final
from unittest.mock import AsyncMock, MagicMock

from src.vinted_scraper.utils import HTTP_OK, SESSION_COOKIE_NAME, get_random_user_agent

BASE_URL: Final = "https://fakeurl.com"
USER_AGENT: Final = get_random_user_agent()
COOKIE_VALUE: Final = "valid_token-123456"


def create_mock(json_data=None, status_code=HTTP_OK, text="{}"):
    """Create a mock response"""
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data or {}
    mock.headers = {}
    mock.text = text
    return mock


def create_cookie_response():
    """Helper to create mock cookie response"""
    mock = create_mock()
    mock.cookies = {SESSION_COOKIE_NAME: COOKIE_VALUE}
    return mock


def setup_mock_get(mock_client, json_data=None, status_code=HTTP_OK, text="{}"):
    """Setup mock client.get for sync tests"""
    mock_client.return_value.get.return_value = create_mock(
        json_data, status_code, text
    )


def setup_async_mock_get(mock_client, json_data=None, status_code=HTTP_OK, text="{}"):
    """Setup mock client.get for async tests"""
    mock_client.return_value.get = AsyncMock(
        return_value=create_mock(json_data, status_code, text)
    )


def setup_mock_stream(mock_client, status_code=HTTP_OK, text="", chunks=None):
    """Setup mock client.stream for sync item() tests.

    Emulates ``with client.stream(...) as response`` where ``response`` exposes
    ``status_code``, ``headers``, ``iter_text`` and ``read``.

    Args:
        mock_client: The patched httpx.Client mock.
        status_code: HTTP status code to return.
        text: Full text body (used as a single chunk if ``chunks`` is None).
        chunks: Optional list of strings to yield as separate chunks.
    """
    response = MagicMock()
    response.status_code = status_code
    response.headers = {}
    if chunks is not None:
        response.iter_text.side_effect = lambda *a, **k: iter(chunks)
    else:
        response.iter_text.side_effect = lambda *a, **k: iter([text] if text else [])
    response.read.return_value = b""

    ctx = MagicMock()
    ctx.__enter__.return_value = response
    ctx.__exit__.return_value = False
    mock_client.return_value.stream.return_value = ctx
    return response


def setup_async_mock_stream(mock_client, status_code=HTTP_OK, text="", chunks=None):
    """Setup mock client.stream for async item() tests.

    Emulates ``async with client.stream(...) as response`` where ``response``
    exposes ``status_code``, ``headers``, ``aiter_text`` and ``aread``.

    Args:
        mock_client: The patched httpx.AsyncClient mock.
        status_code: HTTP status code to return.
        text: Full text body (used as a single chunk if ``chunks`` is None).
        chunks: Optional list of strings to yield as separate chunks.
    """
    response = MagicMock()
    response.status_code = status_code
    response.headers = {}
    response.aread = AsyncMock(return_value=b"")

    chunk_list = chunks if chunks is not None else ([text] if text else [])

    async def _aiter_text(chunk_size=4096):  # pylint: disable=unused-argument
        for chunk in chunk_list:
            yield chunk

    response.aiter_text = _aiter_text

    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=response)
    ctx.__aexit__ = AsyncMock(return_value=False)
    mock_client.return_value.stream.return_value = ctx
    return response
