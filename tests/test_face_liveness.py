#!/usr/bin/env python

"""Tests for `iapp_ai` package."""

import pytest
import sys, os
sys.path.append(os.path.abspath(os.path.join('.', '')))
from test_globals import apikey
import iapp_ai
import time
guid=''

def test_face_liveness():
    global guid
    api = iapp_ai.api(apikey)
    resp = api.face_liveness("media/face.jpg")
    guid = resp.text
    print(resp.text)
    assert resp.ok
    assert resp.text is not None

    return resp

def test_info_face_liveness():
    global guid
    taskGuid  =   guid
    api = iapp_ai.api(apikey)
    
    status = None

    while status is None:
        resp = api.info_face_liveness(taskGuid=str(taskGuid).replace('"',''))
        resps = resp.json()
        if 'status' in resps:
            status = resps['status']
        time.sleep(0.5)
    print(resp.text)
    assert resp.ok 
    assert resp.text is not None
    
    return resp

