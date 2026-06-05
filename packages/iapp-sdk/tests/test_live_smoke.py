"""Live integration smoke tests (no media fixtures required).

These hit the real ``api.iapp.co.th`` and require a valid ``IAPP_API_KEY``. They
are skipped automatically when the key is unset (see ``conftest.py``). They use
only text inputs, so no image/audio fixtures are needed — they exist to confirm
the SDK still talks to the live API end to end and returns a ``requests.Response``.
"""

import os

import requests

from iapp_ai import api

KEY = os.environ.get("IAPP_API_KEY", "")


def test_translate_live():
    resp = api(KEY).eng_thai_translate("hello")
    assert isinstance(resp, requests.Response)
    assert resp.status_code == 200, resp.text


def test_summarization_live():
    text = "ประเทศไทยมีวัฒนธรรมและประวัติศาสตร์อันยาวนานและมีสถานที่ท่องเที่ยวมากมาย"
    resp = api(KEY).thai_text_summarization(text, 1)
    assert isinstance(resp, requests.Response)
    assert resp.status_code == 200, resp.text
