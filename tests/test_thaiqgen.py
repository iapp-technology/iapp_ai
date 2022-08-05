#!/usr/bin/env python

"""Tests for `iapp_ai` package."""
import sys, os
sys.path.append(os.path.abspath(os.path.join('.', '')))

import pytest
from test_globals import apikey
import iapp_ai

def test_thai_qgen():
    api = iapp_ai.api(apikey)
    resp = api.thai_qgen_api(text="แค็วม์เป็นแค่หมู่บ้านใช่หรือไม่")
    # print(resp.json())
    assert resp.ok 
    assert resp.text is not None
