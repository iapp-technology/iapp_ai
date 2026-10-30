"""Thai syllable segmentation with the Han-solo CRF model.

``Featurizer`` and ``segment`` come from PyThaiNLP's ``pythainlp/tokenize/han_solo.py``
(commit 8fe2ab7d); ``Featurizer`` is from ssg (https://github.com/ponrawee/ssg).
They must stay as they are: the model was trained on exactly these features.
Han-solo: https://github.com/PyThaiNLP/Han-solo

Code: Copyright 2016-2026 PyThaiNLP Project, Copyright 2019 Ponrawee Prasertsom.
Model ``data/han_solo.crfsuite``: Han-solo project, used unchanged.
Both under the Apache License 2.0 (see LICENSE-APACHE in this package).
Changed by iApp Technology: the model file is closed once loaded and a lock
guards the tagger.
"""

import threading
from importlib.resources import as_file, files
from typing import Any, Dict, List, Optional, Tuple

import pycrfsuite

_MODEL_FILE = "han_solo.crfsuite"
_tagger_lock = threading.Lock()
_tagger: Optional[pycrfsuite.Tagger] = None


def _tag(features: List[List[str]]) -> List[str]:
    """Label each character "1" (starts a syllable) or "0", loading the model on first use."""
    global _tagger
    with _tagger_lock:
        if _tagger is None:
            tagger = pycrfsuite.Tagger()
            # the tagger reads the whole file when it opens, so the file may go afterwards
            with as_file(files("iapp_nlp") / "data" / _MODEL_FILE) as path:
                tagger.open(str(path))
            _tagger = tagger
        return list(_tagger.tag(features))


class Featurizer:
    """Extract character n-gram features for Han-solo."""

    #  This class from ssg at https://github.com/ponrawee/ssg.

    N: int
    delimiter: Optional[str]
    radius: int

    def __init__(
        self,
        N: int = 2,
        sequence_size: int = 1,
        delimiter: Optional[str] = None,
    ) -> None:
        """
        Initialize the featurizer.

        :param int N: size of the character n-gram
        :param int sequence_size: size of the character sequence
        :param Optional[str] delimiter: delimiter character in the text
        """
        self.N: int = N
        self.delimiter: Optional[str] = delimiter
        self.radius: int = N + sequence_size

    def pad(self, sentence: str, padder: str = "#") -> str:
        """
        Pad a sentence with a padding character on both sides.

        :param str sentence: sentence to pad
        :param str padder: padding character
        :return: padded sentence
        :rtype: str
        """
        return padder * (self.radius) + sentence + padder * (self.radius)

    def _skip_delimiter(
        self, sentence: str, abs_index: int, step: int
    ) -> Tuple[int, str]:
        """
        Skip the delimiter, moving ``abs_index`` by ``step``.

        :param str sentence: sentence to scan
        :param int abs_index: index to start from
        :param int step: step to move the index by
        :return: new index and the character at that index
        :rtype: Tuple[int, str]
        """
        char = sentence[abs_index]
        while char == self.delimiter:
            abs_index += step
            char = sentence[abs_index]
        return abs_index, char

    def _context_features(
        self, sentence: str, current_position: int, indiv_char: bool
    ) -> List[str]:
        """Extract features around the current position."""
        features: List[str] = []
        chars_left = ""
        chars_right = ""
        abs_index_left = current_position  # left start at -1
        abs_index_right = current_position - 1  # right start at 0
        for counter in range(self.radius):
            abs_index_left -= (
                1  # สมมุติตำแหน่งที่ 0 จะได้ -1, -2, -3, -4, -5 (radius = 5)
            )
            abs_index_left, char_left = self._skip_delimiter(
                sentence, abs_index_left, -1
            )
            # เก็บตัวหนังสือ
            chars_left = char_left + chars_left
            # ใส่ลง feature
            if indiv_char:
                features.append("|".join([str(-counter - 1), char_left]))

            abs_index_right += (
                1  # สมมุติคือตำแหน่งที่ 0 จะได้ 0, 1, 2, 3, 4 (radius = 5)
            )
            abs_index_right, char_right = self._skip_delimiter(
                sentence, abs_index_right, 1
            )
            chars_right += char_right
            if indiv_char:
                features.append("|".join([str(counter), char_right]))

        chars = chars_left + chars_right
        for i in range(len(chars) - self.N + 1):
            ngram = chars[i : i + self.N]
            features.append("|".join([str(i - self.radius), ngram]))
        return features

    def featurize(
        self,
        sentence: str,
        padding: bool = True,
        indiv_char: bool = True,
        return_type: str = "list",
    ) -> Dict[str, List[Any]]:
        """
        Extract features and labels from a sentence.

        :param str sentence: sentence to featurize
        :param bool padding: pad the sentence first
        :param bool indiv_char: include features of individual characters
        :param str return_type: type of the features (list or dict)
        :return: features (X) and labels (Y)
        :rtype: Dict[str, List[Any]]
        """
        if padding:
            sentence = self.pad(sentence)
        all_features_list: List[List[str]] = []
        all_labels_int: List[int] = []
        skip_next = False
        for current_position in range(
            self.radius, len(sentence) - self.radius + 1
        ):
            if skip_next:
                skip_next = False
                continue
            cut = 0
            if sentence[current_position] == self.delimiter:
                cut = 1
                skip_next = True
            all_features_list.append(
                self._context_features(sentence, current_position, indiv_char)
            )
            all_labels_int.append(cut)

        if return_type == "list":
            return {
                "X": all_features_list,
                "Y": [str(label) for label in all_labels_int],
            }
        return {
            "X": [
                dict.fromkeys(feature_list, 1)
                for feature_list in all_features_list
            ],
            "Y": all_labels_int,
        }


_to_feature: Featurizer = Featurizer()


def segment(text: str) -> List[str]:
    """
    Split ``text`` into syllables with Han-solo; joining the result gives back ``text``.

    :param str text: text to be tokenized
    :return: list of syllables
    :rtype: List[str]
    """
    x = _to_feature.featurize(text)["X"]
    y_pred = _tag(x)
    list_cut: List[str] = []
    for j, k in zip(list(text), y_pred):
        if k == "1" or not list_cut:
            list_cut.append(j)
        else:
            list_cut[-1] += j
    return list_cut
