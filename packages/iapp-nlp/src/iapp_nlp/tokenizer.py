"""Rule-based Thai/English tokenizer (no model, no dictionary)."""

import re
from dataclasses import dataclass
from typing import List

_TOKEN_RE = re.compile(
    r"[\u0E00-\u0E7F]+"                  # a run of Thai characters
    r"|[A-Za-z0-9]+(?:['’][A-Za-z]+)*"   # an English word or number; keeps "don't"
    r"|[^\s\u200b]"                      # any other single symbol; ZWSP acts as a separator
)


@dataclass(frozen=True)
class Token:
    """One token and where it sits in the original text."""

    text: str
    start: int
    end: int


def tokenize(text: str) -> List[Token]:
    """Split ``text`` into tokens, keeping each token's start/end offset."""
    return [Token(m.group(), m.start(), m.end()) for m in _TOKEN_RE.finditer(text)]


def word_tokenize(text: str) -> List[str]:
    """Split ``text`` into a list of token strings."""
    return [token.text for token in tokenize(text)]
