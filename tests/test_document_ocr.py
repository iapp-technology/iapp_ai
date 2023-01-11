#!/usr/bin/env python

"""Tests for `iapp_ai` package."""
import sys, os
sys.path.append(os.path.abspath(os.path.join('.', '')))

import pytest
from test_globals import apikey
import iapp_ai

def test_document_ocr_plaintext():
    api = iapp_ai.api(apikey)
    resp = api.document_ocr_plaintext(file_path="media/pdf01.pdf")
    print(resp.json())
    assert resp.ok 
    assert resp.json() is not None

def test_document_json_layout():
    api = iapp_ai.api(apikey)
    resp = api.document_ocr_json_layout(file_path="media/pdf01.pdf")
    print(resp.json())
    assert resp.ok 
    assert resp.json() is not None

def test_document_ocr_docx():
    api = iapp_ai.api(apikey)
    resp = api.document_ocr_docx("media/pdf01.pdf")
    print(resp.text)
    assert resp.ok 
    assert resp.text is not None

