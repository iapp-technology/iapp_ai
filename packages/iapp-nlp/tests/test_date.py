# SPDX-FileCopyrightText: 2016-2026 PyThaiNLP Project
# SPDX-FileContributor: iApp Technology
# SPDX-License-Identifier: Apache-2.0
"""Tests for convert_years, reign years, thai_strftime, thai_strptime and thaiword_to_date."""

import hashlib
import unittest
from datetime import datetime, timedelta, timezone
from typing import Any

from iapp_nlp.util import (
    convert_years,
    now_reign_year,
    reign_year_to_ad,
    thai_strftime,
    thai_strptime,
    thaiword_to_date,
)


class DateTestCase(unittest.TestCase):
    def test_date(self):
        self.assertIsNotNone(now_reign_year())
        self.assertEqual(reign_year_to_ad(2, 10), 2017)
        self.assertIsNotNone(reign_year_to_ad(2, 9))
        self.assertIsNotNone(reign_year_to_ad(2, 8))
        self.assertIsNotNone(reign_year_to_ad(2, 7))

    def test_thai_strftime(self):
        date = datetime(1976, 10, 6, 1, 40, tzinfo=timezone.utc)
        self.assertEqual(thai_strftime(date, '%d'), '06')
        self.assertEqual(thai_strftime(date, '%-d'), '6')
        self.assertEqual(thai_strftime(date, '%_d'), ' 6')
        self.assertEqual(thai_strftime(date, '%0d'), '06')
        self.assertEqual(thai_strftime(date, '%H'), '01')
        self.assertEqual(thai_strftime(date, '%-H'), '1')
        self.assertEqual(thai_strftime(date, '%_M'), '40')
        self.assertEqual(thai_strftime(date, '%0M'), '40')
        self.assertEqual(thai_strftime(date, '%e'), ' 6')
        self.assertEqual(thai_strftime(date, '%-e'), '6')
        self.assertEqual(thai_strftime(date, '%_e'), ' 6')
        self.assertEqual(thai_strftime(date, '%0e'), '06')
        self.assertEqual(thai_strftime(date, '%Ed'), '06')
        self.assertEqual(thai_strftime(date, '%Od'), '๐๖')
        self.assertEqual(thai_strftime(date, '%d', thaidigit=True), '๐๖')
        self.assertEqual(thai_strftime(date, '%%'), '%')
        self.assertEqual(thai_strftime(date, '%'), '%')
        self.assertEqual(thai_strftime(date, '%-'), '-')
        self.assertEqual(thai_strftime(date, '%c'), 'พ   6 ต.ค. 01:40:00 2519')
        self.assertEqual(thai_strftime(date, '%0c'), 'พ   6 ต.ค. 01:40:00 2519')
        self.assertEqual(thai_strftime(date, '%c', True), 'พ   ๖ ต.ค. ๐๑:๔๐:๐๐ ๒๕๑๙')
        self.assertEqual(thai_strftime(date, '%Aที่ %d %B พ.ศ. %Y เวลา %H:%Mน. (%a %d-%b-%y) %% %'), 'วันพุธที่ 06 ตุลาคม พ.ศ. 2519 เวลา 01:40น. (พ 06-ต.ค.-19) % %')
        self.assertEqual(thai_strftime(date, '%Q'), 'Q')
        self.assertIsNotNone(thai_strftime(date, '%A%a%B%b%C%c%D%F%G%g%v%X%x%Y%y%+%%'))
        self.assertEqual(thai_strftime(date, '%p').upper(), thai_strftime(date, '%^p'))
        self.assertEqual(thai_strftime(date, '%Z').swapcase(), thai_strftime(date, '%#Z'))
        date = datetime(1, 2, 3)
        self.assertEqual(thai_strftime(date, '%Y'), '0544')
        self.assertEqual(thai_strftime(date, '%y'), '44')
        self.assertEqual(len(thai_strftime(date, '%G')), 4)
        self.assertEqual(len(thai_strftime(date, '%g')), 2)

    def test_thaiword_to_date(self):
        now = datetime.now()
        self.assertEqual(now + timedelta(days=0), thaiword_to_date('วันนี้', now))
        self.assertEqual(now + timedelta(days=1), thaiword_to_date('พรุ่งนี้', now))
        self.assertEqual(now + timedelta(days=2), thaiword_to_date('มะรืนนี้', now))
        self.assertEqual(now + timedelta(days=-1), thaiword_to_date('เมื่อวาน', now))
        self.assertEqual(now + timedelta(days=-2), thaiword_to_date('วานซืน', now))
        self.assertIsNotNone(thaiword_to_date('วันนี้'))
        self.assertIsNone(thaiword_to_date('วันไหน'))

    def test_thai_strptime(self):
        self.assertIsNotNone(thai_strptime('05-7-65 09:00:01.10600', '%d-%B-%Y %H:%M:%S.%f', year='be'))
        self.assertIsNotNone(thai_strptime('24-6-75 09:00:00', '%d-%B-%Y %H:%M:%S', year='be', add_year=2400))
        self.assertIsNotNone(thai_strptime('05-7-22 09:00:01.10600', '%d-%B-%Y %H:%M:%S.%f', year='ad'))
        self.assertIsNotNone(thai_strptime('05-7-99 09:00:01.10600', '%d-%B-%Y %H:%M:%S.%f', year='ad', add_year=1900))

    def test_convert_years(self):
        years = {'be': '2566', 'ad': '2023', 're': '242', 'ah': '1444'}
        for src, src_year in years.items():
            for target, target_year in years.items():
                with self.subTest(src=src, target=target):
                    self.assertEqual(convert_years(src_year, src=src, target=target), target_year)

    def test_convert_years_defaults_and_inputs(self):
        self.assertEqual(convert_years('2566'), '2023')
        self.assertEqual(convert_years(2566), '2023')
        self.assertEqual(convert_years(' 2566 '), '2023')
        self.assertEqual(convert_years('0', src='ad', target='be'), '543')
        self.assertEqual(convert_years('-1', src='ad', target='be'), '542')

    def test_convert_years_same_era(self):
        cases = (('2566', '2566'), (' 2566 ', '2566'), ('0007', '7'), ('0', '0'), ('-1', '-1'), ('12345', '12345'), ('๒๕๖๖', '2566'), (2566, '2566'))
        for era in ('be', 'ad', 're', 'ah'):
            for year, expected in cases:
                with self.subTest(era=era, year=year):
                    self.assertEqual(convert_years(year, src=era, target=era), expected)
            for year in ('abc', '', '2566\u200b'):
                with self.subTest(era=era, year=year):
                    with self.assertRaises(ValueError):
                        convert_years(year, src=era, target=era)

    def test_convert_years_adversarial(self):
        cases = (('0', 'be', 'ad', '-543'), ('-1', 'be', 'ad', '-544'), ('12345', 'be', 'ad', '11802'), ('๒๕๖๖', 'be', 'ad', '2023'), ('0007', 'be', 'ad', '-536'))
        for year, src, target, expected in cases:
            with self.subTest(year=year):
                self.assertEqual(convert_years(year, src, target), expected)
        bad_years: list[Any] = [None, []]
        for year in bad_years:
            with self.subTest(year=year):
                with self.assertRaises(TypeError):
                    convert_years(year, 'be', 'ad')
        for year in ('abc', '', '2566\u200b'):
            with self.subTest(year=year):
                with self.assertRaises(ValueError):
                    convert_years(year, 'be', 'ad')
        for era in ('BE', 'Be', 'cat', ''):
            with self.subTest(era=era):
                with self.assertRaises(NotImplementedError):
                    convert_years('2566', era, era)

    def test_convert_years_unchanged_pairs(self):
        eras: list[Any] = ['be', 'ad', 're', 'ah', 'BE', 'cat', '', None, []]
        years: list[Any] = ['2566', ' 2566 ', '0', '-1', 'abc', '', 2566, '12345', '๒๕๖๖', '0007', '2566\u200b']
        digest = hashlib.sha256()
        count = 0
        for year in years:
            for src in eras:
                for target in eras:
                    if isinstance(src, str) and src == target and (src in ('be', 'ad', 're', 'ah')):
                        continue
                    try:
                        out = convert_years(year, src, target)
                    except Exception as err:
                        out = '!' + type(err).__name__
                    digest.update(repr((year, src, target, out)).encode())
                    count += 1
        self.assertEqual(count, 847)
        self.assertEqual(digest.hexdigest(), '273c414e87e846fe9c32527f6644600df7c477414ff4d4f7103bf1858872b737')

    def test_convert_years_unsupported(self):
        for src, target in (('cat', 'dog'), ('be', 'dog'), ('cat', 'ad'), ('BE', 'ad'), ('', '')):
            with self.subTest(src=src, target=target):
                with self.assertRaises(NotImplementedError):
                    convert_years('2023', src=src, target=target)
        unhashable_eras: list[Any] = [[], ['be'], {}]
        for era in unhashable_eras:
            with self.subTest(era=era):
                with self.assertRaises(NotImplementedError):
                    convert_years('2023', src=era, target='ad')
                with self.assertRaises(NotImplementedError):
                    convert_years('2023', src='be', target=era)
        with self.assertRaises(NotImplementedError):
            convert_years('abc', src='cat', target='dog')
        with self.assertRaises(ValueError):
            convert_years('abc', src='be', target='ad')
        with self.assertRaises(ValueError):
            convert_years('', src='be', target='ad')
