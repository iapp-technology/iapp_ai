"""tag_provinces; the first case is from PyThaiNLP's tests/core/test_tag.py (commit 8fe2ab7d)."""

from iapp_nlp import word_tokenize
from iapp_nlp.tag import tag_provinces


def test_tag_provinces():
    assert tag_provinces(["หนองคาย", "น่าอยู่"]) == [("หนองคาย", "B-LOCATION"), ("น่าอยู่", "O")]


def test_tag_provinces_after_word_tokenize():
    words = word_tokenize("ผมไปเชียงใหม่กับกรุงเทพมหานคร", keep_whitespace=False)
    tagged = dict(tag_provinces(words))
    assert tagged["เชียงใหม่"] == "B-LOCATION"
    assert tagged["กรุงเทพมหานคร"] == "B-LOCATION"
    assert tagged["ผม"] == "O"


def test_tag_provinces_matches_exactly():
    # abbreviations and English names are not in the name list
    assert tag_provinces(["กทม", "Bangkok", ""]) == [("กทม", "O"), ("Bangkok", "O"), ("", "O")]


def test_tag_provinces_empty_list():
    assert tag_provinces([]) == []
