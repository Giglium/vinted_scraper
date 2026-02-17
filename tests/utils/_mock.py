# pylint: disable=protected-access
"""
Mock utils
"""

from unittest.mock import AsyncMock, MagicMock

from src.vinted_scraper.utils import SESSION_COOKIE_NAME, get_random_user_agent

# Change str to final when 3.6+ support is dropped, because final was introduced from 3.8.
BASE_URL: str = "https://fakeurl.com"
USER_AGENT: str = get_random_user_agent()
COOKIE_VALUE: str = "valid_token-123456"


def create_mock(json_data=None, status_code=200, text="{}"):
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


def setup_mock_get(mock_client, json_data=None, status_code=200, text="{}"):
    """Setup mock client.get for sync tests"""
    mock_client.return_value.get.return_value = create_mock(
        json_data, status_code, text
    )


def setup_async_mock_get(mock_client, json_data=None, status_code=200, text="{}"):
    """Setup mock client.get for async tests"""
    mock_client.return_value.get = AsyncMock(
        return_value=create_mock(json_data, status_code, text)
    )
