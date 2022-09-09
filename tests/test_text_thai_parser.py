#!/usr/bin/env python

"""Tests for `iapp_ai` package."""
import sys, os
sys.path.append(os.path.abspath(os.path.join('.', '')))

import pytest
from test_globals import apikey
import iapp_ai

# # TODO: Not yet Support
# def test_text_thai_parser():
#     api = iapp_ai.api(apikey)
#     resp = api.hai_text_parser("นี่คือฉัน")
#     print(resp.text)
#     # assert resp.ok 
#     # assert resp.json() is not None

