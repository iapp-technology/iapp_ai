#!/usr/bin/env python

"""Tests for `iapp_ai` package."""

import pytest
import sys, os
sys.path.append(os.path.abspath(os.path.join('.', '')))
from test_globals import apikey
import iapp_ai

def test_face_liveness():
    api = iapp_ai.api(apikey)
    resp = api.face_liveness("media/E7393203-15.jpg")
    print(resp.json())
    assert resp.ok 
    assert resp.json() is not None
    return resp.json()

def test_info_face_liveness(taskGuid=test_face_liveness()):
    api = iapp_ai.api(apikey)
    # print(str_taskGuid)
    resp = api.info_face_liveness(taskGuid=str(taskGuid))
    print(resp.json())
    assert resp.ok 
    assert resp.json() is not None

