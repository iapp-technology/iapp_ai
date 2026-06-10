"""Unit tests for the A-3 central helpers: build_url + open_input_files.

These back defect fixes D-05 (un-encoded Thai in URLs) and D-01 (leaked file
handles). The helpers are generic; domain methods wire them in separately.
"""

import warnings
from urllib.parse import parse_qs, urlparse

import pytest

from iapp_core import build_url, open_input_files


def test_build_url_joins_base_and_path():
    assert build_url("https://api.iapp.co.th", "translate/auto") == (
        "https://api.iapp.co.th/translate/auto"
    )


def test_build_url_single_slash_between_segments():
    # Trailing/leading slashes collapse to exactly one.
    assert build_url("https://api.iapp.co.th/", "/asr") == "https://api.iapp.co.th/asr"


def test_build_url_percent_encodes_thai():
    url = build_url("https://api.iapp.co.th", "translate/auto", {"text": "สวัสดี"})
    parsed = urlparse(url)
    # Raw Thai must not appear unencoded in the query string...
    assert "สวัสดี" not in url
    # ...but must round-trip back to the original value.
    assert parse_qs(parsed.query)["text"] == ["สวัสดี"]


def test_build_url_drops_none_params():
    url = build_url("https://x.test", "p", {"a": "1", "b": None})
    assert url == "https://x.test/p?a=1"


def test_build_url_no_query_when_params_empty():
    assert build_url("https://x.test", "p", {}) == "https://x.test/p"


def test_open_input_files_yields_open_handles_and_closes(tmp_path):
    f1 = tmp_path / "a.bin"
    f1.write_bytes(b"a")
    f2 = tmp_path / "b.bin"
    f2.write_bytes(b"b")
    with open_input_files([str(f1), str(f2)]) as handles:
        assert len(handles) == 2
        assert all(not h.closed for h in handles)
        captured = handles
    assert all(h.closed for h in captured)  # closed on normal exit


def test_open_input_files_closes_on_exception(tmp_path):
    f = tmp_path / "a.bin"
    f.write_bytes(b"a")
    captured = []
    with pytest.raises(RuntimeError):
        with open_input_files([str(f)]) as handles:
            captured = handles
            raise RuntimeError("boom")
    assert captured and captured[0].closed  # closed even when body raises


def test_open_input_files_no_resource_warning(tmp_path, recwarn):
    f = tmp_path / "a.bin"
    f.write_bytes(b"a")
    warnings.simplefilter("always")
    with open_input_files([str(f)]):
        pass
    assert not [w for w in recwarn.list if issubclass(w.category, ResourceWarning)]
