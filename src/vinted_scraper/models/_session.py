"""Vinted session identity model."""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class VintedSession:
    """The identity needed to authenticate Vinted API calls.

    Bundles the values scraped from (or supplied for) the landing page: the
    session ``cookies``, the ``anon_id`` returned as a response header, and the
    ``csrf_token``. They are created, stored, and sent together, so they travel
    as a single object.

    The ``csrf_token`` is a supported field (it is sent when set and can be
    supplied by a caller), but it is **not** auto-fetched from the landing page:
    the API currently accepts calls without it. See
    ``utils/_session.py::build_session`` for how to re-enable that.

    Attributes:
        cookies: Session cookies keyed by name.
        csrf_token: CSRF token for the API, if available. Not auto-fetched.
        anon_id: Anonymous id for the API, if available.
        locale: Market locale tag (e.g. ``"cs-CZ"``)
    """

    cookies: Dict[str, str] = field(default_factory=dict)
    csrf_token: Optional[str] = None
    anon_id: Optional[str] = None
    locale: Optional[str] = None

    def is_empty(self) -> bool:
        """Return whether no identity part is set.

        Returns:
            ``True`` when there are no cookies and neither token is set.
        """
        return not self.cookies and self.csrf_token is None and self.anon_id is None

    def is_usable(self) -> bool:
        """Return whether the session carries enough to authenticate a call.

        A session is usable once the landing page has handed over the parts the
        API actually checks: the session cookies and the anonymous id. The CSRF
        token is sent when present but is not required to make the call (and is
        not auto-fetched), so it is not part of this check.

        Returns:
            ``True`` when both cookies and an anonymous id are set.
        """
        return bool(self.cookies) and self.anon_id is not None
