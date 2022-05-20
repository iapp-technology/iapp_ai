#!/usr/bin/env python

"""Tests for `iapp_ai` package."""

import pytest
import sys, os
sys.path.append(os.path.abspath(os.path.join('.', '')))
from test_globals import apikey
import iapp_ai

def test_thai_qa():
    api = iapp_ai.api(apikey)
    resp = api.thai_qa_api(question="แค็วม์เป็นแค่หมู่บ้านใช่หรือไม่", document="จังหวัดแค็วม์โปแลนด์คือหน่วยการปกครองท้องถิ่นของประเทศโปแลนด์ในช่วงปี ค.ศ.1975 - ค.ศ.1998 จังหวัดได้รับการรวมเข้ากับจังหวัดลูบลินมีเมืองหลักคือแค็วม์ใน ปี ค.ศ.1998 มีพื้นที่ประมาณ 3865 ตารางกิโลเมตรและมีประชากร 248800 คน")
    print(resp.text)
    assert resp.ok 
    assert resp.text is not None


