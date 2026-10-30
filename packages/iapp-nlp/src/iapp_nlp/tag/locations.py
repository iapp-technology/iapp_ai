# SPDX-FileCopyrightText: 2016-2026 PyThaiNLP Project
# SPDX-FileContributor: iApp Technology
# SPDX-License-Identifier: Apache-2.0
"""Tag Thailand provinces in a list of words."""

from typing import List, Tuple

from ..corpus import provinces


def tag_provinces(tokens: List[str]) -> List[Tuple[str, str]]:
    """Tag each word that is a province name ``B-LOCATION``, the rest ``O``.

    Words are matched exactly, without context, e.g.
    ``["หนองคาย", "น่าอยู่"]`` -> ``[("หนองคาย", "B-LOCATION"), ("น่าอยู่", "O")]``.
    """
    province_list = provinces()
    return [(token, "B-LOCATION") if token in province_list else (token, "O") for token in tokens]
