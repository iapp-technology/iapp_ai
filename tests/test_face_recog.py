#!/usr/bin/env python

"""Tests for `iapp_ai` package."""
import sys, os
sys.path.append(os.path.abspath(os.path.join('.', '')))

import pytest
from test_globals import apikey
import iapp_ai

def test_face_recog_single():
    api = iapp_ai.api(apikey)
    resp = api.face_recog_single(file_path="media/face.jpg", company_name="iApp")
    print(resp.json())
    assert resp.ok 
    assert resp.text is not None

def test_face_recog_multi():
    api = iapp_ai.api(apikey)
    resp = api.face_recog_multi(file_path="media/multi_face.jpg", company_name="iApp")
    # print(resp.text)
    assert resp.ok 
    assert resp.text is not None

def test_face_recog_facecrop():
    api = iapp_ai.api(apikey)
    resp = api.face_recog_facecrop(file_path="media/face.jpg", company_name="iApp")
    # print(resp.text)
    assert resp.ok 
    assert resp.text is not None


def test_face_recog_add():
    api = iapp_ai.api(apikey)
    resp = api.face_recog_add(file_path="media/face.jpg", company_name="iApp", name="Panuphong", password="iApp")
    # print(resp.json())
    assert resp.ok 
    assert resp.json() is not None

def test_face_recog_import():
    api = iapp_ai.api(apikey)
    resp = api.face_recog_import(file_path="media/file.csv", company_name="iApp",password="iApp")
    # print(resp.text)
    assert resp.ok 
    assert resp.text is not None

def test_face_recog_check():
    print("Check")
    api = iapp_ai.api(apikey)
    resp = api.face_recog_check(company_name="iApp", company_password="iApp")
    # print(resp.text)
    assert resp.ok 
    assert resp.text is not None

def test_face_recog_export():
    print("Export")
    api = iapp_ai.api(apikey)
    resp = api.face_recog_export(company_name="iApp", company_password="iApp", type_file="csv")
    assert resp.ok 
    assert resp.text is not None

def test_face_recog_remove():
    api = iapp_ai.api(apikey)
    resp = api.face_recog_remove(company_name="iApp", name="Panupong", company_password="iApp", date="18-05-2022",face_id="01")
    # print(resp.json())
    assert resp.ok 
    assert resp.json() is not None


def test_face_recog_configscore():
    api = iapp_ai.api(apikey)
    resp = api.face_recog_config_score(detect_value="0.9", recog_value="0.5",company_name="iApp", company_password="iApp")
    # print(resp.text)
    assert resp.ok 
    assert resp.text is not None

