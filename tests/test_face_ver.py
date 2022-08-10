#!/usr/bin/env python

"""Tests for `iapp_ai` package."""
import sys, os
sys.path.append(os.path.abspath(os.path.join('.', '')))

import pytest
from test_globals import apikey
import iapp_ai

def test_face_ver1():
    api = iapp_ai.api(apikey)
    resp = api.face_verification("media/face.jpg", "media/face.jpg", "iApp", "0.1")
    # print(resp.json())
    assert resp.ok 
    assert resp.text is not None


def test_face_ver2():
    api = iapp_ai.api(apikey)
    resp = api.face_ver2("media/face.jpg", "media/face.jpg")
    # print(resp.text)
    assert resp.ok 
    assert resp.text is not None

# # TODO: Not yet support faceVerConfig yet
def test_face_ver_config():
    api = iapp_ai.api(apikey)
    resp = api.face_ver_config_score("0.5","0.5","iApp", "iApp")
    # print(resp.text)
    assert resp.ok 
    assert resp.text is not None

