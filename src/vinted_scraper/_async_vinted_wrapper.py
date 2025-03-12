# jscpd:ignore-start
# pylint: disable=missing-module-docstring,duplicate-code
import asyncio
import logging
from typing import Any, Dict, Optional

import httpx

from .utils import (
    SESSION_COOKIE_NAME,
    extract_cookie_from_response,
    get_cookie_headers,
    get_curl_headers,
    get_httpx_config,
    get_random_user_agent,
    log_constructor,
    log_interaction,
    log_sleep,
    url_validator,
)

_log = logging.getLogger(__name__)


class AsyncVintedWrapper:
    """
    AsyncVintedWrapper
    """

    @classmethod
    async def create(
        cls,
        baseurl: str,
        user_agent: Optional[str] = None,
        config: Optional[Dict] = None,
    ):
        """
        Factory method that creates an instance of the AsyncVintedWrapper class.
        You should use this method if you don't want to create the instance manually by
        providing the cookie.

        :param baseurl: The base URL of the Vinted site
        :param user_agent: The user agent to use, if not provided it be chosen randomly.
        :param session_cookie: The session cookie to use, if not provided it be fetched
            automatically.
        :param config: The configuration of the HTTPX client, it will be merged with
        :return: An instance of the class
        """
        self = cls(baseurl, user_agent=user_agent, config=config)
        self._session_cookie = await self.refresh_cookie()
        return self

    def __init__(
        self,
        baseurl: str,
        session_cookie: Optional[str] = None,
        user_agent: Optional[str] = None,
        config: Optional[Dict] = None,
    ):
        # Validate
        if not url_validator(baseurl):
            _log.error("'%s' is not a valid url", baseurl)
            raise RuntimeError(f"'{baseurl}' is not a valid url, please check it!")

        # Logging
        log_constructor(
            log=_log,
            self=self,
            baseurl=baseurl,
            user_agent=user_agent,
            session_cookie=session_cookie,
            config=config,
        )

        # init
        self._client = httpx.AsyncClient(**get_httpx_config(baseurl, config))
        self._session_cookie = session_cookie
        self._base_url = baseurl
        self._user_agent = user_agent or get_random_user_agent()

    async def refresh_cookie(self, retries: int = 3) -> str:
        """
        The same of fetch_cookie but it will use the internal client to perform the API call
        """
        return await AsyncVintedWrapper.fetch_cookie(
            self._client, get_cookie_headers(self._base_url, self._user_agent), retries
        )

    @staticmethod
    async def fetch_cookie(
        client: httpx.AsyncClient, headers: Dict, retries: int = 3
    ) -> str:
        """
        Fetch the session cookie from the base URL using an async HTTP GET request.

        :param client: An instance of httpx.AsyncClient to perform the HTTP request.
        :param headers: A dictionary of HTTP headers to include in the request.
        :param retries: The number of retry attempts if the request is not successful.
        :return: The session cookie extracted from the HTTP response.
        :raises RuntimeError: If the session cookie cannot be fetched within the retry limit
                            or if the response status code is not 200.
        """

        for i in range(retries):
            log_interaction(_log, i)

            # Call base url to fetch session cookie
            response = await client.get("/", headers=headers)

            if response.status_code == 200:
                session_cookie = extract_cookie_from_response(
                    response, SESSION_COOKIE_NAME
                )
                if session_cookie:
                    return session_cookie
                _log.warning("Cannot find session cookie in response")
            else:
                # Exponential backoff before retrying
                sleep_time = 2**i
                log_sleep(_log, sleep_time)
                await asyncio.sleep(sleep_time)

        _log.error("Cannot fetch session cookie from %s", client.base_url)
        raise RuntimeError(
            f"Cannot fetch session cookie from {client.base_url}, because of "
            f"status code: {response.status_code if response is not None else 'none'}"
            "different from 200."
        )

    async def search(self, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Search for items on Vinted.

        :param params: an optional Dictionary with all the query parameters to append to the
            request. Vinted supports a search without any parameters, but to perform a search,
            you should add the `search_text` parameter. Default value: None.
        :return: A Dict that contains the JSON response with the search results.
        """
        return await self._curl("/catalog/items", params=params)

    async def item(self, item_id: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Retrieve details of a specific item on Vinted.

        :param item_id: The unique identifier of the item to retrieve.
        :param params: an optional Dictionary with all the query parameters to append to the
            request. Default value: None.
        :return: A Dict that contains the JSON response with the item's details.
        """
        return await self._curl(f"/items/{item_id}", params=params)

    async def _curl(
        self, endpoint: str, params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Send an async HTTP GET request to the specified endpoint.

        :param endpoint: The endpoint to make the request to.
        :param params: An optional dictionary with query parameters to include in the
            request. Default value: None.
        :return: A dictionary containing the parsed JSON response from the endpoint.
        :raises RuntimeError: If the HTTP response status code is not 200, indicating an error.

        The method performs the following steps:
        1. Constructs the HTTP headers, including the User-Agent and session Cookie.
        2. Sends an HTTP GET request to the specified endpoint with the given parameters.
        3. Checks if the HTTP response status code is 200 (indicating success).
        4. If the response status code is 200, it parses the JSON content of the response
            and returns it as a dictionary.
        5. If the response status code is not 200, it raises a RuntimeError.
        """
        response = await self._client.get(
            f"/api/v2{endpoint}",
            headers=get_curl_headers(
                self._base_url, self._user_agent, self._session_cookie
            ),
            params=params,
        )

        # Success
        if response.status_code == 200:
            return response.json()

        # Fetch (maybe is expired?) the session cookie again and retry the API call
        if response.status_code == 401:
            self._session_cookie = await self.refresh_cookie()
            return await self._curl(endpoint, params)
        raise RuntimeError(
            f"Cannot perform API call to endpoint {endpoint}, error code: {response.status_code}"
        )

    async def __aenter__(self):  # pragma: no cover
        """
        :return: Returns the instance of the class itself.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # pragma: no cover
        """
        Close the http client.

        :param exc_type: Not used.
        :param exc_val: Not used.
        :param exc_tb: Not used.
        """
        await self._client.aclose()


# jscpd:ignore-end
