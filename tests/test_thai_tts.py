#!/usr/bin/env python

"""Tests for `iapp_ai` package."""
import sys, os
sys.path.append(os.path.abspath(os.path.join('.', '')))

import pytest
from test_globals import apikey
import iapp_ai

def test_tts_kaitom():
    api = iapp_ai.api(apikey)
    resp = api.thai_thaitts_kaitom("ภาษาไทย")
    print(resp)
    assert resp
    assert resp is not None

def test_tts_cee():
    api = iapp_ai.api(apikey)
    resp = api.thai_thaitts_cee("นี่คือฉัน")
    print(resp)
    assert resp 
    assert resp is not None
