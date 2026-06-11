"""Custom verification tests for A-4: Error mapping verification.

Ensures that:
1. Mapped error messages exist for 400, 403, 404, 500 status codes.
2. request_sync raises IAppAPIError when raise_for_error=True.
3. The raised error message contains the specific descriptive wording for the status.
"""

import sys
import types
import pytest
from iapp_core import request_sync, IAppAPIError

@pytest.fixture
def mock_http_error(monkeypatch):
    """Fixture to mock requests returning a specific HTTP status code."""
    state = {"status_code": 500, "text": "Server error details"}

    class FakeResponse:
        def __init__(self, status_code, text):
            self.status_code = status_code
            self.text = text

    def fake_request(method, url, **kwargs):
        return FakeResponse(state["status_code"], state["text"])

    fake_module = types.ModuleType("requests")
    fake_module.request = fake_request
    monkeypatch.setitem(sys.modules, "requests", fake_module)
    
    return state

def test_verify_error_mapping_400(mock_http_error):
    mock_http_error["status_code"] = 400
    mock_http_error["text"] = "missing param x"
    
    with pytest.raises(IAppAPIError) as exc_info:
        request_sync("GET", "https://api.iapp.co.th/test", apikey="k", raise_for_error=True)
    
    assert "Bad request (400)" in str(exc_info.value)
    assert "missing param x" in str(exc_info.value)

def test_verify_error_mapping_403(mock_http_error):
    mock_http_error["status_code"] = 403
    mock_http_error["text"] = "plan expired"
    
    with pytest.raises(IAppAPIError) as exc_info:
        request_sync("GET", "https://api.iapp.co.th/test", apikey="k", raise_for_error=True)
    
    assert "Access forbidden (403)" in str(exc_info.value)
    assert "plan expired" in str(exc_info.value)

def test_verify_error_mapping_404(mock_http_error):
    mock_http_error["status_code"] = 404
    
    with pytest.raises(IAppAPIError) as exc_info:
        request_sync("GET", "https://api.iapp.co.th/test", apikey="k", raise_for_error=True)
    
    assert "Not found (404)" in str(exc_info.value)

def test_verify_error_mapping_500(mock_http_error):
    mock_http_error["status_code"] = 500
    mock_http_error["text"] = "internal crash"
    
    with pytest.raises(IAppAPIError) as exc_info:
        request_sync("GET", "https://api.iapp.co.th/test", apikey="k", raise_for_error=True)
    
    assert "iApp server error (500)" in str(exc_info.value)
    assert "internal crash" in str(exc_info.value)
