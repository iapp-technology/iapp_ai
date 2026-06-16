"""Offline mock tests for the Face & eKYC SDK methods (Task C-6)."""

import json
import os
import pytest
import requests
from iapp_ai import api
import iapp_ai.module_api as module_api

@pytest.fixture
def mock_sdk_request(monkeypatch):
    """Replace request_sync with a mock recorder that returns configurable responses."""
    calls = []
    response_data = {"status_code": 200, "json_payload": {"status": "success", "taskGuid": "test-guid-12345"}}

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
        # Close open file handles to prevent ResourceWarnings
        for item in files or []:
            if isinstance(item[1], (list, tuple)) and len(item[1]) > 1:
                handle = item[1][1]
                if hasattr(handle, "close"):
                    handle.close()
        
        calls.append({
            "method": method,
            "url": url,
            "apikey": apikey,
            "headers": headers,
            "params": params,
            "data": data,
            "json_body": json_body,
            "files": files,
            "raise_for_error": raise_for_error,
            "timeout": timeout,
        })
        
        resp = requests.Response()
        resp.status_code = response_data["status_code"]
        resp._content = json.dumps(response_data["json_payload"]).encode("utf-8")
        resp.url = url
        return resp

    monkeypatch.setattr(module_api, "request_sync", fake_request_sync)
    return {"calls": calls, "response_data": response_data}

def test_face_liveness_flow(mock_sdk_request, tmp_path):
    f = tmp_path / "face.jpg"
    f.write_bytes(b"image_content")
    
    client = api("TEST_KEY")
    
    # 1. Submit Liveness Check
    resp = client.face_liveness(str(f))
    assert resp.status_code == 200
    assert resp.json()["taskGuid"] == "test-guid-12345"
    
    call = mock_sdk_request["calls"][-1]
    assert call["url"] == "https://api.iapp.co.th/v3/store/ekyc/face-passive-liveness"
    assert call["method"] == "POST"
    assert call["apikey"] == "TEST_KEY"
    assert call["files"][0][0] == "file"
    assert call["files"][0][1][0] == "face.jpg" # basename
    
    # 2. Check Global taskGuid is updated to the string, not the response
    import iapp_ai.module_api as mod
    assert mod.taskGuid == "test-guid-12345"
    
    # 3. Retrieve Liveness Info
    resp_info = client.info_face_liveness(taskGuid=mod.taskGuid)
    assert resp_info.status_code == 200
    call_info = mock_sdk_request["calls"][-1]
    assert call_info["url"] == "https://api.iapp.co.th/v3/store/ekyc/face-passive-liveness/test-guid-12345"
    assert call_info["method"] == "GET"

def test_face_verification(mock_sdk_request, tmp_path):
    f1 = tmp_path / "face1.jpg"
    f1.write_bytes(b"1")
    f2 = tmp_path / "face2.jpg"
    f2.write_bytes(b"2")
    
    client = api("K")
    resp = client.face_verification(str(f1), str(f2), "companyA", 48.0)
    assert resp.status_code == 200
    call = mock_sdk_request["calls"][-1]
    assert call["url"] == "https://api.iapp.co.th/v3/store/ekyc/face-verification"
    assert call["data"]["company"] == "companyA"
    assert call["data"]["threshold"] == 48.0
    
    # Test v2 verification
    resp2 = client.face_ver2(str(f1), str(f2))
    assert resp2.status_code == 200
    call2 = mock_sdk_request["calls"][-1]
    assert call2["url"] == "https://api.iapp.co.th/v3/store/ekyc/face-verification"

def test_face_detection(mock_sdk_request, tmp_path):
    f = tmp_path / "face.jpg"
    f.write_bytes(b"x")
    
    client = api("K")
    client.face_detect_single(str(f))
    call = mock_sdk_request["calls"][-1]
    assert call["url"] == "https://api.iapp.co.th/v3/store/ekyc/face-detection/single"
    
    client.face_detect_multi(str(f), "companyB")
    call = mock_sdk_request["calls"][-1]
    assert call["url"] == "https://api.iapp.co.th/v3/store/ekyc/face-detection/multi"
    assert call["data"]["company"] == "companyB"

def test_face_recognition_flow(mock_sdk_request, tmp_path):
    f = tmp_path / "face.jpg"
    f.write_bytes(b"x")
    
    client = api("K")
    
    # 1. recog_single
    client.face_recog_single(str(f), "comp")
    assert mock_sdk_request["calls"][-1]["url"] == "https://api.iapp.co.th/v3/store/ekyc/face-recognition/single"
    assert mock_sdk_request["calls"][-1]["data"]["company"] == "comp"
    
    # 2. recog_multi
    client.face_recog_multi(str(f), "comp")
    assert mock_sdk_request["calls"][-1]["url"] == "https://api.iapp.co.th/v3/store/ekyc/face-recognition/multi"
    
    # 3. recog_facecrop
    client.face_recog_facecrop(str(f), "comp")
    assert mock_sdk_request["calls"][-1]["url"] == "https://api.iapp.co.th/v3/store/ekyc/face-recognition/facecrop"
    
    # 4. recog_add
    client.face_recog_add(str(f), "comp", "john", "pass123")
    assert mock_sdk_request["calls"][-1]["url"] == "https://api.iapp.co.th/v3/store/ekyc/face-recognition/add"
    assert mock_sdk_request["calls"][-1]["data"]["name"] == "john"
    
    # 5. recog_import
    client.face_recog_import(str(f), "comp", "pass123")
    assert mock_sdk_request["calls"][-1]["url"] == "https://api.iapp.co.th/v3/store/ekyc/face-recognition/import"
    
    # 6. recog_check
    client.face_recog_check("comp", "pass123")
    assert mock_sdk_request["calls"][-1]["url"] == "https://api.iapp.co.th/v3/store/ekyc/face-recognition/check"
    
    # 7. recog_export
    client.face_recog_export("comp", "pass123", "csv")
    assert mock_sdk_request["calls"][-1]["url"] == "https://api.iapp.co.th/v3/store/ekyc/face-recognition/export"
    
    # 8. recog_remove
    client.face_recog_remove("comp", "john", "pass123", "2026-06-10", "face-id-99")
    assert mock_sdk_request["calls"][-1]["url"] == "https://api.iapp.co.th/v3/store/ekyc/face-recognition/remove"

def test_score_configurations(mock_sdk_request):
    client = api("K")
    
    client.face_ver_config_score(0.5, 0.7, "comp", "pass")
    call_ver = mock_sdk_request["calls"][-1]
    assert call_ver["url"] == "https://api.iapp.co.th/face_config_score"
    assert call_ver["data"]["detect_value"] == 0.5
    assert call_ver["data"]["compare_value"] == 0.7
    
    client.face_detect_config_score(0.6, "comp", "pass")
    call_det = mock_sdk_request["calls"][-1]
    assert call_det["data"]["detect_value"] == 0.6
    
    client.face_recog_config_score(0.4, 0.8, "comp", "pass")
    call_rec = mock_sdk_request["calls"][-1]
    assert call_rec["data"]["recog_value"] == 0.8

def test_img_bg_removal(mock_sdk_request, tmp_path):
    f = tmp_path / "img.jpg"
    f.write_bytes(b"x")
    
    client = api("K")
    
    # Test base64
    client.img_bg_removal_base64(data_payload="YmFzZTY0c3Ry")
    call = mock_sdk_request["calls"][-1]
    assert call["url"] == "https://api.iapp.co.th/v3/store/smart-city/remove-background"
    assert call["files"][0][0] == "file"
    
    # Test file
    mock_sdk_request["response_data"]["json_payload"] = {}
    output_f = tmp_path / "out.jpg"
    client.img_bg_removal_file(str(f), output_path=str(output_f))
    call_file = mock_sdk_request["calls"][-1]
    assert call_file["url"] == "https://api.iapp.co.th/v3/store/smart-city/remove-background"
    assert os.path.exists(output_f)
