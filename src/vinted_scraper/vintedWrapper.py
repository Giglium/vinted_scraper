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
        verify_ssl: bool = True,
    ):
        """
        Initialize the Vinted API wrapper
        
        :param baseurl: (required) Base Vinted site URL to use for requests
        :param agent: (optional) Custom user agent string
        :param session_cookie: (optional) Existing session cookie
        :param proxies: (optional) Proxy configuration for requests
        :param verify_ssl: (optional) Verify SSL certificates. Recommended to keep as True for security.
        """
        self.baseurl = baseurl[:-1] if baseurl.endswith("/") else baseurl
        self.verify_ssl = verify_ssl

        # Validate base URL format
        if not re.match(
            re.compile(r"^(https?://)?(www\.)?[\w.-]+\.\w{2,}$"), self.baseurl
        ):
            raise RuntimeError(f"Invalid base URL: {self.baseurl}")

        self.user_agent = agent or get_random_user_agent()
        self.proxies = proxies
        self.session_cookie = session_cookie or self._fetch_cookie()

    def _fetch_cookie(self, proxies: Optional[Dict] = None, retries: int = 3) -> str:
        """
        Fetch session cookie from Vinted website
        
        :param proxies: Optional proxy configuration (overrides instance proxies)
        :param retries: Number of retry attempts
        :return: Session cookie string
        """
        for attempt in range(retries):
            try:
                response = requests.get(
                    self.baseurl,
                    headers=self._extended_headers(),
                    proxies=proxies or self.proxies,
                    verify=self.verify_ssl,
                )
                
                if response.status_code == 200:
                    if cookie := response.headers.get("Set-Cookie", ""):
                        if "access_token_web=" in cookie:
                            return cookie.split("access_token_web=")[1].split(";")[0]
                
                # Exponential backoff before retrying
                time.sleep(2 ** attempt)
                
            except requests.exceptions.RequestException:
                time.sleep(2 ** attempt)

        raise RuntimeError(
            f"Failed to fetch session cookie after {retries} attempts. "
            f"Last status code: {getattr(response, 'status_code', 'No response')}"
        )

    def search(self, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Search for items on Vinted
        
        :param params: Search parameters dictionary
        :return: Search results as JSON dictionary
        """
        return self._curl("/catalog/items", params=params)

    def item(self, item_id: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Get detailed information about a specific item
        
        :param item_id: Vinted item ID
        :param params: Optional additional parameters
        :return: Item details as JSON dictionary
        """
        return self._curl(f"/items/{item_id}", params=params)

    def _curl(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute API request with error handling and retry logic
        
        :param endpoint: API endpoint to call
        :param params: Query parameters
        :return: Response JSON as dictionary
        """
        headers = self._extended_headers(include_cookie=True)
        max_retries = 3
        retry_delay = 1  # seconds

        for attempt in range(max_retries):
            try:
                response = requests.get(
                    f"{self.baseurl}/api/v2{endpoint}",
                    params=params,
                    headers=headers,
                    proxies=self.proxies,
                    verify=self.verify_ssl,
                )

                if response.status_code == 200:
                    return json.loads(response.content)
                elif response.status_code == 401:
                    # Refresh expired session cookie and retry
                    self.session_cookie = self._fetch_cookie()
                    return self._curl(endpoint, params)
                else:
                    raise RuntimeError(
                        f"API request failed to {endpoint} with status code {response.status_code}"
                    )

            except requests.exceptions.SSLError as e:
                time.sleep(retry_delay)
                if attempt == max_retries - 1:
                    raise RuntimeError(f"SSL verification failed: {str(e)}")

            except requests.exceptions.RequestException as e:
                time.sleep(retry_delay)
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Request failed after {max_retries} attempts: {str(e)}")

        return {}

    def _extended_headers(self, include_cookie: bool = False) -> Dict[str, str]:
        """
        Generate browser-like headers to avoid detection
        
        :param include_cookie: Whether to include session cookie
        :return: Headers dictionary
        """
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "DNT": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Origin": self.baseurl,
            "Referer": self.baseurl,
        }
        if include_cookie and self.session_cookie:
            headers["Cookie"] = f"access_token_web={self.session_cookie}"
        return headers
