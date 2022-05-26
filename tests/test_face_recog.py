#!/usr/bin/env python

"""Tests for `iapp_ai` package."""
import sys, os
sys.path.append(os.path.abspath(os.path.join('.', '')))

import pytest
from test_globals import apikey
import iapp_ai

def test_face_recog_single():
    api = iapp_ai.api(apikey)
    resp = api.face_recog_single("media/id-card-front.jpg", "iApp")
    # print(resp.json())
    # assert resp.ok 
    # assert resp.json() is not None

def test_face_recog_multi():
    api = iapp_ai.api(apikey)
    resp = api.face_recog_multi("media/id-card-front.jpg", "iApp")
    print(resp.text)
    # assert resp.ok 
    # assert resp.json() is not None

def test_face_recog_facecrop():
    api = iapp_ai.api(apikey)
    resp = api.face_recog_facecrop("media/id-card-front.jpg", "iApp")
    print(resp.text)
    # assert resp.ok 
    # assert resp.json() is not None

# TODO: Not yet Support
# def test_face_recog_add():
#     api = iapp_ai.api(apikey)
#     resp = api.face_recog_add("media/id-card-front.jpg", "iApp", "Panuphong", "1234")
#     # print(resp.json())
#     # assert resp.ok 
#     # assert resp.json() is not None

# TODO: Not yet Support
# def test_face_recog_import():
#     api = iapp_ai.api(apikey)
#     resp = api.face_recog_import("media/file.csv", "iApp", "1234")
#     print(resp.text)
#     # assert resp.ok 
#     # assert resp.json() is not None

# TODO: Not yet Support
# def test_face_recog_check():
#     print("Check")
#     api = iapp_ai.api(apikey)
#     resp = api.face_recog_check("iApp", "1234")
#     print(resp.text)
    # assert resp.ok 
    # assert resp.json() is not None

def test_face_recog_export():
    print("Export")
    api = iapp_ai.api(apikey)
    resp = api.face_recog_export("iApp", "1234")
    # assert resp.ok 
    # assert resp.json() is not None

# TODO: Not yet Support
# def test_face_recog_remove():
#     api = iapp_ai.api(apikey)
#     resp = api.face_recog_remove("iApp", "Panupong", "1234", "18-05-2022", "01")
#     # print(resp.json())
#     # assert resp.ok 
#     # assert resp.json() is not None

# TODO: Not yet Support
# def test_face_recog_configscore():
#     api = iapp_ai.api(apikey)
#     resp = api.face_recog_config_score("0.9", "0.5","iApp", "1234")
#     print(resp.text)
    # assert resp.ok 
    # assert resp.json() is not None

