# SPDX-FileCopyrightText: 2016-2026 PyThaiNLP Project
# SPDX-FileContributor: iApp Technology
# SPDX-License-Identifier: Apache-2.0
"""Thai sentence segmentation with a CRF model (crfcut), trained on TED subtitles.

``_ENDERS``, ``_STARTERS``, ``_extract_features`` and the label rules in
``segment`` must stay as they are: the model was trained on exactly these
features.

Model ``data/sentenceseg_crfcut.model``: PyThaiNLP Project, used unchanged under
CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
"""

import threading
from importlib.resources import as_file, files
from typing import List, Optional, Set

import pycrfsuite

from . import core  # module import: core also imports this file

_ENDERS: Set[str] = {
    # ending honorifics
    "ครับ",
    "ค่ะ",
    "คะ",
    "นะคะ",
    "นะ",
    "จ้ะ",
    "จ้า",
    "จ๋า",
    "ฮะ",
    # enders
    "ๆ",
    "ได้",
    "แล้ว",
    "ด้วย",
    "เลย",
    "มาก",
    "น้อย",
    "กัน",
    "เช่นกัน",
    "เท่านั้น",
    "อยู่",
    "ลง",
    "ขึ้น",
    "มา",
    "ไป",
    "ไว้",
    "เอง",
    "อีก",
    "ใหม่",
    "จริงๆ",
    "บ้าง",
    "หมด",
    "ทีเดียว",
    "เดียว",
    # demonstratives
    "นั้น",
    "นี้",
    "เหล่านี้",
    "เหล่านั้น",
    # questions
    "อย่างไร",
    "ยังไง",
    "หรือไม่",
    "มั้ย",
    "ไหน",
    "ไหม",
    "อะไร",
    "ทำไม",
    "เมื่อไหร่",
    "เมื่อไร",
}
_STARTERS: Set[str] = {
    # pronouns
    "ผม",
    "ฉัน",
    "ดิฉัน",
    "ชั้น",
    "คุณ",
    "มัน",
    "เขา",
    "เค้า",
    "เธอ",
    "เรา",
    "พวกเรา",
    "พวกเขา",
    "กู",
    "มึง",
    "แก",
    "ข้าพเจ้า",
    # connectors
    "และ",
    "หรือ",
    "แต่",
    "เมื่อ",
    "ถ้า",
    "ใน",
    "ด้วย",
    "เพราะ",
    "เนื่องจาก",
    "ซึ่ง",
    "ไม่",
    "ตอนนี้",
    "ทีนี้",
    "ดังนั้น",
    "เพราะฉะนั้น",
    "ฉะนั้น",
    "ตั้งแต่",
    "ในที่สุด",
    "ก็",
    "กับ",
    "แก่",
    "ต่อ",
    # demonstratives
    "นั้น",
    "นี้",
    "เหล่านี้",
    "เหล่านั้น",
}


def _extract_features(
    doc: List[str], window: int = 2, max_n_gram: int = 3
) -> List[List[str]]:
    """
    Extract CRF features from a list of words.

    The function slides n-grams of up to ``max_n_gram`` words over a window
    of ``window`` words before and after each word.

    :param List[str] doc: list of words to extract features from
    :param int window: size of the window before and after each word
    :param int max_n_gram: maximum n-gram size; create n-grams from
        1-gram to ``max_n_gram``-gram within the window
    :return: list of feature lists, one per word, to feed to the CRF
    :rtype: List[List[str]]
    """
    if not doc:
        return []

    doc_features = []
    # Pad the document with "xxpad" tokens efficiently
    padded_doc = ["xxpad"] * window
    padded_doc.extend(doc)
    padded_doc.extend(["xxpad"] * window)
    doc = padded_doc

    # add enders and starters
    doc_ender = ["ender" if token in _ENDERS else "normal" for token in doc]
    doc_starter = [
        "starter" if token in _STARTERS else "normal" for token in doc
    ]

    # for each word
    for i in range(window, len(doc) - window):
        # bias term
        word_features = ["bias"]
        # ngram features
        for n_gram in range(1, min(max_n_gram + 1, 2 + window * 2)):
            for j in range(i - window, i + window + 2 - n_gram):
                feature_position = f"{n_gram}_{j - i}_{j - i + n_gram}"
                word_ = f"{'|'.join(doc[j : (j + n_gram)])}"
                word_features += [f"word_{feature_position}={word_}"]
                ender_ = f"{'|'.join(doc_ender[j : (j + n_gram)])}"
                word_features += [f"ender_{feature_position}={ender_}"]
                starter_ = f"{'|'.join(doc_starter[j : (j + n_gram)])}"
                word_features += [f"starter_{feature_position}={starter_}"]
        # append to feature per word
        doc_features.append(word_features)

    return doc_features

_MODEL_FILE = "sentenceseg_crfcut.model"
_tagger_lock = threading.Lock()
_tagger: Optional[pycrfsuite.Tagger] = None


def _tag(features: List[List[str]]) -> List[str]:
    """Label each word "E" (ends a sentence) or "I", loading the model on first use."""
    global _tagger
    with _tagger_lock:
        if _tagger is None:
            tagger = pycrfsuite.Tagger()
            # the tagger reads the whole file when it opens, so the file may go afterwards
            with as_file(files("iapp_nlp") / "data" / _MODEL_FILE) as path:
                tagger.open(str(path))
            _tagger = tagger
        return list(_tagger.tag(features))


def segment(text: str) -> List[str]:
    """Split ``text`` into sentences; joining the result gives back ``text``."""
    toks = core.word_tokenize(text)
    if not toks:
        return []
    labs = _tag(_extract_features(toks))
    labs[-1] = "E"  # make sure it cuts the last sentence

    # To ensure splitting of sentences using Terminal Punctuation
    for idx, _ in enumerate(toks):
        if toks[idx].strip().endswith(("!", ".", "?")):
            labs[idx] = "E"
        # Spaces or empty strings would no longer be treated as end of sentence.
        elif (idx == 0 or labs[idx - 1] == "E") and toks[idx].strip() == "":
            labs[idx] = "I"

    sentences = []
    sentence = ""
    for i, w in enumerate(toks):
        sentence = sentence + w
        # Empty strings should not be part of output, and neither should
        # spaces alone: they stay with the sentence before them
        if labs[i] == "E" and sentence.strip():
            sentences.append(sentence)
            sentence = ""

    # spaces after the last sentence end are labelled "I" above; keep them so no text is lost
    if sentence:
        if sentences:
            sentences[-1] += sentence
        else:
            sentences.append(sentence)

    return sentences
