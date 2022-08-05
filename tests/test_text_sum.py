#!/usr/bin/env python
# coding=utf8

"""Tests for `iapp_ai` package."""
import sys, os
sys.path.append(os.path.abspath(os.path.join('.', '')))

import pytest
from test_globals import apikey
import iapp_ai

def test_text_summarization():
    api = iapp_ai.api(apikey)
    resp = api.thai_text_summarization(text="ตำรวจกองปราบ ดังกล่าวล่าสุด เมื่อเวลา 09.30 น. วันที่ 11 มีนาคม 2555 ผู้สื่อข่าวรายงานว่า ภายหลัง พล.ต.ท.จิรภพ ภูริเดช ผบช.ก. นำกําลังตำรวจสอบสวนกลาง สนธิกำลังร่วมกับ ตำรวจภูธรภาค 9 เข้าตรวจค้นพื้นที่เป้าหมายหลายจุดเมื่อช่วงเช้าที่ผ่านมา สุดขณะนี้ สามารถจับกุมตัว นายพงศกร หรือเจ สุวรรณมะโณ อายุ 22 ปี หนึ่งในกลุ่มผู้ต้องหาที่ถูกออกหมายจับได้ หลังทราบว่าหลบซ่อนตัวอยู่ภายในพื้นที่ อ.รัตภูมิ จ.สงขลา ก่อนพาตัวเข้าจุดซ่อนอาวุธปืนภายในสวนปาล์มท้ายวัดท่าควาย ซึ่งจากการหาเข้าตรวจค้น พบอาวุธปืนในการก่อเหตุจํานวน 2 กระบอก ประกอบด้วย ปีนเอชเค 1 กระบอก และ ปืนพกสั้นขนาด 9 มม. 1 กระบอก ซุกซ่อนในกอหญ้าในต้นปาล์มและต้นกล้วย", output_length=84)
    # print(resp.json())
    assert resp.ok 
    assert resp.text is not None

# test_text_summarization()
