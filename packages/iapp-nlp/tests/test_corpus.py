"""thai_stopwords and provinces; the checks follow PyThaiNLP's tests/core/test_corpus.py (commit 8fe2ab7d)."""

import pytest

from iapp_nlp.corpus import common, provinces, thai_stopwords


def test_thai_stopwords():
    words = thai_stopwords()
    assert isinstance(words, frozenset)
    assert len(words) == 1030
    assert {"มี", "ไป", "ขณะ", "การ", "ประการหนึ่ง"} <= words


def test_thai_stopwords_drop_the_leading_byte_order_mark():
    # the file starts with a BOM before "ณ"
    assert "ณ" in thai_stopwords()


def test_thai_stopwords_keep_the_stray_byte_order_mark_like_pythainlp():
    # line 40 of the file is "\ufeffๆ", a second BOM; PyThaiNLP keeps it as an
    # extra entry next to the real "ๆ", so this list does the same
    assert {"ๆ", "\ufeffๆ"} <= thai_stopwords()
    assert [word for word in thai_stopwords() if "\ufeff" in word] == ["\ufeffๆ"]


def test_provinces():
    names = provinces()
    rows = provinces(details=True)
    assert isinstance(names, frozenset)
    assert isinstance(rows, list)
    assert len(names) == len(rows) == 77
    assert {"กระบี่", "กรุงเทพมหานคร", "อุบลราชธานี"} <= names
    assert {"name_th": "นนทบุรี", "abbr_th": "นบ", "name_en": "Nonthaburi", "abbr_en": "NBI"} in rows


@pytest.fixture
def fake_province_file(monkeypatch):
    """Point provinces() at the given lines, with an empty cache."""
    def use(lines):
        monkeypatch.setattr(common, "_provinces", frozenset())
        monkeypatch.setattr(common, "_province_details", [])
        monkeypatch.setattr(common, "_read_lines", lambda filename: lines)
    return use


@pytest.mark.parametrize(
    "line, message",
    [
        ("กรุงเทพ,กทม", "too few fields"),
        ("กรุงเทพ,,Bangkok,BKK", "blank or empty field"),
    ],
)
def test_provinces_skip_bad_lines_with_a_warning(fake_province_file, line, message):
    fake_province_file([line])
    with pytest.warns(UserWarning, match=message):
        assert provinces() == frozenset()


def test_provinces_skip_blank_lines_silently(fake_province_file, recwarn):
    fake_province_file(["", "   ", "กระบี่,กบ,Krabi,KBI"])
    assert provinces() == frozenset({"กระบี่"})
    assert not recwarn.list
