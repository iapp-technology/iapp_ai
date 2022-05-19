#!/usr/bin/env python

"""Tests for `iapp_ai` package."""

import pytest
from test_globals import apikey
import iapp_ai

def test():
    api = iapp_ai.api(apikey)
    resp = api.book_bank_api("media/E7393203-15.jpg")
    print(resp.json())
    assert resp.ok 
    assert resp.json() is not None
