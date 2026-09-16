# pylint: disable=protected-access,too-many-arguments,too-many-positional-arguments
"""
Mock utils
"""

from typing import Final, Optional
from unittest.mock import AsyncMock, MagicMock

from src.vinted_scraper.models import VintedSession
from src.vinted_scraper.utils import (
    ANON_ID_HEADER,
    HTTP_OK,
    SESSION_COOKIE_NAME,
    get_random_user_agent,
)

BASE_URL: Final = "https://fakeurl.com"
USER_AGENT: Final = get_random_user_agent()
COOKIE_VALUE: Final = "valid_token-123456"
# The landing-page HTML snippet the cookie-stream mocks stream by default. It
# carries the ``<html lang>`` tag (so the fetched session picks up a locale) and
# the CSRF marker, yielding a complete session and matching a real page.
CSRF_UUID: Final = "11111111-2222-3333-4444-555555555555"
LOCALE_VALUE: Final = "en-US"
CSRF_HTML: Final = (
    f'<html lang="{LOCALE_VALUE}"><head></head>{{"CSRF_TOKEN":"{CSRF_UUID}"}}'
)
ANON_ID_VALUE: Final = "anon-123"


def make_session(
    cookie: bool = True,
    csrf_token: Optional[str] = None,
    anon_id: Optional[str] = None,
) -> VintedSession:
    """Build a VintedSession for constructing wrappers in tests.

    Args:
        cookie: Include the standard session cookie when True.
        csrf_token: Optional CSRF token.
        anon_id: Optional anonymous id.

    Returns:
        A populated ``VintedSession``.
    """
    cookies = {SESSION_COOKIE_NAME: COOKIE_VALUE} if cookie else {}
    return VintedSession(cookies=cookies, csrf_token=csrf_token, anon_id=anon_id)


def create_mock(json_data=None, status_code=HTTP_OK, text="{}"):
    """Create a mock response"""
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data or {}
    mock.headers = {}
    mock.text = text
    return mock


def setup_two_clients(
    mock_client,
    json_data=None,
    status_code=HTTP_OK,
    text="{}",
    site_base="https://www.fakeurl.com",
    api_base="https://api.fakeurl.com",
    is_async=False,
):
    """Make the patched httpx client class return two distinct clients.

    The wrapper builds a site client and an ``api.`` client (in that order).
    This returns ``(site, api)`` so tests can assert which client a request was
    routed to. Both expose a real ``base_url`` string and a ``get``
    returning the given response.

    Args:
        mock_client: The patched httpx.Client / httpx.AsyncClient mock.
        json_data: JSON payload for the mocked ``get`` response.
        status_code: HTTP status code for the mocked ``get`` response.
        text: Text body for the mocked ``get`` response.
        site_base: ``base_url`` reported by the site client.
        api_base: ``base_url`` reported by the api client.
        is_async: When True, ``get`` is an ``AsyncMock`` (async wrapper).

    Returns:
        Tuple ``(site_client, api_client)`` mocks.
    """
    site = MagicMock()
    site.base_url = site_base
    api = MagicMock()
    api.base_url = api_base
    if is_async:
        site.get = AsyncMock(return_value=create_mock(json_data, status_code, text))
        api.get = AsyncMock(return_value=create_mock(json_data, status_code, text))
    else:
        site.get.return_value = create_mock(json_data, status_code, text)
        api.get.return_value = create_mock(json_data, status_code, text)
    mock_client.side_effect = [site, api]
    return site, api


def setup_mock_cookie_stream(
    mock_client, status_code=HTTP_OK, with_cookie=True, html=CSRF_HTML, headers=None
):
    """Setup the streamed landing-page request used to fetch cookies/tokens.

    The session cookie is now fetched via ``client.stream("GET", "/")`` (the
    same streaming strategy as ``item()``), so the streamed response must carry
    ``cookies`` and, optionally, the ``X-Anon-Id`` header and CSRF-bearing HTML.
    ``html`` defaults to a CSRF-bearing snippet so the fetched session is usable
    (cookie + CSRF); pass ``html=""`` to simulate a page without a CSRF token.

    Args:
        mock_client: The patched httpx.Client mock.
        status_code: HTTP status code for the landing-page response.
        with_cookie: When True, attach the session cookie.
        html: HTML body streamed as a single chunk (defaults to a CSRF snippet).
        headers: Response headers dict. Defaults to a set carrying ``X-Anon-Id``
            so the fetched session is complete; pass ``{}`` to omit it.
    """
    response = MagicMock()
    response.status_code = status_code
    response.headers = {ANON_ID_HEADER: ANON_ID_VALUE} if headers is None else headers
    response.cookies = {SESSION_COOKIE_NAME: COOKIE_VALUE} if with_cookie else {}
    response.iter_text.side_effect = lambda *a, **k: iter([html] if html else [])
    response.read.return_value = b""

    ctx = MagicMock()
    ctx.__enter__.return_value = response
    ctx.__exit__.return_value = False
    mock_client.return_value.stream.return_value = ctx
    return response


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


def _install_async_stream(mock_client, response, chunk_list):
    """Wire ``response`` as an async streaming context on the mock client.

    Installs ``aread``, an ``aiter_text`` yielding ``chunk_list``, and the async
    context-manager protocol so ``async with client.stream(...)`` yields it.

    Args:
        mock_client: The patched httpx.AsyncClient mock.
        response: The response mock to expose.
        chunk_list: The text chunks ``aiter_text`` should yield.

    Returns:
        The wired ``response``.
    """
    response.aread = AsyncMock(return_value=b"")

    async def _aiter_text(chunk_size=4096):  # pylint: disable=unused-argument
        for chunk in chunk_list:
            yield chunk

    response.aiter_text = _aiter_text

    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=response)
    ctx.__aexit__ = AsyncMock(return_value=False)
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
    chunk_list = chunks if chunks is not None else ([text] if text else [])
    return _install_async_stream(mock_client, response, chunk_list)


def setup_async_mock_cookie_stream(
    mock_client, status_code=HTTP_OK, with_cookie=True, html=CSRF_HTML, headers=None
):
    """Async counterpart of :func:`setup_mock_cookie_stream`.

    Emulates the streamed landing-page request used to fetch cookies/tokens via
    ``async with client.stream("GET", "/") as response``. ``html`` defaults to a
    CSRF-bearing snippet so the fetched session is usable (cookie + CSRF); pass
    ``html=""`` to simulate a page without a CSRF token.

    Args:
        mock_client: The patched httpx.AsyncClient mock.
        status_code: HTTP status code for the landing-page response.
        with_cookie: When True, attach the session cookie.
        html: HTML body streamed as a single chunk (defaults to a CSRF snippet).
        headers: Response headers dict. Defaults to a set carrying ``X-Anon-Id``
            so the fetched session is complete; pass ``{}`` to omit it.
    """
    response = MagicMock()
    response.status_code = status_code
    response.headers = {ANON_ID_HEADER: ANON_ID_VALUE} if headers is None else headers
    response.cookies = {SESSION_COOKIE_NAME: COOKIE_VALUE} if with_cookie else {}
    return _install_async_stream(mock_client, response, [html] if html else [])
