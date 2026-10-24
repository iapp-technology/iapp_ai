"""Thai word tokenizer: nlpo3 segmentation plus whitespace and number clean-up."""

import re
from typing import List

from . import crfcut, han_solo, nlpo3, tcc_p
from .tokenizer import Token

# Digits joined by "." "," or ":" (12:30, 1,234.5, 127.0.0.1); \d also matches Thai digits
_FORMATTED_NUMBER_RE = re.compile(r"\d+(?:[.,:]\d+)+")
# Whitespace other than plain spaces: tabs, new lines, carriage returns
_LINE_BREAK_RE = re.compile(r"[\t\n\r\f\v]+")


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


def syllable_tokenize(text: str, keep_whitespace: bool = True) -> List[str]:
    """Split ``text`` into Thai syllables with the Han-solo CRF model, e.g. ``นายก`` -> ``นา`` ``ยก``.

    Tabs and new lines come out as pieces of their own.
    ``keep_whitespace=False`` drops pieces made only of spaces (tabs and new lines stay).
    """
    if not text:
        return []
    syllables: List[str] = []
    pos = 0
    # the model never saw tabs or new lines in training and glues them to a neighbour, so cut them out first
    for match in _LINE_BREAK_RE.finditer(text):
        if match.start() > pos:
            syllables.extend(han_solo.segment(text[pos:match.start()]))
        syllables.append(match.group())
        pos = match.end()
    if pos < len(text):
        syllables.extend(han_solo.segment(text[pos:]))
    if not keep_whitespace:
        syllables = [syllable.strip(" ") for syllable in syllables if syllable.strip(" ")]
    return syllables


def sent_tokenize(text: str, keep_whitespace: bool = True) -> List[str]:
    """Split ``text`` into sentences with PyThaiNLP's CRF model (crfcut).

    Each line is split on its own, so a new line always ends a sentence.
    ``keep_whitespace=False`` trims spaces off each sentence and drops sentences that were only spaces.
    """
    if not text:
        return []
    sentences: List[str] = []
    leading = ""  # blank lines before the first sentence
    for line in text.splitlines(keepends=True):  # crfcut alone does not cut at "\n"
        if not line.strip():  # a blank line stays on the sentence before it
            if sentences:
                sentences[-1] += line
            else:
                leading += line
            continue
        pieces = crfcut.segment(line)
        pieces[0] = leading + pieces[0]
        leading = ""
        sentences.extend(pieces)
    if leading:  # the text was only blank lines or spaces
        sentences.append(leading)
    if not keep_whitespace:
        sentences = [sentence.strip(" ") for sentence in sentences if sentence.strip(" ")]
    return sentences


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
