# SPDX-FileCopyrightText: 2016-2026 PyThaiNLP Project
# SPDX-FileContributor: iApp Technology
# SPDX-License-Identifier: Apache-2.0
"""Tests for normalize, plus typos seen in Thai chat text.

The comment on each case names the normalization step it checks.
"""

import pytest

from iapp_nlp import normalize

CASES = [
    ('เเปลก', 'แปลก'),  # normalize
    ('นํา', 'นำ'),  # normalize
    ('กํา', 'กำ'),  # normalize
    ('ก่ํา', 'ก่ำ'),  # normalize
    ('กะ่', 'ก่ะ'),  # normalize
    ('กํ่า', 'ก่ำ'),  # normalize
    ('กา่', 'ก่า'),  # normalize
    ('นๅคา', 'นาคา'),  # normalize
    ('ฤๅษี', 'ฤๅษี'),  # normalize
    ('กาา', 'กา'),  # normalize
    ('กา า  า  า', 'กา'),  # normalize
    ('กา าาะา', 'กาะา'),  # normalize
    ('ก่่', 'ก่'),  # normalize
    ('ก่้', 'ก้'),  # normalize
    ('ก่้่้', 'ก้'),  # normalize
    ('\u0e48ก', 'ก'),  # remove_dangling
    ('\u0e48\u0e48ก', 'ก'),  # remove_dangling
    ('\u0e48\u0e49ก', 'ก'),  # remove_dangling
    ('\u0e48ก\u0e48', 'ก่'),  # remove_dangling
    ('พ ุ่มดอกไม้', 'พุ่มดอกไม้'),  # normalize
    ('เค\u0e49\u0e49\u0e49\u0e32เด\u0e34นไปสน\u0e32มหญ\u0e32\u0e49หน\u0e32\u0e49บ\u0e32\u0e49น', 'เค\u0e49\u0e32เด\u0e34นไปสน\u0e32มหญ\u0e49\u0e32หน\u0e49\u0e32บ\u0e49\u0e32น'),  # normalize
    ('พ ุ่มดอกไม้ในสนามหญา้หนา้บา้น', 'พุ่มดอกไม้ในสนามหญ้าหน้าบ้าน'),  # normalize
    ('ก ิ', 'กิ'),  # normalize
    ('ก ุ', 'กุ'),  # normalize
    ('ก  ้า', 'ก้า'),  # normalize
    ('  ab  c d  ', 'ab c d'),  # remove_dup_spaces
    ('\nab  c   \n d \n', 'ab c\nd'),  # remove_dup_spaces
    ('ก\u0e32\u200b', 'กา'),  # remove_zw
    ('ก\u200c\u0e32', 'กา'),  # remove_zw
    ('\u200bก\u0e32', 'กา'),  # remove_zw
    ('ก\u0e32\u200b\u200c\u200b', 'กา'),  # remove_zw
    ('', ''),  # remove_repeat_vowels
    ('สวัสดี', 'สวัสดี'),  # remove_repeat_vowels
    ('นานาา', 'นานา'),  # remove_repeat_vowels
    ('ดีีีี', 'ดี'),  # remove_repeat_vowels
    ('เเปลก', 'แปลก'),  # remove_repeat_vowels
    ('', ''),  # remove_spaces_before_marks
    ('กิน', 'กิน'),  # remove_spaces_before_marks
    ('ก ิ', 'กิ'),  # remove_spaces_before_marks
    ('ก ุ', 'กุ'),  # remove_spaces_before_marks
    ('ก ่า', 'ก่า'),  # remove_spaces_before_marks
    ('', ''),  # reorder_vowels
    ('สวัสดี', 'สวัสดี'),  # reorder_vowels
    ('เเปลก', 'แปลก'),  # reorder_vowels
    ('กํา', 'กำ'),  # reorder_vowels
]


@pytest.mark.parametrize("text, expected", CASES)
def test_cases(text, expected):
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
