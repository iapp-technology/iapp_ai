from iapp_nlp import Token, tokenize, word_tokenize


def test_english_splits_punctuation():
    assert word_tokenize("Hello, world!") == ["Hello", ",", "world", "!"]


def test_english_keeps_contractions():
    assert word_tokenize("I don't know") == ["I", "don't", "know"]


def test_thai_run_stays_whole():
    assert word_tokenize("สวัสดีครับ ยินดีต้อนรับ") == ["สวัสดีครับ", "ยินดีต้อนรับ"]


def test_thai_english_boundary():
    assert word_tokenize("ซื้อ iPhone15ราคา 30000 บาท!") == [
        "ซื้อ", "iPhone15", "ราคา", "30000", "บาท", "!",
    ]


def test_zero_width_space_is_a_separator():
    assert word_tokenize("สวัสดี\u200bครับ") == ["สวัสดี", "ครับ"]


def test_offsets_point_back_into_text():
    text = "สวัสดี hello"
    tokens = tokenize(text)
    assert tokens == [Token("สวัสดี", 0, 6), Token("hello", 7, 12)]
    assert all(text[t.start:t.end] == t.text for t in tokens)


def test_empty_string():
    assert word_tokenize("") == []