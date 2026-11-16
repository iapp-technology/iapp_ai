# SPDX-License-Identifier: Apache-2.0
"""Behaviour of the OpenThai2.0-LATTE-WordSeg-Lite runtime: its tests/test_basic.py, importing from iapp_nlp."""
import hashlib
import json
import warnings

import pytest

from iapp_nlp import Tokenizer, word_tokenize
from iapp_nlp.tokenizer import latte
from iapp_nlp.tokenizer.latte import Segmenter

ASSETS = latte.ASSETS


@pytest.fixture(scope="module")
def seg():
    return Segmenter()


def test_thai_sentence(seg):
    assert seg.tokenize("ฉันกินข้าวที่บ้าน") == ["ฉัน", "กิน", "ข้าว", "ที่", "บ้าน"]


@pytest.mark.parametrize("text", ["", " ", "   ", "\n", "\n\n", " \n ", "\t"])
def test_empty_and_whitespace(seg, text):
    toks = seg.tokenize(text)
    assert "".join(toks) == text
    assert all(t.isspace() for t in toks) and all(len(t) == 1 for t in toks)
    assert seg.tokenize(text, keep_whitespace=False) == []


@pytest.mark.parametrize("text", ["ราคา 41,900 บาท 😀😀 ดีมาก!!", "ข้อความ\nสองบรรทัด\r\nและ\tแท็บ",
                                  "a\ud800b ทดสอบ", "ไทย𝕏𝟘ภาษา", "ๆๆๆ", "ก", "a"])
def test_lossless(seg, text):
    assert "".join(seg.tokenize(text)) == text


def test_latin_and_digit_runs_are_never_split(seg):
    toks = seg.tokenize("ดาวน์โหลดinternationalizationที่github.comเวอร์ชัน20261113")
    for run in ("internationalization", "github", "com", "20261113"):
        assert any(run in t for t in toks), (run, toks)


def test_thai_digit_runs_are_never_split(seg):
    assert seg.tokenize("เลขที่๑๐๙๘๗๖") == ["เลข", "ที่", "๑๐๙๘๗๖"]    # 0.1.1 gave ๑๐ ๙๘๗๖


def test_whitespace_tokens(seg):
    assert seg.tokenize("ไป  ไหน") == ["ไป", " ", " ", "ไหน"]
    assert seg.tokenize("ไป  ไหน", keep_whitespace=False) == ["ไป", "ไหน"]


def test_batch_matches_single_calls_line_by_line():
    seg = Segmenter(batch_chars=0)                  # one line per batch: independent of other texts
    texts = ["ฉันกินข้าวที่บ้าน", "วันนี้อากาศดีมาก", "", "ประเทศไทยมีพื้นที่ประมาณห้าแสนตารางกิโลเมตร"]
    assert seg.tokenize_batch(texts) == [seg.tokenize(t) for t in texts]


def test_deterministic(seg):
    text = "การประชุมครั้งนี้มีผู้เข้าร่วมกว่าหนึ่งพันคนจากทั่วประเทศ"
    assert all(seg.tokenize(text) == seg.tokenize(text) for _ in range(3))


def test_module_level_functions():
    assert word_tokenize("สวัสดีครับ", keep_whitespace=False) == ["สวัสดี", "ครับ"]
    assert Tokenizer().word_tokenize_batch(["สวัสดี", "ขอบคุณ"]) == [["สวัสดี"], ["ขอบคุณ"]]


def test_user_words_reach_the_dictionary(seg):
    custom = Segmenter(user_words=["ไอแอพพ์"])
    assert custom.lexicon.size == seg.lexicon.size + 1


def test_shipped_files_match_the_manifest():
    manifest = json.loads((ASSETS / "manifest.json").read_text(encoding="utf-8"))
    model = manifest["model"]
    for name, digest in {model["file"]: model["sha256"], **manifest["files_sha256"]}.items():
        assert hashlib.sha256((ASSETS / name).read_bytes()).hexdigest() == digest, name
    assert [p.name for p in ASSETS.glob("*.onnx")] == [model["file"]]          # one model only


# ---------------------------------------------------------------- units
UNIT_TEXTS = ["การศึกษาของเจ้าหน้าที่คณะกรรมการการเลือกตั้งเมื่อวานนี้", "ฉันกินข้าวที่บ้าน",
              "ผลกระทบต่อความสัมพันธ์ระหว่างประเทศไทยกับญี่ปุ่น", "วันนี้อากาศดีจริงๆ 555", "", "ก"]


def _starts(tokens):
    pos, out = 0, set()
    for t in tokens:
        out.add(pos)
        pos += len(t)
    return out


def test_three_units(seg):
    assert seg.units == ["long", "short", "minimal"]
    assert seg.unnested_units == ["minimal"]


@pytest.mark.parametrize("text", UNIT_TEXTS)
def test_units_are_nested(seg, text):
    nested = [u for u in seg.units if u not in seg.unnested_units]          # coarse to fine
    starts = [_starts(seg.tokenize(text, unit=u)) for u in nested]
    for coarse, fine in zip(starts, starts[1:]):
        assert coarse <= fine
    for u in seg.units:
        assert "".join(seg.tokenize(text, unit=u)) == text


def test_finer_units_split_more(seg):
    """Each unit splits the test texts at least as often as the next coarser one (on the whole set)."""
    counts = [sum(len(seg.tokenize(t, unit=u, keep_whitespace=False)) for t in UNIT_TEXTS) for u in seg.units]
    assert counts == sorted(counts)


def test_default_unit_is_short(seg):
    assert seg.unit == "short"
    assert all(seg.tokenize(t) == seg.tokenize(t, unit="short") for t in UNIT_TEXTS)


def test_unknown_unit(seg):
    with pytest.raises(ValueError):
        seg.tokenize("ทดสอบ", unit="paragraph")
    with pytest.raises(ValueError):
        Segmenter(unit="paragraph")
    for working_name in ("large", "word", "sub"):          # the names of the training runs are not unit names
        with pytest.raises(ValueError):
            seg.tokenize("ทดสอบ", unit=working_name)


# The examples of README.md (the model card): change both together when the model changes. Each was chosen with
# a clear margin (|logit| >= 0.7 at every possible boundary), so that small numeric differences between CPUs or
# ONNX Runtime versions are unlikely to flip them.
MODEL_CARD = {
    "แม่น้ำเจ้าพระยาไหลผ่านกรุงเทพ": ("แม่น้ำ|เจ้าพระยา|ไหล|ผ่าน|กรุงเทพ", "แม่น้ำ|เจ้าพระยา|ไหล|ผ่าน|กรุงเทพ",
                                     "แม่|น้ำ|เจ้า|พระยา|ไหล|ผ่าน|กรุง|เทพ"),
    "เจ้าหน้าที่การศึกษาเปิดเผยว่า": ("เจ้าหน้าที่|การศึกษา|เปิดเผย|ว่า", "เจ้า|หน้าที่|การ|ศึกษา|เปิด|เผย|ว่า",
                                     "เจ้า|หน้า|ที่|การ|ศึกษา|เปิด|เผย|ว่า"),
    "ข้อ 1. (ก) ทดสอบ": ("ข้อ|1|.|(|ก|)|ทดสอบ", "ข้อ|1|.|(|ก|)|ทดสอบ", "ข้อ|1.|(ก)|ทด|สอบ"),
    "iPhone15 ราคา 2,552.24 บาท ที่ www.google.com": ("iPhone|15|ราคา|2,552.24|บาท|ที่|www.google.com",) * 3,
    "ข้อ 4.1 ระบุว่า": ("ข้อ|4|.|1|ระบุ|ว่า", "ข้อ|4|.|1|ระบุ|ว่า", "ข้อ|4.1|ระบุ|ว่า"),
}


@pytest.mark.parametrize("text", MODEL_CARD)
def test_model_card_examples(seg, text):
    for unit, expected in zip(("long", "short", "minimal"), MODEL_CARD[text]):
        assert "|".join(seg.tokenize(text, keep_whitespace=False, unit=unit)) == expected, unit


# ------------------------------------------------------------------ several readings (tokenize_nbest)
@pytest.mark.parametrize("text", ["ฉันกินข้าวที่บ้าน", "เจ้าหน้าที่การศึกษาเปิดเผยว่า", "ตากลม",
                                  "ราคา 41,900 บาท iPhone15 ดีมาก", "สองบรรทัด\nบรรทัดที่สอง"])
@pytest.mark.parametrize("unit", ["long", "short", "minimal"])
def test_nbest_starts_with_tokenize(seg, text, unit):
    ranked = seg.tokenize_nbest(text, 5, unit)
    assert ranked[0][0] == seg.tokenize(text, unit=unit)
    assert 1 <= len(ranked) <= 5
    assert all("".join(toks) == text for toks, _ in ranked)
    assert len({tuple(toks) for toks, _ in ranked}) == len(ranked)
    probs = [p for _, p in ranked]
    assert all(0.0 < p <= 1.0 for p in probs) and probs[1:] == sorted(probs[1:], reverse=True)


@pytest.mark.parametrize("text, readings", [
    ("ตากลม", [["ตา", "กลม"], ["ตาก", "ลม"]]),
    ("ไปหามเหสี", [["ไป", "หา", "มเหสี"], ["ไป", "หาม", "เหสี"]]),
    ("คนขับรถ", [["คนขับ", "รถ"], ["คน", "ขับ", "รถ"]]),
])
def test_nbest_finds_both_readings(seg, text, readings):
    found = [toks for toks, _ in seg.tokenize_nbest(text, 5)]
    for reading in readings:
        assert reading in found, (reading, found)


def test_nbest_keeps_spaces_and_runs(seg):
    for toks, _ in seg.tokenize_nbest("ตากลม iPhone 15 ไปหามเหสี", 8):
        assert "iPhone" in toks and "15" in toks and toks.count(" ") == 3
    assert all(" " not in toks for toks, _ in seg.tokenize_nbest("ตากลม iPhone", 3, keep_whitespace=False))


@pytest.mark.parametrize("text, expected", [("", []), (" ", [" "]), ("\n\t", ["\n", "\t"])])
def test_nbest_empty(seg, text, expected):
    assert seg.tokenize_nbest(text) == [(expected, 1.0)]


def test_nbest_rejects_n_below_one(seg):
    with pytest.raises(ValueError):
        seg.tokenize_nbest("ตากลม", 0)


def test_nbest_takom_order(seg):
    # the example of the post card (docs/sns/make_card.py checks this line)
    assert [t for t, _ in seg.tokenize_nbest("ตากลม", 3)] == [["ตา", "กลม"], ["ตากลม"], ["ตาก", "ลม"]]


# ---------------------------------------------------------------- 0.1.1: long lines, input checks, limits
PHRASES = ["เจ้าหน้าที่การศึกษาเปิดเผยว่า", "ฉันกินข้าวที่บ้านแล้วไปทำงานต่อ", "ประเทศไทยมีพื้นที่ประมาณห้าแสนตารางกิโลเมตร",
           "การประชุมครั้งนี้มีผู้เข้าร่วมกว่าหนึ่งพันคนจากทั่วประเทศ", "วันนี้อากาศดีมาก", "แม่น้ำเจ้าพระยาไหลผ่านกรุงเทพ"]
LONG = "".join(PHRASES[i % len(PHRASES)] for i in range(60))        # 2,050 characters, no whitespace


@pytest.mark.parametrize("unit", ["long", "short", "minimal"])
def test_long_lines_in_windows_match_the_whole_line(seg, monkeypatch, unit):
    whole = seg.tokenize(LONG, unit=unit)
    monkeypatch.setattr(latte, "MAX_WINDOW", 300)            # nine windows instead of one line
    monkeypatch.setattr(latte, "WINDOW_CONTEXT", 100)
    assert len(latte._windows(len(LONG))) > 1
    assert seg.tokenize(LONG, unit=unit) == whole


def test_windows_tile_the_line():
    for n in (0, 1, 9_999, 10_000, 10_001, 25_000, 1_000_000):
        w = latte._windows(n)
        assert w[0][2] == 0 and w[-1][3] == n
        assert all(a[3] == b[2] for a, b in zip(w, w[1:]))           # the kept parts tile the line
        for start, end, keep_from, keep_to in w:
            assert end - start <= latte.MAX_WINDOW
            assert start == 0 or keep_from - start >= latte.WINDOW_CONTEXT
            assert end == n or end - keep_to >= latte.WINDOW_CONTEXT


@pytest.mark.parametrize("bad", [None, 42, "ไทย".encode(), ["ไทย"]])
def test_text_must_be_a_string(seg, bad):
    with pytest.raises(TypeError):
        seg.tokenize(bad)
    with pytest.raises(TypeError):
        seg.tokenize_nbest(bad)
    with pytest.raises(TypeError):
        seg.tokenize_batch(["ไทย", bad])


def test_batch_takes_a_list_not_one_string(seg):
    with pytest.raises(TypeError):
        seg.tokenize_batch("ไทย")
    lines = ["ฉันกินข้าว", "ที่บ้าน"]
    assert seg.tokenize_batch(t for t in lines) == seg.tokenize_batch(lines)    # any iterable, read once


def test_user_words_the_dictionary_cannot_hold_warn(seg):
    with pytest.warns(UserWarning, match="2 of the user words not used"):
        custom = Segmenter(user_words=["ก", "ไทยแลนด์ฟู้ดเฟสติวัล", " บราวน์ชูการ์ ", ""])
    assert "บราวน์ชูการ์" in custom.tokenize("ฉันชอบกินบราวน์ชูการ์ร้านนี้มาก")
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert Segmenter(user_words=None).lexicon.size == seg.lexicon.size
        Segmenter(user_words=["ไอแอพพ์"])
    with pytest.raises(TypeError):
        Segmenter(user_words="บราวน์ชูการ์")                       # one string, not a list of words


def test_nbest_limits(seg):
    with pytest.raises(ValueError):
        seg.tokenize_nbest("ตากลม", latte.MAX_NBEST + 1)
    with pytest.raises(ValueError):
        seg.tokenize_nbest("ก" * (latte.MAX_NBEST_CHARS + 1))
