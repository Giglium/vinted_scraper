import json
import re
from typing import Any, Dict, Optional

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
        """
        Send an HTTP GET request to the self.base_url to fetch the session cookie.

        :return: The session cookie extracted from the HTTP response headers.
        :raises RuntimeError: If the session cookie cannot be fetched or doesn't match the expected format.

        The method performs the following steps:
        1. Sends an HTTP GET request to the base URL using the provided User-Agent header.
        2. Retrieves the "Set-Cookie" header from the HTTP response.
        3. Checks if the "Set-Cookie" header contains the expected session cookie format.
        4. If a matching session cookie is found, it extracts and returns it.
        5. If the session cookie cannot be fetched or doesn't match the expected format, it raises a RuntimeError.
        """
        response = requests.get(self.baseurl, headers={"User-Agent": self.user_agent})

        session_cookie = response.headers.get("Set-Cookie")
        if session_cookie and "secure, _vinted_fr_session=" in session_cookie:
            return session_cookie.split("secure, _vinted_fr_session=")[1].split(";")[0]

        raise RuntimeError(f"Cannot fetch session cookie from {self.baseurl}")

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
            f"{self.baseurl}/api/v2{endpoint}", params=params, headers=headers
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
