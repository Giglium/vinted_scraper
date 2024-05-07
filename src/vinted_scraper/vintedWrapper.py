import json
import re
import time
from typing import Any, Dict, Optional

import requests

from .utils import get_random_user_agent


class VintedWrapper:
    def __init__(
        self,
        baseurl: str,
        agent: Optional[str] = None,
        session_cookie: Optional[str] = None,
        proxies: Optional[Dict] = None,
    ):
        """
        :param baseurl: (required) Base Vinted site url to use in the requests
        :param agent: (optional) User agent to use on the requests
        :param session_cookie: (optional) Vinted session cookie
        :param proxies: (optional) Dictionary mapping protocol or protocol and
        hostname to the URL of the proxy. For more info see:
        https://requests.readthedocs.io/en/latest/user/advanced/#proxies
        """

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
        self.proxies = proxies

    def _fetch_cookie(self, retries: int = 3) -> str:
        """
        Send an HTTP GET request to the self.base_url to fetch the session cookie with retries.

        :param retries: Number of retries for the HTTP request.
        :return: The session cookie extracted from the HTTP response headers.
        :raises RuntimeError: If the session cookie cannot be fetched or doesn't match the expected format.
        """
        response = None
        for _ in range(retries):
            response = requests.get(
                self.baseurl, headers={"User-Agent": self.user_agent}
            )
            if response.status_code == 200:
                session_cookie = response.headers.get("Set-Cookie")
                if session_cookie and "_vinted_fr_session=" in session_cookie:
                    return session_cookie.split("_vinted_fr_session=")[1].split(";")[0]
            else:
                # Exponential backoff before retrying
                time.sleep(2**_)

        raise RuntimeError(
            f"Cannot fetch session cookie from {self.baseurl}, because of "
            f"status code: {response.status_code if response is not None else 'none'} different from 200."
        )

    def search(self, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Search for items on Vinted.

        :param params: an optional Dictionary with all the query parameters to append to the request.
            Vinted supports a search without any parameters, but to perform a search,
            you should add the `search_text` parameter.
            Default value: None.
        :return: A Dict that contains the JSON response with the search results.
        """
        return self._curl("/catalog/items", params=params)

    def item(self, item_id: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Retrieve details of a specific item on Vinted.

        :param item_id: The unique identifier of the item to retrieve.
        :param params: an optional Dictionary with all the query parameters to append to the request.
            Default value: None.
        :return: A Dict that contains the JSON response with the item's details.
        """
        return self._curl(f"/items/{item_id}", params=params)

    def _curl(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Send an HTTP GET request to the specified endpoint.

        :param endpoint: The endpoint to make the request to.
        :param params: An optional dictionary with query parameters to include in the request.
                       Default value: None.
        :return: A dictionary containing the parsed JSON response from the endpoint.
        :raises RuntimeError: If the HTTP response status code is not 200, indicating an error.

        The method performs the following steps:
        1. Constructs the HTTP headers, including the User-Agent and session Cookie.
        2. Sends an HTTP GET request to the specified endpoint with the given parameters.
        3. Checks if the HTTP response status code is 200 (indicating success).
        4. If the response status code is 200, it parses the JSON content of the response
            and returns it as a dictionary.
        5. If the response status code is not 200, it raises a RuntimeError with an error message.
        """
        headers = {
            "User-Agent": self.user_agent,
            "Cookie": f"_vinted_fr_session={self.session_cookie}",
        }
        response = requests.get(
            f"{self.baseurl}/api/v2{endpoint}",
            params=params,
            headers=headers,
            proxies=self.proxies,
        )

        if 200 == response.status_code:
            return json.loads(response.content)
        elif 401 == response.status_code:
            # Fetch (maybe is expired?) the session cookie again and retry the API call
            self.session_cookie = self._fetch_cookie()
            return self._curl(endpoint, params)
        else:
            raise RuntimeError(
                f"Cannot perform API call to endpoint {endpoint}, error code: {response.status_code}"
            )
