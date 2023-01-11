#!/usr/bin/env python

"""Tests for `iapp_ai` package."""
import sys, os
sys.path.append(os.path.abspath(os.path.join('.', '')))

import pytest
from test_globals import apikey
import iapp_ai

def test_face_ver1():
    api = iapp_ai.api(apikey)
    resp = api.face_verification(file_path1="media/face.jpg", file_path2="media/face.jpg",company_name= "iApp",min_score= "0.1")
    # print(resp.json())
    assert resp.ok 
    assert resp.text is not None

def test_face_ver2():
    api = iapp_ai.api(apikey)
    resp = api.face_ver2(file_path1="media/face.jpg",file_path2= "media/face.jpg")
    # print(resp.text)
    assert resp.ok 
    assert resp.text is not None

# # TODO: Not yet support faceVerConfig yet
def test_face_ver_config():
    api = iapp_ai.api(apikey)
    resp = api.face_ver_config_score(detect_value="0.4",compare_value="0.9",company_name="iApp",company_password="iApp")
    # print(resp.text)
    assert resp.ok 
    assert resp.text is not None

