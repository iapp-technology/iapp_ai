#!/usr/bin/env python

"""Tests for `iapp_ai` package."""
import sys, os
sys.path.append(os.path.abspath(os.path.join('.', '')))

import pytest
from test_globals import apikey
import iapp_ai

def test_passport_ocr():
    api = iapp_ai.api(apikey)
    resp = api.passport_ocr("media/ukr-passport.jpeg")
    # resp = api.passport_ocr("media/thai-passport.jpeg")
    print(resp.json())
    assert resp.ok 
    assert resp.json() is not None

