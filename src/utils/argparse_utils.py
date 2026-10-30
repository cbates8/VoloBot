"""ArgParse Utils"""

import argparse
from typing import override, Any

NONE_EQUIVALENT = ["none", "None", "null", "Null", ""]


def none_or_str(value: str) -> str | None:
    """Get Nonetype if possible, otherwise return string

    Args:
        value (`str`): Argument value

    Returns:
        `str` | `None`: Value as a string or None
    """
    if value in NONE_EQUIVALENT:
        return None
    return str(value)


def none_or_int(value: str) -> int | None:
    """Get Nonetype if possible, otherwise return int

    Args:
        value (`str`): Argument value

    Returns:
        `int` | `None`: Value converted to int or None
    """
    if value in NONE_EQUIVALENT:
        return None
    return int(value)


class ArgParseError(Exception):
    """An generic error from argparse"""

    def __init__(self, message: str, usage: str | None = None):
        super().__init__()
        self.message: str = message
        self.usage: str | None = usage

    @override
    def __str__(self):
        if self.usage is None:
            msg_format = "%(message)s"
        else:
            msg_format = "%(usage)s\n%(message)s"
        return msg_format % dict(message=self.message, usage=self.usage)


class CustArgParser(argparse.ArgumentParser):
    """Custom ArgumentParser"""

    def __init__(self, **kwargs: Any):  # pyright: ignore[reportExplicitAny]
        super().__init__(**kwargs)

    @override
    def error(self, message: str):
        """Overload of argparse.ArgumentParser.error

        Raises an exception instead of exiting the program.
        """
        raise ArgParseError(message, usage=self.format_usage())
