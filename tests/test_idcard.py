#!/usr/bin/env python

"""Tests for `iapp_ai` package."""
# Bring your packages onto the path
# Bring your packages onto the path
import sys, os
sys.path.append(os.path.abspath(os.path.join('.', '')))

import pytest
from test_globals import apikey
import iapp_ai

# @pytest.fixture
# def response():
#     """Sample pytest fixture.

#     See more at: http://doc.pytest.org/en/latest/fixture.html
#     """
#     # import requests
#     # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_idcard_front():
    api = iapp_ai.api(apikey)
    resp = api.idcard_front("media/id-card-front.jpg")
    # print(resp.json())
    assert resp.ok 
    assert resp.json() is not None


def test_idcard_back():
    api = iapp_ai.api(apikey)
    resp = api.idcard_back("media/id-card-back.jpg")
    # print(resp.json())
    assert resp.ok 
    assert resp.json() is not None
