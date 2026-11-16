"""Thai word tokenizer with OpenThai2.0-LATTE-WordSeg-Lite, plus whitespace and number clean-up."""

import re
import threading
from typing import TYPE_CHECKING, Dict, FrozenSet, Iterable, List, Optional, Set

from .token import Token

if TYPE_CHECKING:
    from .latte import Segmenter

# Word units, coarse to fine
UNITS = ("long", "short", "minimal")

# Digits joined by "." "," or ":" (12:30, 1,234.5, 127.0.0.1); \d also matches Thai digits
_FORMATTED_NUMBER_RE = re.compile(r"\d+(?:[.,:]\d+)+")
# What the model reads in place of some characters, one for one so that offsets stay the same:
# Thai digits as Arabic digits, whose runs it never splits, and a zero-width space as a space,
# which always separates words and comes out as a token of its own
_MODEL_VIEW = str.maketrans({**{chr(0x0E50 + d): str(d) for d in range(10)}, "​": " "})

_segmenters: Dict[FrozenSet[str], "Segmenter"] = {}
_segmenters_lock = threading.Lock()


class Tokenizer:
    """Thai word tokenizer with the OpenThai2.0-LATTE-WordSeg-Lite model.

    The model loads when the first tokenizer is made (about 0.2 s), so make one at start-up and
    reuse it. Tokenizers with the same ``extra_words`` share one loaded model, and one tokenizer
    can serve many threads at once.

    ``unit`` sets how finely words are split: ``"long"`` keeps compounds whole (การศึกษา),
    ``"short"`` splits them into words (การ ศึกษา), and ``"minimal"`` splits words into their
    smallest meaningful parts (โรง เรียน).

    ``extra_words`` are hints, not rules: the model finds them in its dictionary but can still
    split them, depending on the text around them. Words with spaces, or shorter than 2 or longer
    than 16 characters, are left out with a ``UserWarning``. Each distinct set of words loads the model again, about
    10 MB that stays in memory until the process ends, so keep to a few fixed word sets.
    """

    def __init__(self, unit: str = "short", extra_words: Optional[Iterable[str]] = None):
        if unit not in UNITS:
            raise ValueError(f"unit must be one of {', '.join(map(repr, UNITS))}, not {unit!r}")
        words = frozenset(_clean_words(extra_words)) if extra_words is not None else frozenset()
        self.unit = unit
        self._segmenter = _segmenter(words)

    def tokenize(self, text: str, keep_whitespace: bool = True, join_broken_num: bool = True) -> List[Token]:
        """Split ``text`` into words, keeping each token's start/end offset.

        Each whitespace character is a token of its own. ``keep_whitespace=False`` drops spaces;
        tabs, new lines and zero-width spaces stay. ``join_broken_num=True`` rejoins formatted
        numbers that segmentation split, e.g. ``19:32``.
        """
        return self.tokenize_batch([text], keep_whitespace, join_broken_num)[0]

    def word_tokenize(self, text: str, keep_whitespace: bool = True, join_broken_num: bool = True) -> List[str]:
        """Split ``text`` into a list of word strings."""
        return [token.text for token in self.tokenize(text, keep_whitespace, join_broken_num)]

    def tokenize_batch(
        self, texts: Iterable[str], keep_whitespace: bool = True, join_broken_num: bool = True
    ) -> List[List[Token]]:
        """``tokenize`` each text, faster than one call per text.

        The model's int8 scales are worked out per batch, so about 1% of texts can come out
        slightly differently than when tokenized alone.
        """
        if isinstance(texts, str):
            raise TypeError("Pass a list of texts, not a single string")
        texts = list(texts)
        views = [text.translate(_MODEL_VIEW) for text in texts]
        result = []
        for text, pieces in zip(texts, self._segmenter.tokenize_batch(views, True, self.unit)):
            tokens = []
            start = 0
            # the pieces add up to the text, so offsets are running lengths
            for piece in pieces:
                end = start + len(piece)
                tokens.append(Token(text[start:end], start, end))
                start = end
            if join_broken_num:
                tokens = _join_formatted_numbers(text, tokens)
            if not keep_whitespace:
                tokens = _strip_spaces(tokens)
            result.append(tokens)
        return result

    def word_tokenize_batch(
        self, texts: Iterable[str], keep_whitespace: bool = True, join_broken_num: bool = True
    ) -> List[List[str]]:
        """``word_tokenize`` each text, faster than one call per text (see ``tokenize_batch``)."""
        return [
            [token.text for token in tokens]
            for tokens in self.tokenize_batch(texts, keep_whitespace, join_broken_num)
        ]


def tokenize(
    text: str,
    keep_whitespace: bool = True,
    join_broken_num: bool = True,
    unit: str = "short",
    extra_words: Optional[Iterable[str]] = None,
) -> List[Token]:
    """Split ``text`` into words, keeping each token's start/end offset.

    Each whitespace character is a token of its own. ``keep_whitespace=False`` drops spaces;
    tabs, new lines and zero-width spaces stay. ``join_broken_num=True`` rejoins formatted
    numbers that segmentation split, e.g. ``19:32``. ``unit`` is ``"long"``, ``"short"`` or
    ``"minimal"``, and ``extra_words`` are hints the model can still split (see ``Tokenizer``).
    The model loads on the first call and stays loaded for later calls with the same ``extra_words``.
    """
    return Tokenizer(unit, extra_words).tokenize(text, keep_whitespace, join_broken_num)


def word_tokenize(
    text: str,
    keep_whitespace: bool = True,
    join_broken_num: bool = True,
    unit: str = "short",
    extra_words: Optional[Iterable[str]] = None,
) -> List[str]:
    """Split ``text`` into a list of word strings (see ``tokenize``)."""
    return [token.text for token in tokenize(text, keep_whitespace, join_broken_num, unit, extra_words)]


def _segmenter(words: FrozenSet[str]) -> "Segmenter":
    """Return the segmenter for these extra words, loading it the first time they are asked for."""
    segmenter = _segmenters.get(words)
    if segmenter is None:
        # concurrent first calls wait for one load instead of each loading a copy
        with _segmenters_lock:
            segmenter = _segmenters.get(words)
            if segmenter is None:
                # imported here so that numpy and ONNX Runtime load only when words are first needed
                from .latte import Segmenter

                segmenter = Segmenter(user_words=sorted(words))
                _segmenters[words] = segmenter
    return segmenter


def _clean_words(words: Iterable[str]) -> Set[str]:
    """Strip each word and drop blanks; a word cannot contain a line break."""
    if isinstance(words, str):
        raise TypeError("Pass a list of words, not a single string")
    cleaned = set()
    for word in words:
        word = word.strip()
        if "\n" in word or "\r" in word:
            raise ValueError(f"A dictionary word cannot contain a line break: {word!r}")
        if word:
            cleaned.add(word)
    return cleaned


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
