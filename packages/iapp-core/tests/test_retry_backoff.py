"""Unit tests for A-2: opt-in retry + backoff in request_sync.

Retries are off by default (backward compatible) and, when enabled, fire on 429
and 5xx with exponential backoff. ``time.sleep`` is patched so tests don't wait.
"""

import sys
import types

import pytest

from iapp_core import transport


@pytest.fixture
def fake_http(monkeypatch):
    """Drive request_sync with a scripted sequence of status codes."""
    state = {"statuses": [200], "calls": 0, "sleeps": []}

    class _Resp:
        def __init__(self, status):
            self.status_code = status
            self.text = ""

    def fake_request(method, url, **kwargs):
        i = min(state["calls"], len(state["statuses"]) - 1)
        status = state["statuses"][i]
        state["calls"] += 1
        return _Resp(status)

    fake_requests = types.ModuleType("requests")
    fake_requests.request = fake_request
    monkeypatch.setitem(sys.modules, "requests", fake_requests)
    monkeypatch.setattr(transport.time, "sleep", lambda s: state["sleeps"].append(s))
    return state


def test_no_retry_by_default(fake_http):
    fake_http["statuses"] = [429, 200]
    resp = transport.request_sync("GET", "https://x.test", apikey="K")
    assert resp.status_code == 429  # not retried
    assert fake_http["calls"] == 1


def test_retries_on_429_then_succeeds(fake_http):
    fake_http["statuses"] = [429, 200]
    resp = transport.request_sync("GET", "https://x.test", apikey="K", retries=3)
    assert resp.status_code == 200
    assert fake_http["calls"] == 2
    assert fake_http["sleeps"] == [0.5]  # backoff_factor * 2**0


def test_retries_on_5xx(fake_http):
    fake_http["statuses"] = [503, 502, 200]
    resp = transport.request_sync("GET", "https://x.test", apikey="K", retries=3)
    assert resp.status_code == 200
    assert fake_http["calls"] == 3
    assert fake_http["sleeps"] == [0.5, 1.0]  # exponential


def test_gives_up_after_retries_exhausted(fake_http):
    fake_http["statuses"] = [429]  # always 429
    resp = transport.request_sync("GET", "https://x.test", apikey="K", retries=2)
    assert resp.status_code == 429
    assert fake_http["calls"] == 3  # 1 initial + 2 retries


def test_4xx_other_than_429_not_retried(fake_http):
    fake_http["statuses"] = [403, 200]
    resp = transport.request_sync("GET", "https://x.test", apikey="K", retries=3)
    assert resp.status_code == 403
    assert fake_http["calls"] == 1
