import io
import sys
import threading

from iapp_nlp import Token, tokenize, word_tokenize
from iapp_nlp import cli
from iapp_nlp.tokenizer import nlpo3


def test_thai_sentence_splits_into_words():
    assert word_tokenize("นายกรัฐมนตรีเดินทางไปเชียงใหม่") == [
        "นายกรัฐมนตรี", "เดินทาง", "ไป", "เชียงใหม่",
    ]


def test_offsets_point_back_into_text():
    text = "ซื้อ iPhone15ราคา 30000 บาท!"
    tokens = tokenize(text)
    assert all(text[t.start:t.end] == t.text for t in tokens)
    assert "".join(t.text for t in tokens) == text  # whitespace kept, nothing lost


def test_english_splits_at_digits():
    # accepted on purpose: the whole text goes to nlpo3, which splits English at digits
    assert word_tokenize("ซื้อ iPhone15ราคา 30000 บาท!") == [
        "ซื้อ", " ", "iPhone", "15", "ราคา", " ", "30000", " ", "บาท", "!",
    ]


def test_keep_whitespace_false_drops_only_spaces():
    text = "บรรทัดแรก\nบรรทัดสอง สาม"
    assert word_tokenize(text, keep_whitespace=False) == [
        "บรรทัด", "แรก", "\n", "บรรทัด", "สอง", "สาม",
    ]


def test_keep_whitespace_false_trims_spaces_and_keeps_offsets():
    text = "abc  \t def"
    assert tokenize(text, keep_whitespace=False) == [
        Token("abc", 0, 3), Token("\t", 5, 6), Token("def", 7, 10),
    ]


def test_zero_width_space_is_kept():
    assert word_tokenize("สวัสดี​ครับ", keep_whitespace=False) == ["สวัสดี", "​", "ครับ"]


def test_formatted_numbers_are_joined():
    assert word_tokenize("เงิน1,234บาท19:32น 127.0.0.1") == [
        "เงิน", "1,234", "บาท", "19:32", "น", " ", "127.0.0.1",
    ]


def test_formatted_numbers_join_thai_digits():
    assert word_tokenize("๑๒:๓๐ น.") == ["๑๒:๓๐", " ", "น."]


def test_join_broken_num_false_leaves_numbers_split():
    assert word_tokenize("19:32น", join_broken_num=False) == ["19", ":", "32", "น"]


def test_numbers_split_by_spaces_are_not_joined():
    assert word_tokenize("19 : 32", keep_whitespace=False) == ["19", ":", "32"]


def test_empty_string():
    assert tokenize("") == []
    assert word_tokenize("") == []


def test_dictionary_loads_once_across_threads():
    results = []
    threads = [
        threading.Thread(target=lambda: results.append(word_tokenize("เชียงใหม่")))
        for _ in range(8)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    nlpo3.load_dict()  # loading again is a no-op, not an error
    assert results == [["เชียงใหม่"]] * 8


def test_cli_prints_words_without_spaces(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["iapp-tokenize", "นายกรัฐมนตรี", "เดินทาง"])
    cli.main()
    assert capsys.readouterr().out == "นายกรัฐมนตรี | เดินทาง\n"


def test_cli_reads_stdin(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["iapp-tokenize"])
    monkeypatch.setattr(sys, "stdin", io.StringIO("ไปเชียงใหม่\n"))
    cli.main()
    assert capsys.readouterr().out == "ไป | เชียงใหม่\n"
