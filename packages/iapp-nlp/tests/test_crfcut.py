import threading

from iapp_nlp import sent_tokenize
from iapp_nlp.tokenizer import crfcut


def test_model_finds_sentence_ends_inside_one_line():
    text = "ฉันไปประชุมเมื่อวันที่ 11 มีนาคม แล้วกลับบ้านตอนเย็น วันนี้อากาศดีมาก ฉันจึงออกไปวิ่งที่สวน"
    assert sent_tokenize(text) == [
        "ฉันไปประชุมเมื่อวันที่ 11 มีนาคม แล้วกลับบ้านตอนเย็น ",
        "วันนี้อากาศดีมาก ",
        "ฉันจึงออกไปวิ่งที่สวน",
    ]


def test_keep_whitespace_false_trims_spaces():
    assert sent_tokenize("หิวข้าวมากๆ แต่ไม่รู้จะกินอะไรดี", keep_whitespace=False) == [
        "หิวข้าวมากๆ", "แต่ไม่รู้จะกินอะไรดี",
    ]


def test_terminal_punctuation_ends_a_sentence():
    assert sent_tokenize("สวัสดีครับ! วันนี้ว่างไหม? ไปเที่ยวกัน", keep_whitespace=False) == [
        "สวัสดีครับ!", "วันนี้ว่างไหม?", "ไปเที่ยวกัน",
    ]


def test_new_line_ends_a_sentence():
    assert sent_tokenize("บริษัทเปิดตัวสินค้าใหม่วันนี้\nราคาเริ่มต้น 999 บาท") == [
        "บริษัทเปิดตัวสินค้าใหม่วันนี้\n", "ราคาเริ่มต้น 999 บาท",
    ]


def test_blank_lines_stay_on_a_sentence():
    assert sent_tokenize("บรรทัดหนึ่ง\n\nบรรทัดสาม\n") == ["บรรทัดหนึ่ง\n\n", "บรรทัดสาม\n"]
    assert sent_tokenize("\n\nขึ้นต้นด้วยบรรทัดว่าง") == ["\n\nขึ้นต้นด้วยบรรทัดว่าง"]


def test_no_text_is_lost():
    texts = ["ว่างไหม?\nไปกัน ", "สวัสดีครับ! ", "   ", "\n", "ดร.สมชาย ไปประชุมที่ กทม. เมื่อวาน\n\n"]
    for text in texts:
        assert "".join(sent_tokenize(text)) == text


def test_abbreviations_end_a_sentence_like_pythainlp():
    # known issue kept on purpose: every word ending in "." ends a sentence, abbreviations too
    assert sent_tokenize("ดร.สมชาย ไปประชุมที่ กทม. เมื่อวาน", keep_whitespace=False) == [
        "ดร.", "สมชาย ไปประชุมที่ กทม.", "เมื่อวาน",
    ]


def test_empty_and_space_only_text():
    assert sent_tokenize("") == []
    assert sent_tokenize("   ", keep_whitespace=False) == []
    assert crfcut.segment("") == []


def test_tagger_is_shared_safely_across_threads():
    text = "หิวข้าวมากๆ แต่ไม่รู้จะกินอะไรดี วันนี้อากาศดีมาก ฉันจึงออกไปวิ่งที่สวน " * 20
    expected = sent_tokenize(text)
    results = []
    threads = [threading.Thread(target=lambda: results.append(sent_tokenize(text))) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert results == [expected] * 8
