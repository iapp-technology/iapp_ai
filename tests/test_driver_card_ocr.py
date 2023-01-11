#!/usr/bin/env python

"""Tests for `iapp_ai` package."""
import sys, os
sys.path.append(os.path.abspath(os.path.join('.', '')))

import pytest
from test_globals import apikey
import iapp_ai

def test_driver_card_ocr():
    api = iapp_ai.api(apikey)
    resp = api.driver_card_ocr("media/driver_card.png")
    # print(resp.json())
    assert resp.ok 
    assert resp.json() is not None

