import re

from iapp_nlp import subword_tokenize
from iapp_nlp.tokenizer import tcc_p

# vowels and marks written above or below a consonant; a cluster never starts with one
_ATTACHED_MARK_RE = re.compile("^[ัิ-ฺ็-๎]")


def test_splits_into_thai_character_clusters():
    assert subword_tokenize("ประเทศไทย") == ["ป", "ระ", "เท", "ศ", "ไท", "ย"]
    assert subword_tokenize("ขนมชั้น") == ["ข", "น", "ม", "ชั้น"]
    assert subword_tokenize("พิสูจน์ได้ค่ะ") == ["พิ", "สูจน์", "ได้", "ค่ะ"]
    assert subword_tokenize("ก็ไม่รู้") == ["ก็", "ไม่", "รู้"]


def test_uses_improved_rules():
    # the plain TCC rules split this into "รั" "ฐ"
    assert subword_tokenize("นายกรัฐมนตรี") == ["นา", "ย", "ก", "รัฐ", "ม", "น", "ต", "รี"]


def test_never_starts_a_cluster_with_a_vowel_or_tone_mark():
    text = "เมื่อวานนี้นายกรัฐมนตรีเดินทางไปเชียงใหม่ พิสูจน์ได้ค่ะ ก็ไม่รู้"
    assert not [piece for piece in subword_tokenize(text) if _ATTACHED_MARK_RE.match(piece)]


def test_pieces_add_up_to_the_text():
    text = "ซื้อ iPhone15  ราคา 1,234 บาท\nบรรทัดใหม่\tแท็บ"
    assert "".join(subword_tokenize(text)) == text


def test_non_thai_characters_come_out_one_at_a_time():
    assert subword_tokenize("ซื้อ iPhone15") == ["ซื้อ", " ", "i", "P", "h", "o", "n", "e", "1", "5"]


def test_keep_whitespace_false_drops_only_spaces():
    assert subword_tokenize("ไป มา\nแล้ว", keep_whitespace=False) == ["ไป", "มา", "\n", "แล้", "ว"]


def test_empty_string():
    assert subword_tokenize("") == []
    assert tcc_p.segment("") == []
