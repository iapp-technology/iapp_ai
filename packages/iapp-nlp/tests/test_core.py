import io
import subprocess
import sys
import threading

import pytest

from iapp_nlp import Token, Tokenizer, cli, tokenize, word_tokenize, word_tokenize_nbest
from iapp_nlp.tokenizer import core, latte

# The examples below were chosen with a clear margin (|logit| >= 0.7 at every boundary the model
# decides), so that small numeric differences between CPUs or ONNX Runtime versions do not flip them.


def test_thai_sentence_splits_into_words():
    assert word_tokenize("แม่น้ำเจ้าพระยาไหลผ่านกรุงเทพ") == ["แม่น้ำ", "เจ้าพระยา", "ไหล", "ผ่าน", "กรุงเทพ"]


@pytest.mark.parametrize(
    "unit, words",
    [
        ("long", ["เจ้าหน้าที่", "การศึกษา", "เปิดเผย", "ว่า"]),
        ("short", ["เจ้า", "หน้าที่", "การ", "ศึกษา", "เปิด", "เผย", "ว่า"]),
        ("minimal", ["เจ้า", "หน้า", "ที่", "การ", "ศึกษา", "เปิด", "เผย", "ว่า"]),
    ],
)
def test_units(unit, words):
    assert word_tokenize("เจ้าหน้าที่การศึกษาเปิดเผยว่า", unit=unit) == words


def test_default_unit_is_short():
    text = "เจ้าหน้าที่การศึกษาเปิดเผยว่า"
    assert word_tokenize(text) == word_tokenize(text, unit="short")


@pytest.mark.parametrize("unit", ["paragraph", "word", "Short", "", None])
def test_unknown_unit_is_an_error(unit):
    with pytest.raises(ValueError, match="unit must be one of"):
        word_tokenize("ทดสอบ", unit=unit)


def test_offsets_point_back_into_text():
    text = "ซื้อ iPhone15ราคา 30000 บาท!"
    tokens = tokenize(text)
    assert all(text[t.start:t.end] == t.text for t in tokens)
    assert "".join(t.text for t in tokens) == text  # whitespace kept, nothing lost


def test_english_splits_at_digits():
    # runs of Latin letters and of digits stay whole, but a letter run and a digit run can split
    assert word_tokenize("ซื้อ iPhone15ราคา 30000 บาท!") == [
        "ซื้อ", " ", "iPhone", "15", "ราคา", " ", "30000", " ", "บาท", "!",
    ]


def test_each_whitespace_character_is_a_token():
    assert word_tokenize("ไป  ไหน") == ["ไป", " ", " ", "ไหน"]


def test_keep_whitespace_false_drops_only_spaces():
    text = "บรรทัดแรก\nบรรทัดสอง สาม"
    assert word_tokenize(text, keep_whitespace=False) == [
        "บรรทัด", "แรก", "\n", "บรรทัด", "สอง", "สาม",
    ]


def test_keep_whitespace_false_keeps_offsets():
    text = "abc  \t def"
    assert tokenize(text, keep_whitespace=False) == [
        Token("abc", 0, 3), Token("\t", 5, 6), Token("def", 7, 10),
    ]


@pytest.mark.parametrize(
    "text, words",
    [
        ("สวัสดี​ครับ", ["สวัสดี", "​", "ครับ"]),
        ("abc​def", ["abc", "​", "def"]),  # the model alone keeps this whole
    ],
)
def test_zero_width_space_is_a_token_of_its_own(text, words):
    assert word_tokenize(text, keep_whitespace=False) == words


@pytest.mark.parametrize("unit", core.UNITS)
def test_thai_digit_runs_are_never_split(unit):
    # the model alone splits this number into ๐๘ ๑ ๒ ๓ ๔ ๕ ๖๗๘
    assert word_tokenize("โทร ๐๘๑๒๓๔๕๖๗๘", unit=unit) == ["โทร", " ", "๐๘๑๒๓๔๕๖๗๘"]


@pytest.mark.parametrize("unit", core.UNITS)
@pytest.mark.parametrize("text", ["โทร 0812345678", "ราคา1,250บาท เวลา 12:30 น.", "ข้อ 4.1 ระบุว่า", "ก3"])
def test_thai_digits_split_like_arabic_digits(text, unit):
    thai = text.translate(str.maketrans("0123456789", "๐๑๒๓๔๕๖๗๘๙"))
    arabic_words = word_tokenize(text, join_broken_num=False, unit=unit)
    thai_words = word_tokenize(thai, join_broken_num=False, unit=unit)
    assert [len(word) for word in thai_words] == [len(word) for word in arabic_words]


def test_formatted_numbers_are_joined():
    assert word_tokenize("เงิน1,234บาท19:32น 127.0.0.1") == [
        "เงิน", "1,234", "บาท", "19:32", "น", " ", "127.0.0.1",
    ]


def test_join_broken_num_false_leaves_numbers_split():
    text = "ข้อ 4.1 ระบุว่า"
    assert word_tokenize(text, keep_whitespace=False) == ["ข้อ", "4.1", "ระบุ", "ว่า"]
    assert word_tokenize(text, keep_whitespace=False, join_broken_num=False) == [
        "ข้อ", "4", ".", "1", "ระบุ", "ว่า",
    ]


def test_formatted_numbers_join_thai_digits():
    assert word_tokenize("ข้อ ๔.๑ ระบุว่า", keep_whitespace=False) == ["ข้อ", "๔.๑", "ระบุ", "ว่า"]


def test_numbers_split_by_spaces_are_not_joined():
    assert word_tokenize("19 : 32", keep_whitespace=False) == ["19", ":", "32"]


def test_empty_string():
    assert tokenize("") == []
    assert word_tokenize("") == []


@pytest.mark.parametrize("bad", [None, 42, "ไทย".encode(), ["ไทย"]])
def test_text_must_be_a_string(bad):
    with pytest.raises(TypeError, match="text must be a str"):
        word_tokenize(bad)
    with pytest.raises(TypeError, match="text must be a str"):
        core.Tokenizer().word_tokenize_batch(["ไทย", bad])
    with pytest.raises(TypeError, match="text must be a str"):
        word_tokenize_nbest(bad)


def test_nbest_gives_the_readings_of_an_ambiguous_phrase():
    readings = word_tokenize_nbest("ตากลม", 3)
    assert sorted(words for words, _ in readings) == [["ตา", "กลม"], ["ตาก", "ลม"], ["ตากลม"]]
    assert readings[0][0] == word_tokenize("ตากลม")


@pytest.mark.parametrize("unit", core.UNITS)
@pytest.mark.parametrize("text", ["ไปหามเหสี", "ราคา ๑๒,๕๐๐ บาท", "ประชุม 12:30 น.", "สวัสดี\nครับ", ""])
def test_nbest_starts_with_word_tokenize(text, unit):
    readings = word_tokenize_nbest(text, 5, unit=unit)
    assert readings[0][0] == word_tokenize(text, unit=unit)
    assert all("".join(words) == text for words, _ in readings)
    probabilities = [probability for _, probability in readings[1:]]
    assert probabilities == sorted(probabilities, reverse=True)


def test_nbest_joins_numbers_and_drops_the_copies_this_makes():
    readings = word_tokenize_nbest("ประชุม 12:30 น.", 10)
    assert all("12:30" in words for words, _ in readings)
    assert len({tuple(words) for words, _ in readings}) == len(readings)


def test_nbest_keep_whitespace_false_drops_only_spaces():
    for words, _ in word_tokenize_nbest("ตากลม iPhone\n15", 3, keep_whitespace=False):
        assert " " not in words and "\n" in words


def test_nbest_with_a_tokenizer():
    tokenizer = Tokenizer(unit="long")
    [(words, probability)] = tokenizer.word_tokenize_nbest("เจ้าหน้าที่การศึกษา", 1)
    assert words == tokenizer.word_tokenize("เจ้าหน้าที่การศึกษา") == ["เจ้าหน้าที่", "การศึกษา"]
    assert 0 < probability <= 1


@pytest.mark.parametrize("n", [0, 101])
def test_nbest_limits(n):
    with pytest.raises(ValueError, match="n must be between 1 and 100"):
        word_tokenize_nbest("ตากลม", n)
    with pytest.raises(ValueError, match="at most 10,000 characters"):
        word_tokenize_nbest("ก" * 10_001)


def test_model_loads_once_across_threads(monkeypatch):
    loads = []
    segmenter = latte.Segmenter
    monkeypatch.setattr(core, "_segmenters", {})
    monkeypatch.setattr(latte, "Segmenter", lambda **kwargs: loads.append(kwargs) or segmenter(**kwargs))
    results = []
    threads = [
        threading.Thread(target=lambda: results.append(word_tokenize("ไปเชียงใหม่")))
        for _ in range(8)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert len(loads) == 1
    assert results == [["ไป", "เชียงใหม่"]] * 8


def test_import_loads_neither_numpy_nor_onnxruntime():
    # they load on the first word tokenization, so the rest of the package starts fast
    code = "import sys, iapp_nlp; print(sorted({'numpy', 'onnxruntime'} & set(sys.modules)))"
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "[]"


def test_cli_prints_words_without_spaces(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["iapp-tokenize", "ผมไป", "เชียงใหม่"])
    cli.main()
    assert capsys.readouterr().out == "ผม | ไป | เชียงใหม่\n"


def test_cli_reads_stdin(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["iapp-tokenize"])
    monkeypatch.setattr(sys, "stdin", io.StringIO("ไปเชียงใหม่\n"))
    cli.main()
    assert capsys.readouterr().out == "ไป | เชียงใหม่\n"


def test_cli_unit(capsys):
    cli.main(["--unit", "long", "เจ้าหน้าที่การศึกษาเปิดเผยว่า"])
    assert capsys.readouterr().out == "เจ้าหน้าที่ | การศึกษา | เปิดเผย | ว่า\n"


def test_cli_rejects_an_unknown_unit(capsys):
    with pytest.raises(SystemExit) as exit_info:
        cli.main(["--unit", "word", "ทดสอบ"])
    assert exit_info.value.code == 2
    assert "invalid choice" in capsys.readouterr().err
