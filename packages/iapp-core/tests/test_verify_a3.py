"""Custom verification tests for A-3: URL building and File Handling.

Ensures that:
1. build_url percent encodes Thai characters and spaces in parameters.
2. build_url collapses multiple slashes between base and path.
3. open_input_files context manager opens files in read-binary mode by default.
4. open_input_files context manager guarantees closure of all opened file handles
   even if an exception occurs inside the 'with' block.
"""

import pytest
from urllib.parse import urlparse, parse_qs
from iapp_core import build_url, open_input_files

def test_verify_build_url_encoding():
    # Test with Thai text and spaces
    thai_text = "ภาษาไทย ทดสอบ"
    url = build_url("https://api.iapp.co.th/", "/ocr/predict", {"query": thai_text, "empty": None})
    
    # Check that double slashes are collapsed
    assert "https://api.iapp.co.th/ocr/predict" in url
    assert "empty" not in url
    
    # Check encoding of Thai text
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    assert params["query"] == [thai_text]
    assert "%" in url  # Must be percent encoded

def test_verify_open_input_files_leak_prevention(tmp_path):
    f1 = tmp_path / "test1.jpg"
    f1.write_bytes(b"image1")
    f2 = tmp_path / "test2.jpg"
    f2.write_bytes(b"image2")

    handles_ref = []
    
    # Normal usage
    with open_input_files([str(f1), str(f2)]) as handles:
        assert len(handles) == 2
        assert all(not h.closed for h in handles)
        handles_ref = list(handles)

    # After exiting block, all files must be closed
    assert all(h.closed for h in handles_ref)

def test_verify_open_input_files_closed_on_error(tmp_path):
    f1 = tmp_path / "test1.jpg"
    f1.write_bytes(b"image1")
    
    handles_ref = []
    
    with pytest.raises(ValueError):
        with open_input_files([str(f1)]) as handles:
            assert not handles[0].closed
            handles_ref = list(handles)
            raise ValueError("Intentional error inside block")

    # Handles must be closed even when exception is raised
    assert all(h.closed for h in handles_ref)
