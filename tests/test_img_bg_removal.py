#!/usr/bin/env python

"""Tests for `iapp_ai` package."""
import sys, os
sys.path.append(os.path.abspath(os.path.join('.', '')))

import pytest
from test_globals import apikey
import iapp_ai

def test_img_background_removal():
    api = iapp_ai.api(apikey)
    resp = api.img_bg_removal("media/base64.txt")
    print(resp.json())
    assert resp.ok 
    assert resp.json() is not None
