"""Tests for custom dictionaries: extra_words, custom_dict and Tokenizer."""

import pytest

from iapp_nlp import Tokenizer, tokenize, word_tokenize
from iapp_nlp.corpus import thai_words
from iapp_nlp.tokenizer import nlpo3

TEXT = "ชาไข่มุกบราวน์ชูการ์อร่อย"


def test_default_dictionary_splits_an_unknown_name():
    assert word_tokenize(TEXT) == ["ชา", "ไข่", "มุ", "กบ", "ราวน์", "ชู", "การ์", "อร่อย"]


def test_extra_words_add_to_the_bundled_dictionary():
    assert word_tokenize(TEXT, extra_words=["บราวน์ชูการ์"]) == ["ชา", "ไข่มุก", "บราวน์ชูการ์", "อร่อย"]


def test_custom_dict_replaces_the_bundled_dictionary():
    assert word_tokenize("ไอแอพพ์เปิดตัวโมเดลใหม่", custom_dict=["ไอแอพพ์"]) == ["ไอแอพพ์", "เปิดตัวโมเดลใหม่"]


def test_custom_dict_and_extra_words_together():
    words = word_tokenize("ไอแอพพ์เปิดตัว", custom_dict=["ไอแอพพ์"], extra_words=["เปิดตัว"])
    assert words == ["ไอแอพพ์", "เปิดตัว"]


def test_tokenizer_matches_the_functions_and_keeps_offsets():
    tokenizer = Tokenizer(extra_words=["บราวน์ชูการ์"])
    assert tokenizer.word_tokenize(TEXT) == word_tokenize(TEXT, extra_words=["บราวน์ชูการ์"])
    tokens = tokenizer.tokenize(TEXT)
    assert tokens == tokenize(TEXT, extra_words=["บราวน์ชูการ์"])
    assert all(TEXT[token.start:token.end] == token.text for token in tokens)


def test_tokenizer_options_work_as_in_word_tokenize():
    tokenizer = Tokenizer(extra_words=["บราวน์ชูการ์"])
    assert tokenizer.word_tokenize("นัดเวลา 19:32น.", keep_whitespace=False) == ["นัด", "เวลา", "19:32", "น."]
    assert tokenizer.word_tokenize("") == []


def test_tokenizer_without_words_uses_the_bundled_dictionary():
    assert Tokenizer().word_tokenize(TEXT) == word_tokenize(TEXT)


def test_same_words_load_once(monkeypatch):
    calls = []
    load_dict = nlpo3.nlpo3.load_dict
    monkeypatch.setattr(nlpo3, "_custom_dicts", {})
    monkeypatch.setattr(nlpo3.nlpo3, "load_dict", lambda path, name: calls.append(name) or load_dict(path, name))
    Tokenizer(custom_dict=["ก", "ข"])
    Tokenizer(custom_dict=[" ข ", "ก", "ก"])  # same words after cleaning, in another order
    assert len(calls) == 1


def test_words_are_stripped_and_blanks_dropped():
    assert word_tokenize("กขค", custom_dict=[" กข ", "", "  "]) == ["กข", "ค"]


@pytest.mark.parametrize("words", [[], ["", "  "]])
def test_empty_dictionary_is_an_error(words):
    with pytest.raises(ValueError, match="no words"):
        Tokenizer(custom_dict=words)


def test_word_with_a_line_break_is_an_error():
    with pytest.raises(ValueError, match="line break"):
        Tokenizer(extra_words=["ก\nข"])


def test_a_single_string_is_an_error():
    with pytest.raises(TypeError, match="list of words"):
        Tokenizer(extra_words="บราวน์ชูการ์")


def test_thai_words():
    words = thai_words()
    assert isinstance(words, frozenset)
    assert len(words) == 62106  # 62,107 lines, "โรม่า" is listed twice
    assert {"นายกรัฐมนตรี", "เชียงใหม่"} <= words
