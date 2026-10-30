"""Thai text normalization: repeated, misordered and stray vowels and marks.

The rules come from PyThaiNLP's ``pythainlp/util/normalize.py`` (commit
8fe2ab7d) and its Thai character sets in ``pythainlp/__init__.py``.

Copyright 2016-2026 PyThaiNLP Project. Licensed under the Apache License 2.0;
see LICENSE-APACHE in this package. Changed by iApp Technology: only
``normalize`` is public, and the maiyamok helpers (which need PyThaiNLP's
tokenizer) are left out.
"""

import re
from typing import List, Tuple

_CONSONANTS = "กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮ"
_VOWELS = (
    "\u0e24\u0e26\u0e30\u0e31\u0e32\u0e33\u0e34\u0e35\u0e36\u0e37"
    "\u0e38\u0e39\u0e40\u0e41\u0e42\u0e43\u0e44\u0e45\u0e4d\u0e47"
)
_LEAD_VOWELS = "\u0e40\u0e41\u0e42\u0e43\u0e44"
_FOLLOW_VOWELS = "\u0e30\u0e32\u0e33\u0e45"
_ABOVE_VOWELS = "\u0e31\u0e34\u0e35\u0e36\u0e37\u0e4d\u0e47"
_BELOW_VOWELS = "\u0e38\u0e39"
_TONEMARKS = "\u0e48\u0e49\u0e4a\u0e4b"

# marks that cannot start a word: above/below vowels, tone marks, Phinthu,
# Thanthakhat, Nikhahit, Yamakkan
_DANGLING_CHARS = f"{_ABOVE_VOWELS}{_BELOW_VOWELS}{_TONEMARKS}\u0e3a\u0e4c\u0e4d\u0e4e"
_RE_DANGLING_AT_START = re.compile(f"^[{_DANGLING_CHARS}]+")
_RE_DANGLING_AFTER_SPACE = re.compile(f" +[{_DANGLING_CHARS}]+")

_ZERO_WIDTH_CHARS = "\u200b\u200c"  # ZWSP, ZWNJ

_REORDER_PAIRS: List[Tuple[str, str]] = [
    ("\u0e40\u0e40", "\u0e41"),  # Sara E + Sara E -> Sara Ae
    # tone mark/Thanthakhat + above/below vowel -> vowel + mark
    (f"([{_TONEMARKS}\u0e4c]+)([{_ABOVE_VOWELS}{_BELOW_VOWELS}]+)", "\\2\\1"),
    (f"\u0e4d([{_TONEMARKS}]*)\u0e32", "\\1\u0e33"),  # Nikhahit + Sara Aa -> Sara Am
    (f"([{_FOLLOW_VOWELS}]+)([{_TONEMARKS}]+)", "\\2\\1"),  # follow vowel + tone -> tone + vowel
    ("([^\u0e24\u0e26])\u0e45", "\\1\u0e32"),  # Lakkhangyao -> Sara Aa
]

_NOREPEAT_CHARS = (
    f"{_FOLLOW_VOWELS}{_LEAD_VOWELS}{_ABOVE_VOWELS}{_BELOW_VOWELS}\u0e3a\u0e4c\u0e4d\u0e4e"
)
_NOREPEAT_PAIRS: List[Tuple[str, str]] = [(f"({ch}[ ]*)+{ch}", ch) for ch in _NOREPEAT_CHARS]

_RE_TONEMARKS = re.compile(f"[{_TONEMARKS}]+")
_RE_NEWLINES = re.compile("[ \n]*\n[ \n]*")

# a single space before a mark, after a consonant not preceded by a vowel:
# fixes "พ ุ่ม" but keeps "ภาพ ุ่"
_RE_SPACE_BEFORE_MARK = re.compile(
    f"([{_CONSONANTS}])(?<![{_VOWELS}][{_CONSONANTS}]) ([{_DANGLING_CHARS}])"
)


def normalize(text: str) -> str:
    """Clean common Thai typing errors, e.g. ``เเปลก`` -> ``แปลก``, ``แล้้ว`` -> ``แล้ว``.

    Removes zero-width characters, duplicate spaces and blank lines (and
    surrounding spaces), spaces before tone marks and vowels, repeated vowels
    and signs, repeated tone marks (the last one is kept), and marks left at the
    start of the text or after a space. Tone marks and vowels are put in the
    standard order first. Letters are never changed, so a misspelled word stays
    misspelled.
    """
    text = _remove_zero_width(text)
    text = _remove_dup_spaces(text)
    text = _RE_SPACE_BEFORE_MARK.sub(r"\1\2", text)
    text = _remove_repeat_vowels(text)
    text = _RE_DANGLING_AT_START.sub("", text)
    return _RE_DANGLING_AFTER_SPACE.sub(" ", text)


def _remove_zero_width(text: str) -> str:
    for ch in _ZERO_WIDTH_CHARS:
        text = text.replace(ch, "")
    return text


def _remove_dup_spaces(text: str) -> str:
    while "  " in text:
        text = text.replace("  ", " ")
    return _RE_NEWLINES.sub("\n", text).strip()


def _remove_repeat_vowels(text: str) -> str:
    # reorder first so a double Sara E becomes Sara Ae instead of being dropped
    for pattern, repl in _REORDER_PAIRS:
        text = re.sub(pattern, repl, text)
    for pattern, repl in _NOREPEAT_PAIRS:
        text = re.sub(pattern, repl, text)
    return _RE_TONEMARKS.sub(_last_char, text)


def _last_char(match: "re.Match[str]") -> str:
    return match.group(0)[-1]
