"""Thai Character Cluster (TCC) segmentation with the improved rules that newmm uses.

The rule table (``_RE_TCC``) comes from PyThaiNLP's ``pythainlp/tokenize/tcc_p.py``
(commit 8fe2ab7d), which follows Theeramunkong et al. 2000
(https://doi.org/10.1145/355214.355225). Credits: TCC by Jakkrit TeCho,
grammar by Wittawat Jitkrittum, Python code by Korakot Chaovavanich.

Copyright 2016-2026 PyThaiNLP Project. Licensed under the Apache License 2.0;
see LICENSE-APACHE in this package. Changed by iApp Technology: ``segment``
matches at a position instead of slicing the rest of the text, so it runs in
linear time.
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
