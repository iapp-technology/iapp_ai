"""normalize: cases from PyThaiNLP's own tests, plus typos seen in Thai chat text.

The (input, expected) pairs come from PyThaiNLP's ``tests/core/test_util.py``
(commit 8fe2ab7d), Apache License 2.0; the comment on each names the PyThaiNLP
function it tested there and its line. All of them hold through ``normalize``.
"""

import pytest

from iapp_nlp import normalize

PYTHAINLP_CASES = [
    ('เเปลก', 'แปลก'),  # normalize, line 615
    ('นํา', 'นำ'),  # normalize, line 618
    ('กํา', 'กำ'),  # normalize, line 619
    ('ก่ํา', 'ก่ำ'),  # normalize, line 622
    ('กะ่', 'ก่ะ'),  # normalize, line 627
    ('กํ่า', 'ก่ำ'),  # normalize, line 630
    ('กา่', 'ก่า'),  # normalize, line 635
    ('นๅคา', 'นาคา'),  # normalize, line 638
    ('ฤๅษี', 'ฤๅษี'),  # normalize, line 639
    ('กาา', 'กา'),  # normalize, line 642
    ('กา า  า  า', 'กา'),  # normalize, line 643
    ('กา าาะา', 'กาะา'),  # normalize, line 644
    ('ก่่', 'ก่'),  # normalize, line 647
    ('ก่้', 'ก้'),  # normalize, line 650
    ('ก่้่้', 'ก้'),  # normalize, line 651
    ('\u0e48ก', 'ก'),  # remove_dangling, line 656
    ('\u0e48\u0e48ก', 'ก'),  # remove_dangling, line 657
    ('\u0e48\u0e49ก', 'ก'),  # remove_dangling, line 658
    ('\u0e48ก\u0e48', 'ก่'),  # remove_dangling, line 659
    ('พ ุ่มดอกไม้', 'พุ่มดอกไม้'),  # normalize, line 662
    ('เค\u0e49\u0e49\u0e49\u0e32เด\u0e34นไปสน\u0e32มหญ\u0e32\u0e49หน\u0e32\u0e49บ\u0e32\u0e49น', 'เค\u0e49\u0e32เด\u0e34นไปสน\u0e32มหญ\u0e49\u0e32หน\u0e49\u0e32บ\u0e49\u0e32น'),  # normalize, line 663
    ('พ ุ่มดอกไม้ในสนามหญา้หนา้บา้น', 'พุ่มดอกไม้ในสนามหญ้าหน้าบ้าน'),  # normalize, line 667
    ('ก ิ', 'กิ'),  # normalize, line 671
    ('ก ุ', 'กุ'),  # normalize, line 672
    ('ก  ้า', 'ก้า'),  # normalize, line 673
    ('  ab  c d  ', 'ab c d'),  # remove_dup_spaces, line 678
    ('\nab  c   \n d \n', 'ab c\nd'),  # remove_dup_spaces, line 679
    ('ก\u0e32\u200b', 'กา'),  # remove_zw, line 686
    ('ก\u200c\u0e32', 'กา'),  # remove_zw, line 687
    ('\u200bก\u0e32', 'กา'),  # remove_zw, line 688
    ('ก\u0e32\u200b\u200c\u200b', 'กา'),  # remove_zw, line 689
    ('', ''),  # remove_repeat_vowels, line 1307
    ('สวัสดี', 'สวัสดี'),  # remove_repeat_vowels, line 1308
    ('นานาา', 'นานา'),  # remove_repeat_vowels, line 1309
    ('ดีีีี', 'ดี'),  # remove_repeat_vowels, line 1310
    ('เเปลก', 'แปลก'),  # remove_repeat_vowels, line 1312
    ('', ''),  # remove_spaces_before_marks, line 1315
    ('กิน', 'กิน'),  # remove_spaces_before_marks, line 1316
    ('ก ิ', 'กิ'),  # remove_spaces_before_marks, line 1317
    ('ก ุ', 'กุ'),  # remove_spaces_before_marks, line 1318
    ('ก ่า', 'ก่า'),  # remove_spaces_before_marks, line 1319
    ('', ''),  # reorder_vowels, line 1324
    ('สวัสดี', 'สวัสดี'),  # reorder_vowels, line 1325
    ('เเปลก', 'แปลก'),  # reorder_vowels, line 1327
    ('กํา', 'กำ'),  # reorder_vowels, line 1329
]


@pytest.mark.parametrize("text, expected", PYTHAINLP_CASES)
def test_matches_pythainlp(text, expected):
    assert normalize(text) == expected


def test_fixes_repeated_and_misordered_marks():
    assert normalize("แล้้ว") == "แล้ว"
    assert normalize("ท่ี") == "ที่"
    assert normalize("นั้้น") == "นั้น"


def test_leaves_misspelled_letters_alone():
    # only marks are fixed; wrong letters need a spell checker
    assert normalize("มี่") == "มี่"


def test_ascii_text_is_unchanged():
    assert normalize("Hello, world!") == "Hello, world!"
