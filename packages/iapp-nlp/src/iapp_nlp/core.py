"""Thai word tokenizer: nlpo3 segmentation plus whitespace and number clean-up."""

import re
from typing import List

from . import nlpo3, tcc_p
from .tokenizer import Token

# Digits joined by "." "," or ":" (12:30, 1,234.5, 127.0.0.1); \d also matches Thai digits
_FORMATTED_NUMBER_RE = re.compile(r"\d+(?:[.,:]\d+)+")


def tokenize(text: str, keep_whitespace: bool = True, join_broken_num: bool = True) -> List[Token]:
    """Split ``text`` into words, keeping each token's start/end offset.

    ``keep_whitespace=False`` drops tokens made only of spaces (tabs and new lines stay).
    ``join_broken_num=True`` rejoins formatted numbers that segmentation split, e.g. ``19:32``.
    """
    if not text:
        return []
    tokens = []
    start = 0
    for piece in nlpo3.segment(text):  # the pieces add up to text, so offsets are running lengths
        tokens.append(Token(piece, start, start + len(piece)))
        start += len(piece)
    if join_broken_num:
        tokens = _join_formatted_numbers(text, tokens)
    if not keep_whitespace:
        tokens = _strip_spaces(tokens)
    return tokens


def word_tokenize(text: str, keep_whitespace: bool = True, join_broken_num: bool = True) -> List[str]:
    """Split ``text`` into a list of word strings."""
    return [token.text for token in tokenize(text, keep_whitespace, join_broken_num)]


def subword_tokenize(text: str, keep_whitespace: bool = True) -> List[str]:
    """Split ``text`` into Thai Character Clusters, e.g. ``ขนมชั้น`` -> ``ข`` ``น`` ``ม`` ``ชั้น``.

    Non-Thai characters come out one at a time, as in PyThaiNLP.
    ``keep_whitespace=False`` drops pieces made only of spaces (tabs and new lines stay).
    """
    if not text:
        return []
    pieces = tcc_p.segment(text)
    if not keep_whitespace:
        pieces = [piece.strip(" ") for piece in pieces if piece.strip(" ")]
    return pieces


def _join_formatted_numbers(text: str, tokens: List[Token]) -> List[Token]:
    """Merge the tokens that exactly cover one formatted number into a single token."""
    result: List[Token] = []
    i = 0
    for match in _FORMATTED_NUMBER_RE.finditer(text):
        while i < len(tokens) and tokens[i].end <= match.start():
            result.append(tokens[i])
            i += 1
        j = i
        while j < len(tokens) and tokens[j].end <= match.end():
            j += 1
        group = tokens[i:j]
        # merge only when the number starts and ends on token boundaries
        if len(group) > 1 and group[0].start == match.start() and group[-1].end == match.end():
            result.append(Token(match.group(), match.start(), match.end()))
            i = j
    result.extend(tokens[i:])
    return result


def _strip_spaces(tokens: List[Token]) -> List[Token]:
    """Trim spaces off each token and drop tokens that were only spaces, like PyThaiNLP."""
    result = []
    for token in tokens:
        stripped = token.text.strip(" ")
        if stripped:
            start = token.start + len(token.text) - len(token.text.lstrip(" "))
            result.append(Token(stripped, start, start + len(stripped)))
    return result
