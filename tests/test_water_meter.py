#!/usr/bin/env python

"""Tests for `iapp_ai` package."""
import sys, os
sys.path.append(os.path.abspath(os.path.join('.', '')))

import pytest
from test_globals import apikey
import iapp_ai

def test_water_meter_file():
    api = iapp_ai.api(apikey)
    resp = api.water_meter_binary("media/wm.jpg")
    print(resp.text)
    # assert resp.ok 
    # assert resp.json() is not None

def test_water_meter_base64():
    api = iapp_ai.api(apikey)
    resp = api.water_meter_base64(image="media/water-meter.txt")
    print(resp.text)
    assert resp.ok 
    assert resp.json() is not None

# test_water_meter_file()
# test_water_meter_base64()