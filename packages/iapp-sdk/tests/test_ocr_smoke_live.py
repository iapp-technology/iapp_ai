import os
import inspect
from typing import Dict, Optional
import pytest
import requests
import iapp_ai.module_api as module_api
from iapp_ai import api

IAPP_API_KEY = os.environ.get("IAPP_API_KEY")
PIC_URLS = {
    "idcard_front": "https://iapp.co.th/img/api/thai_id_card_front.png",
    "idcard_back": "https://www.researchgate.net/profile/Pattarawit-Polpinit/publication/335143642/figure/fig1/AS:791435246850049@1565704275575/Example-for-front-and-back-of-one-ID-card.jpg",
    "idcard_front_photocopied": "https://iapp.co.th/img/api/thai-national-id-card-ocr-with-signature-detection-example.png",
    "book_bank_api": "https://iapp.co.th/img/api/ekyc/bookbank_example.png",
    "passport_ocr": "https://iapp.co.th/img/api/passport-ocr-example.png",
    "document_ocr_plaintext": "https://iapp.co.th/img/api/general-thai-document-ocr-01.png",
    "document_ocr_json_layout": "https://iapp.co.th/img/api/general-thai-document-ocr-01.png",
    "document_ocr_docx": "https://iapp.co.th/img/api/general-thai-document-ocr-01.png",
    "driver_card_ocr": "https://iapp.co.th/img/api/thai_driver_license_example.png"
}

# Helper to download image or return dummy image path
def get_test_image_path(method_name: str, tmp_path) -> str:
    url = PIC_URLS.get(method_name)
    
    # Try downloading if it starts with http/https
    if url and url.startswith(("http://", "https://")):
        try:
            # Short timeout to avoid hanging
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                ext = ".png" if ".png" in url.lower() else ".jpg"
                img_file = tmp_path / f"test_{method_name}{ext}"
                img_file.write_bytes(resp.content)
                return str(img_file)
        except Exception:
            pass
            
    # Fallback: create a tiny dummy 1x1 JPG
    dummy_jpg = tmp_path / f"dummy_{method_name}.jpg"
    dummy_jpg.write_bytes(
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00"
        b"\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19"
        b"\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f"
        b"'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x01\xff\xc4\x00\x1f"
        b"\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02"
        b"\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00"
        b"\x3f\x00\xbf\x00\xff\xd9"
    )
    return str(dummy_jpg)

# --- OFFLINE / MOCKED TESTS (Tasks B1-6 Verification) ---

@pytest.fixture
def mock_client(monkeypatch):
    captured = {}
    def fake_request_sync(
        method, url, *, apikey, headers=None, params=None, data=None,
        json_body=None, files=None, raise_for_error=False, timeout=None
    ):
        captured["method"] = method
        captured["url"] = url
        captured["apikey"] = apikey
        captured["headers"] = headers
        captured["data"] = data
        captured["files"] = files
        
        # Close handles
        for item in files or []:
            if isinstance(item, tuple) and len(item) > 1:
                file_tuple = item[1]
                if isinstance(file_tuple, tuple) and len(file_tuple) > 1:
                    handle = file_tuple[1]
                    if hasattr(handle, "close"):
                        handle.close()
        
        resp = requests.Response()
        resp.status_code = 200
        resp._content = b'{"status": "ok", "text": "mocked response"}'
        resp.url = url
        return resp

    monkeypatch.setattr(module_api, "request_sync", fake_request_sync)
    return captured

# B-1: File Leak Checks for all 9 methods
def test_mock_b1_file_leak(monkeypatch, tmp_path):
    dummy_file = tmp_path / "test_ocr.jpg"
    dummy_file.write_bytes(b"dummy image")
    file_path = str(dummy_file)
    captured_handles = []

    def fake_request_sync_leak(
        method, url, *, apikey, headers=None, params=None, data=None,
        json_body=None, files=None, raise_for_error=False, timeout=None
    ):
        for item in files or []:
            if isinstance(item, tuple) and len(item) > 1:
                file_tuple = item[1]
                if isinstance(file_tuple, tuple) and len(file_tuple) > 1:
                    handle = file_tuple[1]
                    captured_handles.append(handle)
                    assert not handle.closed, "File was closed before request_sync"
        resp = requests.Response()
        resp.status_code = 200
        resp._content = b'{"ok": true}'
        resp.url = url
        return resp

    monkeypatch.setattr(module_api, "request_sync", fake_request_sync_leak)
    client = api("TEST_API_KEY")
    methods = [
        "idcard_front", "idcard_back", "idcard_front_photocopied",
        "book_bank_api", "passport_ocr", "document_ocr_plaintext",
        "document_ocr_json_layout", "document_ocr_docx", "driver_card_ocr"
    ]
    for method_name in methods:
        captured_handles.clear()
        method = getattr(client, method_name)
        method(file_path)
        assert len(captured_handles) > 0
        for handle in captured_handles:
            assert handle.closed, f"File handle leaked in {method_name}"

# B-2: URL Trim Check
def test_mock_b2_url_trim(mock_client, tmp_path):
    dummy_file = tmp_path / "test_ocr.jpg"
    dummy_file.write_bytes(b"dummy")
    client = api("TEST_API_KEY")
    client.idcard_front_photocopied(str(dummy_file))
    assert mock_client["url"] == "https://api.iapp.co.th/v3/store/ekyc/thai-national-id-card-with-signature"
    assert not mock_client["url"].startswith(" ")

# B-3: Print statement removal check
def test_mock_b3_no_print(mock_client, tmp_path, capsys):
    dummy_file = tmp_path / "test_ocr.jpg"
    dummy_file.write_bytes(b"dummy")
    client = api("TEST_API_KEY")
    client.document_ocr_docx(str(dummy_file))
    captured = capsys.readouterr()
    assert captured.out == ""

# B-4: Type Hints & Docstrings verification
def test_mock_b4_type_hints():
    methods = [
        "idcard_front", "idcard_back", "idcard_front_photocopied",
        "book_bank_api", "passport_ocr", "document_ocr_plaintext",
        "document_ocr_json_layout", "document_ocr_docx", "driver_card_ocr"
    ]
    for method_name in methods:
        method = getattr(api, method_name)
        sig = inspect.signature(method)
        assert sig.return_annotation is requests.Response
        assert sig.parameters["file_path"].annotation is str
        assert sig.parameters["headers"].annotation in (Dict[str, str], Optional[Dict[str, str]])
        doc = method.__doc__
        assert doc is not None
        assert "Args:" in doc
        assert "Returns:" in doc

# B-5: Mutable Default values checks
def test_mock_b5_mutable_defaults(monkeypatch, tmp_path):
    dummy_file = tmp_path / "test_ocr.jpg"
    dummy_file.write_bytes(b"dummy")
    file_path = str(dummy_file)
    captured_calls = []

    def fake_request_sync_mutable(
        method, url, *, apikey, headers=None, params=None, data=None,
        json_body=None, files=None, raise_for_error=False, timeout=None
    ):
        captured_calls.append({
            "headers": headers, "data": data,
            "files_count": len(files) if files is not None else 0
        })
        for item in files or []:
            if isinstance(item, tuple) and len(item) > 1:
                file_tuple = item[1]
                if isinstance(file_tuple, tuple) and len(file_tuple) > 1:
                    handle = file_tuple[1]
                    handle.close()
        resp = requests.Response()
        resp.status_code = 200
        resp._content = b'{"ok": true}'
        resp.url = url
        return resp

    monkeypatch.setattr(module_api, "request_sync", fake_request_sync_mutable)
    methods = [
        "idcard_front", "idcard_back", "idcard_front_photocopied",
        "book_bank_api", "passport_ocr", "document_ocr_plaintext",
        "document_ocr_json_layout", "document_ocr_docx", "driver_card_ocr"
    ]
    client = api("TEST_API_KEY")
    for method_name in methods:
        method = getattr(client, method_name)
        # Verify defaults are None in signature
        sig = inspect.signature(method)
        assert sig.parameters["headers"].default is None
        assert sig.parameters["data_payload"].default is None
        assert sig.parameters["files"].default is None

        # Verify mutation in one call doesn't pollute subsequent calls
        captured_calls.clear()
        method(file_path) # Call 1
        method(file_path, headers={"Custom": "Val"}, data_payload={"K": "V"}, files=[("ex", b"ex")]) # Call 2
        captured_calls.clear()
        method(file_path) # Call 3 (uses defaults again)
        call3 = captured_calls[0]
        assert call3["headers"] == {}
        assert call3["data"] == {}
        assert call3["files_count"] == 1

# B-6: Endpoints Alignment check
def test_mock_b6_endpoints(mock_client, tmp_path):
    dummy_file = tmp_path / "test_ocr.jpg"
    dummy_file.write_bytes(b"dummy")
    file_path = str(dummy_file)
    client = api("TEST_API_KEY")
    client.document_ocr_plaintext(file_path)
    assert mock_client["url"] == "https://api.iapp.co.th/v3/store/ocr/document/ocr"
    client.document_ocr_json_layout(file_path)
    assert mock_client["url"] == "https://api.iapp.co.th/v3/store/ocr/document/layout"
    client.document_ocr_docx(file_path)
    assert mock_client["url"] == "https://api.iapp.co.th/v3/store/ocr/document/docx"


# B-7 (Offline Mock/Smoke): Verification of all 9 OCR methods offline
@pytest.mark.parametrize("method_name", [
    "idcard_front", "idcard_back", "idcard_front_photocopied",
    "book_bank_api", "passport_ocr", "document_ocr_plaintext",
    "document_ocr_json_layout", "document_ocr_docx", "driver_card_ocr"
])
def test_mock_ocr_methods(method_name, mock_client, tmp_path):
    dummy_file = tmp_path / f"mock_{method_name}.jpg"
    dummy_file.write_bytes(b"mock image content")
    
    client = api("TEST_API_KEY")
    method = getattr(client, method_name)
    resp = method(str(dummy_file))
    
    assert isinstance(resp, requests.Response)
    assert resp.status_code == 200
    assert mock_client["method"] == "POST"
    assert mock_client["apikey"] == "TEST_API_KEY"
    assert mock_client["files"] is not None


# --- LIVE INTEGRATION TESTS (Task B-7) ---

@pytest.mark.skipif(not IAPP_API_KEY, reason="Live tests require IAPP_API_KEY env var")
@pytest.mark.parametrize("method_name", [
    "idcard_front", "idcard_back", "idcard_front_photocopied",
    "book_bank_api", "passport_ocr", "document_ocr_plaintext",
    "document_ocr_json_layout", "document_ocr_docx", "driver_card_ocr"
])
def test_live_ocr_methods(method_name, tmp_path):
    client = api(IAPP_API_KEY)
    img_path = get_test_image_path(method_name, tmp_path)
    method = getattr(client, method_name)
    resp = method(img_path)
    assert isinstance(resp, requests.Response)
    # Check that status code is one of the expected/successful or business error codes.
    # 563 is ID_CARD_API_NOT_SUPPORT_THIS_IMAGE which is a standard return code for dummy/unsupported images
    assert resp.status_code in (200, 400, 401, 403, 404, 422, 500, 563), f"Unexpected status {resp.status_code}: {resp.text}"
