#!/usr/bin/env python

"""Tests for `iapp_ai` package."""
import sys, os
sys.path.append(os.path.abspath(os.path.join('.', '')))

import pytest
from test_globals import apikey
import iapp_ai

def test_face_recog_single():
    api = iapp_ai.api(apikey)
    resp = api.face_recog_single("media/face.jpg", "iApp")
    # print(resp.json())
    assert resp.ok 
    assert resp.text is not None

def test_face_recog_multi():
    api = iapp_ai.api(apikey)
    resp = api.face_recog_multi("media/multi_face.jpg", "iApp")
    # print(resp.text)
    assert resp.ok 
    assert resp.text is not None

def test_face_recog_facecrop():
    api = iapp_ai.api(apikey)
    resp = api.face_recog_facecrop("media/face.jpg", "iApp")
    # print(resp.text)
    assert resp.ok 
    assert resp.text is not None


def test_face_recog_add():
    api = iapp_ai.api(apikey)
    resp = api.face_recog_add("media/face.jpg", "iApp", "Panuphong", "iApp")
    # print(resp.json())
    assert resp.ok 
    assert resp.json() is not None

def test_face_recog_import():
    api = iapp_ai.api(apikey)
    resp = api.face_recog_import("media/file.csv", "iApp", "iApp")
    # print(resp.text)
    assert resp.ok 
    assert resp.text is not None

def test_face_recog_check():
    print("Check")
    api = iapp_ai.api(apikey)
    resp = api.face_recog_check("iApp", "iApp")
    # print(resp.text)
    assert resp.ok 
    assert resp.text is not None

def test_face_recog_export():
    print("Export")
    api = iapp_ai.api(apikey)
    resp = api.face_recog_export("iApp", "iApp", "csv")
    assert resp.ok 
    assert resp.text is not None


def test_face_recog_remove():
    api = iapp_ai.api(apikey)
    resp = api.face_recog_remove("iApp", "Panupong", "iApp", "18-05-2022", "01")
    # print(resp.json())
    assert resp.ok 
    assert resp.json() is not None


def test_face_recog_configscore():
    api = iapp_ai.api(apikey)
    resp = api.face_recog_config_score("0.9", "0.5","iApp", "iApp")
    # print(resp.text)
    assert resp.ok 
    assert resp.text is not None

