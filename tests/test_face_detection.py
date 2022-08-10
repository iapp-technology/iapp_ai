#!/usr/bin/env python

"""Tests for `iapp_ai` package."""
import sys, os
sys.path.append(os.path.abspath(os.path.join('.', '')))

import pytest
from test_globals import apikey
import iapp_ai

def test_face_detection_single():
    api = iapp_ai.api(apikey)
    resp = api.face_detect_single("media/face.jpg")
    # print(resp.json())
    assert resp.ok 
    assert resp.text is not None

def test_face_detection_multi():
    api = iapp_ai.api(apikey)
    resp = api.face_detect_multi("media/multi_face.jpg", "iApp")
    # print(resp.json())
    assert resp.ok 
    assert resp.text is not None

def test_face_detection_config():
    api = iapp_ai.api(apikey)
    resp = api.face_detect_config_score("0.5","iApp", "iApp")
    # print(resp.json())
    assert resp.ok 
    assert resp.text is not None
