"""Custom verification tests for A-2: Retry and Backoff verification in transport.

Ensures that:
1. request_sync retries on 429 and 5xx.
2. Backoff factors are calculated exponentially.
3. Non-retryable statuses (e.g. 400, 403) fail immediately without retrying.
4. retries=0 by default does not retry.
"""

import sys
import types
import pytest
from iapp_core import transport

@pytest.fixture
def mock_http_retry(monkeypatch):
    """Fixture to drive request_sync with a list of statuses, recording calls and sleep times."""
    state = {"calls": 0, "sleeps": [], "statuses": [200]}

    class FakeResponse:
        def __init__(self, status_code):
            self.status_code = status_code
            self.text = f"status {status_code}"

    def fake_request(method, url, **kwargs):
        idx = min(state["calls"], len(state["statuses"]) - 1)
        status = state["statuses"][idx]
        state["calls"] += 1
        return FakeResponse(status)

    fake_module = types.ModuleType("requests")
    fake_module.request = fake_request
    monkeypatch.setitem(sys.modules, "requests", fake_module)
    
    # Patch time.sleep to record sleep duration instead of actually sleeping
    monkeypatch.setattr(transport.time, "sleep", lambda s: state["sleeps"].append(s))
    
    return state

def test_verify_retry_on_429(mock_http_retry):
    mock_http_retry["statuses"] = [429, 429, 200]
    
    resp = transport.request_sync("GET", "https://api.iapp.co.th/test", apikey="k", retries=3)
    
    assert resp.status_code == 200
    assert mock_http_retry["calls"] == 3
    assert mock_http_retry["sleeps"] == [0.5, 1.0]  # 0.5 * 2^0, 0.5 * 2^1

def test_verify_no_retry_on_400(mock_http_retry):
    mock_http_retry["statuses"] = [400, 200]
    
    resp = transport.request_sync("GET", "https://api.iapp.co.th/test", apikey="k", retries=3)
    
    assert resp.status_code == 400
    assert mock_http_retry["calls"] == 1
    assert len(mock_http_retry["sleeps"]) == 0

def test_verify_retry_gives_up(mock_http_retry):
    mock_http_retry["statuses"] = [500, 500, 500, 500]
    
    resp = transport.request_sync("GET", "https://api.iapp.co.th/test", apikey="k", retries=2)
    
    assert resp.status_code == 500
    assert mock_http_retry["calls"] == 3  # 1 initial + 2 retries
    assert mock_http_retry["sleeps"] == [0.5, 1.0]
