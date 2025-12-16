# jscpd:ignore-start
# pylint: disable=protected-access
"""
Test the Async Vinted Wrapper class
"""
import logging
import sys
import unittest
from unittest.mock import patch

from src.vinted_scraper import AsyncVintedWrapper
from tests.utils._mock import BASE_URL, COOKIE_VALUE, USER_AGENT, get_200_response

# Python 3.7 compatibility: IsolatedAsyncioTestCase was introduced in Python 3.8
if sys.version_info >= (3, 8):
    from unittest import IsolatedAsyncioTestCase as BaseTestCase
else:
    # For Python 3.7, we need to create a simple compatibility shim
    import asyncio
    
    class BaseTestCase(unittest.TestCase):
        """Compatibility shim for IsolatedAsyncioTestCase in Python < 3.8"""
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._asyncio_loop = None
        
        def asyncSetUp(self):
            """Override in subclass for async setup"""
            pass
        
        def asyncTearDown(self):
            """Override in subclass for async teardown"""
            pass
        
        def setUp(self):
            """Set up async event loop"""
            self._asyncio_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._asyncio_loop)
            self._asyncio_loop.run_until_complete(self.asyncSetUp())
        
        def tearDown(self):
            """Tear down async event loop"""
            self._asyncio_loop.run_until_complete(self.asyncTearDown())
            self._asyncio_loop.close()
            asyncio.set_event_loop(None)
        
        def __getattribute__(self, name):
            """Wrap async test methods to run in event loop"""
            attr = object.__getattribute__(self, name)
            if name.startswith('test_') and asyncio.iscoroutinefunction(attr):
                def wrapper(*args, **kwargs):
                    return self._asyncio_loop.run_until_complete(attr(*args, **kwargs))
                return wrapper
            return attr


class TestAsyncVintedWrapper(BaseTestCase):
    """
    Test the Async Vinted Wrapper class with a Mock for the API call
    """

    def test_constructor(self):
        """
        Ensure that the constructor:
         - correctly sets the session cookie and user agent
         - raises an error if the base URL is not valid
         - logs the correct error message
        """
        wrapper = AsyncVintedWrapper(BASE_URL, COOKIE_VALUE, USER_AGENT)
        self.assertEqual(wrapper._base_url, BASE_URL)
        self.assertEqual(wrapper._session_cookie, COOKIE_VALUE)
        self.assertEqual(wrapper._user_agent, USER_AGENT)

        with self.assertLogs(level=logging.INFO) as cm:
            wrong_url = "wrong url"
            with self.assertRaises(RuntimeError):
                AsyncVintedWrapper(wrong_url)

            self.assertEqual(
                cm.output,
                [
                    f"ERROR:{AsyncVintedWrapper.__module__}:'{wrong_url}' is not a valid url"
                ],
            )

    @patch("src.vinted_scraper._async_vinted_wrapper.httpx.AsyncClient")
    async def test_factory_create(self, mock_client):
        """
        Test the factory `create` method of `AsyncVintedWrapper`.

        This method ensures that the factory method `create`:
        - Successfully creates an instance of `AsyncVintedWrapper`.
        - Properly sets the session cookie if not provided.
        - Makes a single GET request to fetch the session cookie.
        - Correctly sets the user agent
        """

        mock_client.return_value.get = get_200_response()

        wrapper = await AsyncVintedWrapper.create(BASE_URL)

        self.assertIsInstance(wrapper, AsyncVintedWrapper)
        self.assertEqual(wrapper._session_cookie, COOKIE_VALUE)
        self.assertIsNotNone(wrapper._user_agent)
        self.assertEqual(mock_client.return_value.get.call_count, 1)

        wrapper = await AsyncVintedWrapper.create(BASE_URL, user_agent=USER_AGENT)
        self.assertEqual(wrapper._user_agent, USER_AGENT)


if __name__ == "__main__":
    unittest.main()
# jscpd:ignore-end
