"""Offline backward-compatibility guard for the iApp AI SDK.

These tests monkeypatch the shared ``request_sync`` so they run with no network
and no API key. They lock down the behaviors existing users depend on:

* methods return the raw ``requests.Response`` and do NOT raise on 4xx,
* the API key is injected,
* endpoint URLs (including legacy quirks: leading space, plain http, the
  non-iApp host) are preserved verbatim,
* multipart file tuples keep their exact field names and content types.
"""

import json

import pytest
import requests

import iapp_ai
import iapp_ai.module_api as module_api
from iapp_ai import api


@pytest.fixture
def captured(monkeypatch):
    """Replace request_sync with a recorder that returns a fake 403 Response."""
    calls = {}

    def fake_request_sync(
        method,
        url,
        *,
        apikey,
        headers=None,
        params=None,
        data=None,
        json_body=None,
        files=None,
        raise_for_error=False,
        timeout=None,
    ):
        # Close any opened file handles to avoid ResourceWarnings.
        for item in files or []:
            handle = item[1][1] if isinstance(item[1], (list, tuple)) and len(item[1]) > 1 else None
            if hasattr(handle, "close"):
                handle.close()
        calls.clear()
        calls.update(
            method=method,
            url=url,
            apikey=apikey,
            headers=headers,
            params=params,
            data=data,
            json_body=json_body,
            files=files,
            raise_for_error=raise_for_error,
            timeout=timeout,
        )
        resp = requests.Response()
        resp.status_code = 403
        resp._content = b'{"ok": false}'
        resp.url = url.strip()
        return resp

    monkeypatch.setattr(module_api, "request_sync", fake_request_sync)
    return calls


def test_version_is_fixed():
    # The legacy __init__ had a malformed __version__ string; it is now valid.
    assert iapp_ai.__version__ == "1.3.0"


def test_returns_raw_response_and_does_not_raise(captured):
    client = api("MY_KEY")
    resp = client.eng_thai_translate("hello")
    assert isinstance(resp, requests.Response)
    assert resp.status_code == 403  # 4xx is RETURNED, never raised
    assert captured["apikey"] == "MY_KEY"
    assert captured["method"] == "GET"
    assert captured["url"] == "https://api.iapp.co.th/translate/auto?text=hello"
    assert captured["raise_for_error"] is False


def test_json_endpoint_sets_content_type(captured):
    client = api("K")
    client.thai_qa_api(question="q", document="d")
    assert captured["url"] == "https://api.iapp.co.th/thai-qa/inference"
    assert captured["headers"].get("Content-Type") == "application/json"
    assert json.loads(captured["data"]) == {"question": "q", "document": "d"}


def test_idcard_front_url_and_content_type(captured, tmp_path):
    f = tmp_path / "id.jpg"
    f.write_bytes(b"\xff\xd8\xff")
    api("K").idcard_front(str(f))
    assert captured["url"] == "https://api.iapp.co.th/thai-national-id-card/v3/front"
    field, filetuple = captured["files"][0]
    assert field == "file"
    assert filetuple[0] == "id.jpg"      # basename used as filename
    assert filetuple[2] == "image/jpg"   # exact legacy content type, not image/jpeg


def test_photocopied_url_is_trimmed(captured, tmp_path):
    f = tmp_path / "id.jpg"
    f.write_bytes(b"x")
    api("K").idcard_front_photocopied(str(f))
    assert captured["url"] == "https://api.iapp.co.th/thai-national-id-card-with-signature/front"


def test_qgen_uses_plain_http_and_apikey_in_query(captured):
    api("SECRET").thai_qgen_api("text")
    assert captured["url"].startswith("http://api.iapp.co.th/qa-generator-th?text=")
    assert "&apikey=SECRET" in captured["url"]


def test_face_verification_two_files_octet_stream(captured, tmp_path):
    f1 = tmp_path / "a.jpg"
    f1.write_bytes(b"a")
    f2 = tmp_path / "b.jpg"
    f2.write_bytes(b"b")
    api("K").face_verification(str(f1), str(f2), "acme", 0.5)
    assert captured["url"] == "https://api.iapp.co.th/face_compare"
    assert captured["data"]["company"] == "acme"
    assert captured["data"]["min_score"] == 0.5
    fields = [item[0] for item in captured["files"]]
    assert fields == ["file1", "file2"]
    assert all(item[1][2] == "application/octet-stream" for item in captured["files"])


def test_asr_uses_raw_path_filename_and_mpga(captured, tmp_path):
    f = tmp_path / "speech.mp3"
    f.write_bytes(b"x")
    api("K").thai_asr_api(str(f))
    assert captured["url"] == "https://api.iapp.co.th/asr"
    _field, filetuple = captured["files"][0]
    assert filetuple[0] == str(f)        # raw path used as filename (legacy quirk)
    assert filetuple[2] == "audio/mpga"


def test_power_meter_hits_legacy_host(captured, tmp_path):
    f = tmp_path / "m.txt"
    f.write_text("base64data")
    api("K").power_meter(image=str(f))
    assert captured["url"] == "https://titipakorn.xyz/ocr/api/predict/ocr_detect/"


def test_passport_ocr_uses_two_tuple_file(captured, tmp_path):
    f = tmp_path / "p.jpg"
    f.write_bytes(b"x")
    api("K").passport_ocr(str(f))
    assert captured["url"] == "https://api.iapp.co.th/passport-ocr/ocr"
    # passport uses a 2-tuple (no content type) — must not gain one
    assert len(captured["files"][0][1]) == 2
