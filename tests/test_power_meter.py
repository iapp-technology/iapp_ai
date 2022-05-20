#!/usr/bin/env python

"""Tests for `iapp_ai` package."""
import sys, os
sys.path.append(os.path.abspath(os.path.join('.', '')))

import pytest
from test_globals import apikey
import iapp_ai

def test_power_meter():
    api = iapp_ai.api(apikey)
    resp = api.power_meter(headers={'Content-Type': 'application/json'},image="media/base64.txt")
    print(resp.json())
    assert resp.ok 
    assert resp.json() is not None
