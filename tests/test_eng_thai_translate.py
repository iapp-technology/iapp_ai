#!/usr/bin/env python

"""Tests for `iapp_ai` package."""
import sys, os
sys.path.append(os.path.abspath(os.path.join('.', '')))

import pytest
from test_globals import apikey
import iapp_ai
import json

def test_eng_thai_translate():
    api = iapp_ai.api(apikey)
    # resp = api.eng_thai_translate("This is me.")
    resp = api.eng_thai_translate("นี่คือฉัน")
    print(json.loads(resp.text))
    assert resp.ok 
    assert resp.json() is not None

