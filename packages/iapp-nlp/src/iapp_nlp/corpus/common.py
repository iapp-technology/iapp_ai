# SPDX-FileCopyrightText: 2016-2026 PyThaiNLP Project
# SPDX-FileContributor: iApp Technology
# SPDX-License-Identifier: Apache-2.0
"""Word lists bundled with iapp_nlp: Thai stopwords and Thailand provinces."""

import warnings
from importlib.resources import files
from typing import Dict, FrozenSet, List, Union

_STOPWORDS_FILE = "stopwords_th.txt"
_PROVINCES_FILE = "thailand_provinces_th.csv"

_stopwords: FrozenSet[str] = frozenset()
_provinces: FrozenSet[str] = frozenset()
_province_details: List[Dict[str, str]] = []


def thai_stopwords() -> FrozenSet[str]:
    """Return the Thai stopwords, e.g. "มี", "ไป", "ขณะ", "การ".

    The list is from a thesis by เพ็ญศิริ ลี้ตระกูล (การเลือกประโยคสำคัญในการสรุปความ
    ภาษาไทยโดยใช้แบบจำลองแบบลำดับชั้น, มหาวิทยาลัยธรรมศาสตร์, 2551).
    """
    global _stopwords
    if not _stopwords:
        _stopwords = frozenset(filter(None, _read_lines(_STOPWORDS_FILE)))
    return _stopwords


def provinces(details: bool = False) -> Union[FrozenSet[str], List[Dict[str, str]]]:
    """Return the Thai names of Thailand's provinces, e.g. "กระบี่", "กรุงเทพมหานคร".

    With ``details=True``, return one dict per province instead, e.g.
    ``{"name_th": "นนทบุรี", "abbr_th": "นบ", "name_en": "Nonthaburi", "abbr_en": "NBI"}``.
    """
    global _provinces, _province_details
    if not _provinces or not _province_details:
        names = set()
        rows = []
        for line in _read_lines(_PROVINCES_FILE):
            if not line.strip():
                continue
            parts = line.split(",")
            try:
                row = {
                    "name_th": parts[0],
                    "abbr_th": parts[1],
                    "name_en": parts[2],
                    "abbr_en": parts[3],
                }
            except IndexError:
                warnings.warn(
                    f"Skipping malformed province entry (too few fields): {line!r}",
                    UserWarning,
                    stacklevel=2,
                )
                continue
            if not all(value.strip() for value in row.values()):
                warnings.warn(
                    f"Skipping province entry with blank or empty field(s): {line!r}",
                    UserWarning,
                    stacklevel=2,
                )
                continue
            names.add(row["name_th"])
            rows.append(row)
        _provinces = frozenset(names)
        _province_details = rows
    if details:
        return _province_details
    return _provinces


def _read_lines(filename: str) -> List[str]:
    # utf-8-sig drops the byte order mark at the start of stopwords_th.txt
    return (files("iapp_nlp") / "data" / filename).read_text(encoding="utf-8-sig").splitlines()
