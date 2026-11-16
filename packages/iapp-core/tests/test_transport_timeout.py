"""Unit tests for the sync transport timeout default (defect D-13).

``request_sync`` must always send a timeout to ``requests`` so a stalled
connection cannot hang the caller forever. By default it uses the
``(CONNECT_TIMEOUT, READ_TIMEOUT)`` pair from :mod:`iapp_core.config`; an
explicit ``timeout`` argument still overrides it.
"""

import sys
import types

import pytest

from iapp_core import transport
from iapp_core.config import CONNECT_TIMEOUT, READ_TIMEOUT


@pytest.fixture
def captured_requests(monkeypatch):
    """Replace the ``requests`` module with a recorder for request_sync."""
    calls = {}

    class _Resp:
        status_code = 200
        text = ""

    def fake_request(method, url, **kwargs):
        calls.clear()
        calls.update(method=method, url=url, **kwargs)
        return _Resp()

    fake_requests = types.ModuleType("requests")
    fake_requests.request = fake_request
    monkeypatch.setitem(sys.modules, "requests", fake_requests)
    return calls


def test_default_timeout_is_config_tuple(captured_requests):
    transport.request_sync("GET", "https://example.com", apikey="K")
    assert captured_requests["timeout"] == (CONNECT_TIMEOUT, READ_TIMEOUT)


def test_explicit_timeout_overrides_default(captured_requests):
    transport.request_sync("GET", "https://example.com", apikey="K", timeout=5.0)
    assert captured_requests["timeout"] == 5.0


def test_timeout_is_never_none(captured_requests):
    transport.request_sync("POST", "https://example.com", apikey="K")
    assert captured_requests["timeout"] is not None
