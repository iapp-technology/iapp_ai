#!/usr/bin/env python

"""Tests for `iapp_ai` package."""
import sys, os
sys.path.append(os.path.abspath(os.path.join('.', '')))

import pytest
from test_globals import apikey
import iapp_ai

def test_license_plate_ocr():
    api = iapp_ai.api(apikey)
    resp = api.license_plate_ocr("media/plate.jpg")
    # print(resp.text)
    assert resp.ok
    assert resp.text is not None

