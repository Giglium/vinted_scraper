# jscpd:ignore-start
# pylint: disable=missing-module-docstring,duplicate-code
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx

from .utils import (
    API_CATALOG_ITEMS,
    API_ITEMS,
    DEFAULT_RETRIES,
    HTTP_OK,
    HTTP_UNAUTHORIZED,
    RETRY_BASE_SLEEP,
    SESSION_COOKIE_NAME,
    extract_cookie_from_response,
    get_cookie_headers,
    get_curl_headers,
    get_httpx_config,
    get_random_user_agent,
    log_constructor,
    log_cookie_fetch_failed,
    log_cookie_fetched,
    log_cookie_retry,
    log_curl_request,
    log_curl_response,
    log_interaction,
    log_item,
    log_refresh_cookie,
    log_search,
    log_sleep,
    url_validator,
)

_log = logging.getLogger(__name__)


@dataclass
class AsyncVintedWrapper:
    """
    AsyncVintedWrapper
    """

    baseurl: str
    session_cookie: Optional[Dict[str, str]] = None
    user_agent: Optional[str] = None
    config: Optional[Dict] = None
    cookie_names: Optional[List[str]] = None
    _client: httpx.AsyncClient = field(init=False, repr=False)

    @classmethod
    async def create(
        cls,
        baseurl: str,
        user_agent: Optional[str] = None,
        config: Optional[Dict] = None,
        cookie_names: Optional[List[str]] = None,
    ):
        """
        Factory method that creates an instance of the AsyncVintedWrapper class.

        :param baseurl: The base URL of the Vinted site
        :param user_agent: The user agent to use, if not provided it be chosen randomly.
        :param config: The configuration of the HTTPX client, it will be merged with defaults.
        :param cookie_names: List of cookie names to extract. Defaults to [SESSION_COOKIE_NAME].
        :return: An instance of the class
        """
        _log.debug("Creating the async wrapper using the factory method")
        self = cls(
            baseurl, user_agent=user_agent, config=config, cookie_names=cookie_names
        )
        self.session_cookie = await self.refresh_cookie()
        return self

    def __post_init__(self) -> None:
        """
        Initialize AsyncVintedWrapper after dataclass initialization.
        """
        if not url_validator(self.baseurl):
            _log.error("'%s' is not a valid url", self.baseurl)
            raise RuntimeError(f"'{self.baseurl}' is not a valid url, please check it!")

        log_constructor(
            log=_log,
            self=self,
            baseurl=self.baseurl,
            user_agent=self.user_agent,
            session_cookie=self.session_cookie,
            config=self.config,
        )

        if self.user_agent is None:
            self.user_agent = get_random_user_agent()
        if self.cookie_names is None:
            self.cookie_names = [SESSION_COOKIE_NAME]
        self._client = httpx.AsyncClient(**get_httpx_config(self.baseurl, self.config))

    async def refresh_cookie(self, retries: int = DEFAULT_RETRIES) -> Dict[str, str]:
        """
        Refresh session cookies using the internal client.

        :param retries: Number of retry attempts. Defaults to 3.
        :return: Dictionary of session cookies.
        """
        log_refresh_cookie(_log)
        return await AsyncVintedWrapper.fetch_cookie(
            self._client,
            get_cookie_headers(self.baseurl, self.user_agent),
            self.cookie_names,
            retries,
        )

    @staticmethod
    async def fetch_cookie(
        client: httpx.AsyncClient,
        headers: Dict,
        cookie_names: List[str],
        retries: int = DEFAULT_RETRIES,
    ) -> Dict[str, str]:
        """
        Fetch session cookies from the base URL using an async HTTP GET request.

        :param client: An instance of httpx.AsyncClient.
        :param headers: A dictionary of HTTP headers.
        :param cookie_names: List of cookie names to extract.
        :param retries: Number of retry attempts. Defaults to 3.
        :return: Dictionary of session cookies.
        :raises RuntimeError: If cookies cannot be fetched.
        """
        response = None

        for i in range(retries):
            log_interaction(_log, i, retries)
            response = await client.get("/", headers=headers)

            if response.status_code == HTTP_OK:
                cookies = extract_cookie_from_response(response, cookie_names)
                if cookies:
                    log_cookie_fetched(_log, str(cookies))
                    return cookies
                _log.warning("Cannot find session cookie in response")
            else:
                log_cookie_fetch_failed(_log, response.status_code, i, retries)
                sleep_time = RETRY_BASE_SLEEP**i
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
        log_search(_log, params)
        return await self.curl(API_CATALOG_ITEMS, params=params)

    async def item(self, item_id: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Retrieve details of a specific item on Vinted.

        :param item_id: The unique identifier of the item to retrieve.
        :param params: an optional Dictionary with all the query parameters to append to the
            request. Default value: None.
        :return: A Dict that contains the JSON response with the item's details.
        """
        log_item(_log, item_id, params)
        return await self.curl(f"{API_ITEMS}/{item_id}", params=params)

    async def curl(
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
        headers = get_curl_headers(self.baseurl, self.user_agent, self.session_cookie)

        log_curl_request(_log, self.baseurl, endpoint, headers, params)

        response = await self._client.get(
            endpoint,
            headers=get_curl_headers(
                self.baseurl, self.user_agent, self.session_cookie
            ),
            params=params,
        )

        log_curl_response(
            _log, endpoint, response.status_code, response.headers, response.text
        )

        # Success
        if response.status_code == HTTP_OK:
            try:
                return response.json()
            except ValueError as e:
                _log.error("Failed to parse JSON response from %s: %s", endpoint, e)
                raise RuntimeError(f"Invalid JSON response from {endpoint}: {e}") from e

        # Fetch (maybe is expired?) the session cookie again and retry the API call
        if response.status_code == HTTP_UNAUTHORIZED:
            log_cookie_retry(_log, response.status_code)
            self.session_cookie = await self.refresh_cookie()
            return await self.curl(endpoint, params)
        raise RuntimeError(
            f"Cannot perform API call to endpoint {endpoint}, error code: {response.status_code}"
        )

    async def __aenter__(self) -> "AsyncVintedWrapper":  # pragma: no cover
        """
        :return: Returns the instance of the class itself.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # pragma: no cover
        """
        Close the http client.

        :param exc_type: Not used.
        :param exc_val: Not used.
        :param exc_tb: Not used.
        """
        await self._client.aclose()


# jscpd:ignore-end
