"""The token type returned by ``tokenize``."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    """One token and where it sits in the original text."""

    text: str
    start: int
    end: int
