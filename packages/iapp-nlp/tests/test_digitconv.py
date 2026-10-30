"""Numbers and digits: the bahttext / num_to_thaiword / digit checks from
PyThaiNLP's tests/core/test_util.py::test_number (commit 8fe2ab7d), Apache
License 2.0. Checks of thaiword_to_num, text_to_num and words_to_num are left
out until those functions are added.
"""

import unittest

from iapp_nlp.util import (
    arabic_digit_to_thai_digit,
    bahttext,
    digit_to_text,
    num_to_thaiword,
    num_to_thaiword_float,
    text_to_arabic_digit,
    text_to_thai_digit,
    thai_digit_to_arabic_digit,
)


class NumberTestCase(unittest.TestCase):
    def test_number(self):
        self.assertEqual(bahttext(5611116.5), 'ห้าล้านหกแสนหนึ่งหมื่นหนึ่งพันหนึ่งร้อยสิบหกบาทห้าสิบสตางค์')
        self.assertEqual(bahttext(116), 'หนึ่งร้อยสิบหกบาทถ้วน')
        self.assertEqual(bahttext(0), 'ศูนย์บาทถ้วน')
        with self.assertRaises(TypeError):
            bahttext(None)
        self.assertEqual(bahttext(-100), 'ลบหนึ่งร้อยบาทถ้วน')
        self.assertEqual(bahttext(-50.5), 'ลบห้าสิบบาทห้าสิบสตางค์')
        self.assertIsNotNone(bahttext(999999999999))
        self.assertEqual(bahttext(0.01), 'ศูนย์บาทหนึ่งสตางค์')
        self.assertEqual(bahttext(0.99), 'ศูนย์บาทเก้าสิบเก้าสตางค์')
        self.assertEqual(bahttext(1.0), 'หนึ่งบาทถ้วน')
        self.assertEqual(num_to_thaiword_float(123.45), 'หนึ่งร้อยยี่สิบสามจุดสี่ห้า')
        self.assertEqual(num_to_thaiword_float(0.5), 'ศูนย์จุดห้า')
        self.assertEqual(num_to_thaiword_float(123.12345), 'หนึ่งร้อยยี่สิบสามจุดหนึ่งสองสามสี่ห้า')
        self.assertEqual(num_to_thaiword_float(3.14159), 'สามจุดหนึ่งสี่หนึ่งห้าเก้า')
        self.assertEqual(num_to_thaiword_float(10.01), 'สิบจุดศูนย์หนึ่ง')
        self.assertEqual(num_to_thaiword_float(1001.001), 'หนึ่งพันเอ็ดจุดศูนย์ศูนย์หนึ่ง')
        self.assertEqual(num_to_thaiword_float(0.1), 'ศูนย์จุดหนึ่ง')
        self.assertEqual(num_to_thaiword_float(11.11), 'สิบเอ็ดจุดหนึ่งหนึ่ง')
        self.assertEqual(num_to_thaiword_float(1.0), 'หนึ่ง')
        self.assertEqual(num_to_thaiword_float(0.0), 'ศูนย์')
        self.assertEqual(num_to_thaiword_float(5000000.0), 'ห้าล้าน')
        self.assertEqual(num_to_thaiword_float(-3.14), 'ลบสามจุดหนึ่งสี่')
        self.assertEqual(num_to_thaiword_float(-0.5), 'ลบศูนย์จุดห้า')
        self.assertEqual(num_to_thaiword_float(1e-05), 'ศูนย์จุดศูนย์ศูนย์ศูนย์ศูนย์หนึ่ง')
        self.assertEqual(num_to_thaiword_float(1.23e-10), 'ศูนย์จุดศูนย์ศูนย์ศูนย์ศูนย์ศูนย์ศูนย์ศูนย์ศูนย์ศูนย์หนึ่งสองสาม')
        self.assertEqual(num_to_thaiword_float(0.001), 'ศูนย์จุดศูนย์ศูนย์หนึ่ง')
        self.assertEqual(num_to_thaiword_float(100.0001), 'หนึ่งร้อยจุดศูนย์ศูนย์ศูนย์หนึ่ง')
        self.assertEqual(num_to_thaiword_float(1.23456789), 'หนึ่งจุดสองสามสี่ห้าหกเจ็ดแปดเก้า')
        self.assertEqual(num_to_thaiword_float(1000000000.5), 'หนึ่งพันล้านจุดห้า')
        self.assertEqual(num_to_thaiword_float(42), 'สี่สิบสอง')
        self.assertEqual(num_to_thaiword_float(-99), 'ลบเก้าสิบเก้า')
        self.assertEqual(num_to_thaiword_float(-0.0), 'ศูนย์')
        self.assertEqual(num_to_thaiword_float(1000000000.0), 'หนึ่งพันล้าน')
        with self.assertRaises(TypeError):
            num_to_thaiword_float(None)
        with self.assertRaises(TypeError):
            num_to_thaiword_float('not a number')
        self.assertEqual(num_to_thaiword(None), '')
        self.assertEqual(num_to_thaiword(0), 'ศูนย์')
        self.assertEqual(num_to_thaiword(112), 'หนึ่งร้อยสิบสอง')
        self.assertEqual(num_to_thaiword(-273), 'ลบสองร้อยเจ็ดสิบสาม')
        self.assertEqual(num_to_thaiword(1), 'หนึ่ง')
        self.assertEqual(num_to_thaiword(-1), 'ลบหนึ่ง')
        self.assertEqual(num_to_thaiword(101), 'หนึ่งร้อยเอ็ด')
        self.assertEqual(num_to_thaiword(1001), 'หนึ่งพันเอ็ด')
        self.assertEqual(num_to_thaiword(1000001), 'หนึ่งล้านเอ็ด')
        self.assertEqual(num_to_thaiword(11000000), 'สิบเอ็ดล้าน')
        self.assertEqual(num_to_thaiword(21000000), 'ยี่สิบเอ็ดล้าน')
        self.assertEqual(num_to_thaiword(11000001), 'สิบเอ็ดล้านเอ็ด')
        self.assertEqual(num_to_thaiword(501741221), 'ห้าร้อยเอ็ดล้านเจ็ดแสนสี่หมื่นหนึ่งพันสองร้อยยี่สิบเอ็ด')
        self.assertEqual(num_to_thaiword(6001461300), 'หกพันเอ็ดล้านสี่แสนหกหมื่นหนึ่งพันสามร้อย')
        self.assertEqual(num_to_thaiword(10), 'สิบ')
        self.assertEqual(num_to_thaiword(20), 'ยี่สิบ')
        self.assertEqual(num_to_thaiword(100), 'หนึ่งร้อย')
        self.assertEqual(num_to_thaiword(1000), 'หนึ่งพัน')
        self.assertEqual(num_to_thaiword(10000), 'หนึ่งหมื่น')
        self.assertEqual(num_to_thaiword(100000), 'หนึ่งแสน')
        self.assertEqual(num_to_thaiword(111111), 'หนึ่งแสนหนึ่งหมื่นหนึ่งพันหนึ่งร้อยสิบเอ็ด')
        self.assertEqual(num_to_thaiword(1000000000), 'หนึ่งพันล้าน')
        self.assertEqual(num_to_thaiword(1000000000000), 'หนึ่งล้านล้าน')
        self.assertEqual(num_to_thaiword(10000000), 'สิบล้าน')
        self.assertEqual(num_to_thaiword(101000000), 'หนึ่งร้อยเอ็ดล้าน')
        self.assertEqual(num_to_thaiword(-1000001), 'ลบหนึ่งล้านเอ็ด')
        self.assertEqual(num_to_thaiword(-11000000), 'ลบสิบเอ็ดล้าน')
        self.assertEqual(num_to_thaiword(-0), 'ศูนย์')
        self.assertEqual(arabic_digit_to_thai_digit('ไทยแลนด์ 4.0'), 'ไทยแลนด์ ๔.๐')
        self.assertEqual(arabic_digit_to_thai_digit(''), '')
        with self.assertRaises(TypeError):
            arabic_digit_to_thai_digit(None)
        self.assertEqual(thai_digit_to_arabic_digit('๔๐๔ Not Found'), '404 Not Found')
        self.assertEqual(thai_digit_to_arabic_digit(''), '')
        with self.assertRaises(TypeError):
            thai_digit_to_arabic_digit(None)
        self.assertEqual(digit_to_text('RFC 7258'), 'RFC เจ็ดสองห้าแปด')
        self.assertEqual(digit_to_text(''), '')
        with self.assertRaises(TypeError):
            digit_to_text(None)
        self.assertEqual(text_to_arabic_digit('เจ็ด'), '7')
        self.assertEqual(text_to_arabic_digit(''), '')
        with self.assertRaises(TypeError):
            text_to_arabic_digit(None)
        self.assertEqual(text_to_thai_digit('เก้า'), '๙')
        self.assertEqual(text_to_thai_digit(''), '')
        with self.assertRaises(TypeError):
            text_to_thai_digit(None)
