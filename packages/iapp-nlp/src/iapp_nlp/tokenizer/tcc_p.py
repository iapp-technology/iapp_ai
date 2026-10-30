# SPDX-FileCopyrightText: 2016-2026 PyThaiNLP Project
# SPDX-FileContributor: iApp Technology
# SPDX-License-Identifier: Apache-2.0
"""Thai Character Cluster (TCC) segmentation with the improved rules that newmm uses.

The rules follow Theeramunkong et al. 2000 (https://doi.org/10.1145/355214.355225).

Credits:

* TCC: Jakkrit TeCho
* Grammar: Wittawat Jitkrittum (https://github.com/wittawatj/jtcc/blob/master/TCC.g)
* Python code: Korakot Chaovavanich
"""

import re
from typing import List

_RE_TCC: List[str] = (
    """\
เc็ck
เcctาะk
เccีtยะk
เccีtย(?=[เ-ไก-ฮ]|$)k
เcc็ck
เcิc์ck
เcิtck
เcีtยะ?k
เcืtอะ?k
เc[ิีุู]tย(?=[เ-ไก-ฮ]|$)k
เctา?ะ?k
cัtวะk
c[ัื]tc[ุิะ]?k
c[ิุู]์
c[ะ-ู]tk
cรรc์
c็
ct[ะาำ]?k
ck
แc็c
แcc์
แctะ
แcc็c
แccc์
โctะ
[เ-ไ]ct
ก็
อึ
หึ
""".replace("k", "(cc?[dิ]?[์])?")
    .replace("c", "[ก-ฮ]")
    .replace("t", "[่-๋]?")
    .replace("d", "อูอุ".replace("อ", ""))  # DSara: lower vowel
    .split()
)

_PAT_TCC = re.compile("|".join(_RE_TCC))


def segment(text: str) -> List[str]:
    """Split ``text`` into Thai Character Clusters, the smallest units that cannot be cut."""
    result = []
    pos = 0
    while pos < len(text):
        # match at pos instead of on text[pos:], which would copy the rest of the text every step
        match = _PAT_TCC.match(text, pos)
        end = match.end() if match else pos + 1
        result.append(text[pos:end])
        pos = end
    return result
