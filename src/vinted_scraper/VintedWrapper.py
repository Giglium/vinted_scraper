import json
import re
from typing import Dict, Optional

import requests

from .utils import get_random_user_agent


class VintedWrapper:
    def __init__(self, baseurl: str, agent=None, session_cookie=None):
        self.baseurl = baseurl[:-1] if baseurl.endswith("/") else baseurl

        # Check if the URL is valid
        if not re.match(
            re.compile(r"^(https?://)?(www\.)?[\w.-]+\.\w{2,}$"), self.baseurl
        ):
            raise RuntimeError(f"{self.baseurl} is not a valid url, please check it!")

        self.user_agent = agent if agent is not None else get_random_user_agent()
        self.session_cookie = (
            session_cookie if session_cookie is not None else self._fetch_cookie()
        )

    def _fetch_cookie(self) -> str:
        response = requests.get(self.baseurl, headers={"User-Agent": self.user_agent})

        session_cookie = response.headers.get("Set-Cookie")
        if session_cookie and "secure, _vinted_fr_session=" in session_cookie:
            return session_cookie.split("secure, _vinted_fr_session=")[1].split(";")[0]

        raise RuntimeError(f"Cannot fetch session cookie from {self.baseurl}")

    def search(self, params: Optional[Dict] = None) -> Dict:
        """
        :param params: an optional Dictionary with all the query parameters to append at the request.
            Vinted support a search without any param but to perform a search you should add the `search_text` params.
            Default value: None.
        """
        return self._curl("/catalog/items", params=params)

    def _curl(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        :param params: an optional Dictionary with all the query parameters to append at the request.
            Default value: None.
        """
        headers = {
            "User-Agent": self.user_agent,
            "Cookie": f"_vinted_fr_session={self.session_cookie}",
        }
        response = requests.get(
            f"{self.baseurl}/api/v2/{endpoint}", params=params, headers=headers
        )

        if 200 == response.status_code:
            return json.loads(response.content)
        # TODO: Implement retry
        # elif 401 == response.status_code:
        #     # Fetch (maybe is expired?) the session cookie again and retry the API call
        #     self.session_cookie = self._fetch_cookie()
        #     return self._curl(endpoint, params)
        else:
            raise RuntimeError(
                f"Cannot perform API call to endpoint {endpoint}, error code: {response.status_code}"
            )
