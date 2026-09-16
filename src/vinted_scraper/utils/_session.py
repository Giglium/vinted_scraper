"""Session-fetch helpers: build a ``VintedSession`` and handle fetch failures.

These are the stateless pieces of the landing-page session fetch, shared by the
sync and async wrappers. They live here (rather than on the wrapper) because
they never touch instance state: they only turn a landing-page response into a
``VintedSession`` and decide what to do when the fetch does not succeed.
"""

import logging
from typing import List, NoReturn

from ..models import VintedSession
from ._constants import RETRY_BASE_SLEEP
from ._httpx import extract_anon_id_from_response, extract_cookie_from_response
from ._log import log_cookie_fetch_failed, log_session_fetched, log_sleep

# NOTE: the CSRF token is intentionally not auto-fetched right now (the API
# accepts calls without it, see ``build_session``). To re-enable, restore the
# ``extract_csrf_token`` import from ``._html`` and the commented lines below.

__all__ = [
    "build_session",
    "handle_session_failure",
    "raise_session_error",
]

_log = logging.getLogger(__name__)


def build_session(  # pylint: disable=unused-argument
    response, html: str, cookie_names: List[str]
) -> VintedSession:
    """Build a ``VintedSession`` from a (2xx) landing-page response.

    Bundles the cookies (from the response) and the anonymous id (from the
    headers). A warning is logged for any part the landing page did not hand
    over, since that points at a real fetch problem (unlike a caller-supplied
    partial session, which is allowed to be incomplete, and so the
    ``VintedSession`` model stays silent on construction).

    The CSRF token is currently **not** auto-fetched: the API accepts calls
    without it, so parsing it out of ``html`` is skipped. ``html`` (the streamed
    head fragment) is still accepted so this can be re-enabled without touching
    the call sites — set ``csrf_token=extract_csrf_token(html)`` below.

    Args:
        response: The landing page response.
        html: The HTML head fragment read from the landing page request
            (currently unused; kept for re-enabling CSRF extraction).
        cookie_names: Cookie names to extract.

    Returns:
        The built ``VintedSession``.
    """
    session = VintedSession(
        cookies=extract_cookie_from_response(response, cookie_names),
        # csrf_token=extract_csrf_token(html),  # not currently required by the API
        anon_id=extract_anon_id_from_response(response),
    )
    if not session.cookies:
        _log.warning("Session is missing 'cookies'")
    if session.anon_id is None:
        _log.warning("Session is missing 'anon_id'")
    log_session_fetched(_log, session)
    return session


def handle_session_failure(response, attempt: int, retries: int) -> float:
    """Log a failed session attempt and return the sleep duration.

    Args:
        response: httpx response object.
        attempt: Current attempt number (0-indexed).
        retries: Total retry count.

    Returns:
        Seconds to sleep before the next attempt.
    """
    log_cookie_fetch_failed(_log, response.status_code, attempt, retries)
    sleep_time = RETRY_BASE_SLEEP**attempt
    log_sleep(_log, sleep_time)
    return sleep_time


def raise_session_error(base_url, response) -> NoReturn:
    """Raise after all session-fetch retries are exhausted.

    Args:
        base_url: The base URL that was targeted.
        response: Last httpx response (may be ``None``).

    Raises:
        RuntimeError: Always.
    """
    _log.error("Cannot fetch session from %s", base_url)
    raise RuntimeError(
        f"Cannot fetch session from {base_url}, because of "
        f"status code: {response.status_code if response is not None else 'none'} "
        "different from 200."
    )
