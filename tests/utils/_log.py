"""
log utils
"""

import sys


def assert_no_logs(func, test, level, *args, **kwargs):
    """
    Executes the given function within UnitTest.assertNoLogs
    if Python version is 3.10 or higher.

    :param func: A callable (function) to execute.
    :param test: The test case instance, which has self.assertNoLogs.
    :param level: The log level to use.
    :param args: Positional arguments for func.
    :param kwargs: Keyword arguments for func.
    """
    py_version = sys.version_info

    if py_version.major >= 3 and py_version.minor >= 10:
        with test.assertNoLogs(level=level):
            func(*args, **kwargs)
