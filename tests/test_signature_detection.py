#!/usr/bin/env python

"""Tests for `iapp_ai` package."""
import sys, os
sys.path.append(os.path.abspath(os.path.join('.', '')))

import pytest
from test_globals import apikey
import iapp_ai

# # TODO: Not yet Support
# def test_signature_detection():
#     api = iapp_ai.api(apikey)
#     resp = api.signature_detect("media/signature.jpg")
#     print(resp.text)
#     # assert resp.ok 
#     # assert resp.json() is not None

