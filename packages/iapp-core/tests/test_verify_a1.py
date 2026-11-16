"""Custom verification tests for A-1: Default timeout verification in transport.

Ensures that:
1. request_sync defaults to (CONNECT_TIMEOUT, READ_TIMEOUT).
2. Explicit timeout overrides the default.
3. Every request has a timeout (it is never None).
"""

import sys
import types
import pytest
from iapp_core import transport
from iapp_core.config import CONNECT_TIMEOUT, READ_TIMEOUT

@pytest.fixture
def mock_requests(monkeypatch):
    """Fixture to mock the requests module and record the kwargs passed to request."""
    recorded_kwargs = {}

    class FakeResponse:
        status_code = 200
        text = '{"status": "ok"}'
        def json(self):
            return {"status": "ok"}

    def fake_request(method, url, **kwargs):
        recorded_kwargs.clear()
        recorded_kwargs.update(kwargs)
        return FakeResponse()

    fake_module = types.ModuleType("requests")
    fake_module.request = fake_request
    monkeypatch.setitem(sys.modules, "requests", fake_module)
    return recorded_kwargs

def test_verify_default_timeout(mock_requests):
    # Call request_sync without explicit timeout
    transport.request_sync("GET", "https://api.iapp.co.th/test", apikey="test_key")
    
    # Verify it uses the CONNECT_TIMEOUT and READ_TIMEOUT from config
    assert "timeout" in mock_requests
    assert mock_requests["timeout"] == (CONNECT_TIMEOUT, READ_TIMEOUT)
    assert mock_requests["timeout"] is not None

def test_verify_explicit_timeout_override(mock_requests):
    # Call request_sync with explicit float timeout
    transport.request_sync("GET", "https://api.iapp.co.th/test", apikey="test_key", timeout=5.0)
    assert mock_requests["timeout"] == 5.0

    # Call request_sync with explicit tuple timeout
    transport.request_sync("GET", "https://api.iapp.co.th/test", apikey="test_key", timeout=(2.0, 10.0))
    assert mock_requests["timeout"] == (2.0, 10.0)
