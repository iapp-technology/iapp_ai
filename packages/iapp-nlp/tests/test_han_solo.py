import threading

from iapp_nlp import syllable_tokenize
from iapp_nlp.tokenizer import han_solo


def test_splits_formal_text_into_syllables():
    assert syllable_tokenize("นายกรัฐมนตรีเดินทางไปเชียงใหม่") == [
        "นา", "ยก", "รัฐ", "มน", "ตรี", "เดิน", "ทาง", "ไป", "เชียง", "ใหม่",
    ]
    assert syllable_tokenize("ประเทศไทย") == ["ประ", "เทศ", "ไทย"]


def test_keeps_repeated_letters_of_social_media_text_together():
    assert syllable_tokenize("ม่ายยยย จริงป่าววว อร่อยมากกกก", keep_whitespace=False) == [
        "ม่ายยยย", "จริง", "ป่าววว", "อร่อย", "มากกกก",
    ]


def test_splits_loanwords():
    assert syllable_tokenize("คอมพิวเตอร์ อินเทอร์เน็ต") == [
        "คอม", "พิว", "เตอร์", " ", "อิน", "เทอร์", "เน็ต",
    ]


def test_tabs_and_new_lines_are_pieces_of_their_own():
    assert syllable_tokenize("สวัสดี\nครับ") == ["สวัส", "ดี", "\n", "ครับ"]
    assert syllable_tokenize("ไป\tมา\r\n") == ["ไป", "\t", "มา", "\r\n"]
    assert syllable_tokenize("abc\ndef") == ["abc", "\n", "def"]


def test_pieces_add_up_to_the_text():
    text = "ซื้อ iPhone15ราคา 30000 บาท\n\nม่ายยยย  จริงป่าววว\t55555"
    assert "".join(syllable_tokenize(text)) == text


def test_digits_next_to_thai_split_wrongly():
    # known issue kept on purpose: the model was trained mostly on Thai, see RELEASE_PROGRESS round 7
    assert syllable_tokenize("ซื้อ iPhone15ราคา", keep_whitespace=False) == ["ซื้อ", "iPhone1", "5รา", "คา"]


def test_empty_and_space_only_text():
    assert syllable_tokenize("") == []
    assert syllable_tokenize("   ", keep_whitespace=False) == []


def test_featurizer_makes_one_feature_list_per_character_plus_one():
    assert len(han_solo._to_feature.featurize("สวัสดี")["X"]) == len("สวัสดี") + 1


def test_tagger_is_shared_safely_across_threads():
    text = "นายกรัฐมนตรีเดินทางไปเชียงใหม่ ม่ายยยย จริงป่าววว " * 20
    expected = syllable_tokenize(text)
    results = []
    threads = [threading.Thread(target=lambda: results.append(syllable_tokenize(text))) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert results == [expected] * 8
