#!/usr/bin/env python

"""Tests for `iapp_ai` package."""
import sys, os
sys.path.append(os.path.abspath(os.path.join('.', '')))

import pytest
from test_globals import apikey
import iapp_ai


# #TODO: API is not ready
def test_water_meter_file():
    api = iapp_ai.api(apikey)
    resp = api.water_meter_binary("media/wm.jpg")
    print(resp.text)
    assert resp
    assert resp.text is not None

def test_water_meter_base64():
    api = iapp_ai.api(apikey)
    resp = api.water_meter_base64(image="media/wm_base64.txt")
    print(resp.json())
    assert resp.ok 
    assert resp.text is not None

