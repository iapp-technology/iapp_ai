"""Tests for extra_words and the Tokenizer class."""

import pytest

from iapp_ai.nlp import Token, Tokenizer, tokenize, word_tokenize
from iapp_ai.nlp.tokenizer import core, latte

TEXT = "ไอแอพพ์เทคโนโลยีอยู่ที่กรุงเทพ"
NAME = "ไอแอพพ์เทคโนโลยี"


def test_extra_words_are_hints_the_model_reads():
    assert word_tokenize(TEXT) == ["ไอแอพพ์", "เทคโนโลยี", "อยู่", "ที่", "กรุงเทพ"]
    assert word_tokenize(TEXT, extra_words=[NAME]) == [NAME, "อยู่", "ที่", "กรุงเทพ"]


def test_tokenizer_matches_the_functions_and_keeps_offsets():
    tokenizer = Tokenizer(extra_words=[NAME])
    assert tokenizer.word_tokenize(TEXT) == word_tokenize(TEXT, extra_words=[NAME])
    tokens = tokenizer.tokenize(TEXT)
    assert tokens == tokenize(TEXT, extra_words=[NAME])
    assert all(TEXT[token.start:token.end] == token.text for token in tokens)


def test_tokenizer_options_work_as_in_word_tokenize():
    tokenizer = Tokenizer(unit="long")
    assert tokenizer.unit == "long"
    assert tokenizer.word_tokenize("ข้อ 4.1 ระบุว่า", keep_whitespace=False) == ["ข้อ", "4.1", "ระบุ", "ว่า"]
    assert tokenizer.word_tokenize("ข้อ 4.1 ระบุว่า", keep_whitespace=False, join_broken_num=False) == [
        "ข้อ", "4", ".", "1", "ระบุ", "ว่า",
    ]
    assert tokenizer.word_tokenize("") == []


def test_batch():
    tokenizer = Tokenizer()
    texts = ["ฉันกินข้าวที่บ้าน", "วันนี้ อากาศดีมาก", ""]
    assert tokenizer.word_tokenize_batch(texts) == [
        ["ฉัน", "กิน", "ข้าว", "ที่", "บ้าน"],
        ["วัน", "นี้", " ", "อากาศ", "ดี", "มาก"],
        [],
    ]
    assert tokenizer.word_tokenize_batch(texts, keep_whitespace=False)[1] == ["วัน", "นี้", "อากาศ", "ดี", "มาก"]
    assert tokenizer.tokenize_batch(["ข้อ ๔.๑ ระบุว่า"], keep_whitespace=False) == [
        [Token("ข้อ", 0, 3), Token("๔.๑", 4, 7), Token("ระบุ", 8, 12), Token("ว่า", 12, 15)],
    ]
    assert tokenizer.word_tokenize_batch(["ข้อ 4.1"], join_broken_num=False) == [["ข้อ", " ", "4", ".", "1"]]


def test_batch_takes_any_iterable_but_not_a_string():
    tokenizer = Tokenizer()
    assert tokenizer.word_tokenize_batch(text for text in ["สวัสดีครับ"]) == [["สวัสดี", "ครับ"]]
    with pytest.raises(TypeError, match="list of texts"):
        tokenizer.word_tokenize_batch("สวัสดีครับ")


@pytest.fixture
def loads(monkeypatch):
    """Record the extra words of each model load, starting with no model loaded."""
    calls = []
    segmenter = latte.Segmenter
    monkeypatch.setattr(core, "_segmenters", {})
    monkeypatch.setattr(
        latte, "Segmenter", lambda **kwargs: calls.append(kwargs["user_words"]) or segmenter(**kwargs)
    )
    return calls


def test_tokenizer_loads_the_model_when_made(loads):
    Tokenizer()
    assert loads == [[]]


def test_same_words_load_once(loads):
    Tokenizer(extra_words=["ไอแอพพ์", "แชทจีพีที"])
    Tokenizer(extra_words=[" แชทจีพีที ", "ไอแอพพ์", "ไอแอพพ์", ""])  # same words after cleaning, in another order
    word_tokenize(TEXT, extra_words=["แชทจีพีที", "ไอแอพพ์"])
    assert loads == [["แชทจีพีที", "ไอแอพพ์"]]


@pytest.mark.parametrize("extra_words", [None, [], ["", "  "]])
def test_no_extra_words_share_one_model(loads, extra_words):
    Tokenizer()
    Tokenizer(extra_words=extra_words)
    word_tokenize("สวัสดี", extra_words=extra_words)
    assert loads == [[]]


def test_unknown_unit_is_an_error_before_loading(loads):
    with pytest.raises(ValueError, match="unit must be one of"):
        Tokenizer(unit="paragraph")
    assert loads == []


def test_word_with_a_line_break_is_an_error():
    with pytest.raises(ValueError, match="line break"):
        Tokenizer(extra_words=["ก\nข"])


def test_a_single_string_is_an_error():
    with pytest.raises(TypeError, match="list of words"):
        Tokenizer(extra_words="ไอแอพพ์")
