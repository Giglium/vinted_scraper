import unittest

from src.vinted_scraper import get_random_user_agent


class MyTestCase(unittest.TestCase):
    def test_random_user_agent(self):
        """
        Ensure that the function doesn't raise any exceptions
        """
        try:
            get_random_user_agent()
        except Exception as e:
            self.fail(f"get_random_user_agent() raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()
