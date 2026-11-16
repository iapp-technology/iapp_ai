"""Custom verification tests for A-7: Output Path API.

Ensures that:
1. default_output_dir defaults to "media" without env variable.
2. default_output_dir respects IAPP_OUTPUT_DIR environment variable.
3. build_output_path uses explicit output_path and overrides the default folder.
4. build_output_path automatically creates parent folders for the output path.
"""

import os
import pytest
from iapp_core import default_output_dir, build_output_path

@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    monkeypatch.delenv("IAPP_OUTPUT_DIR", raising=False)

def test_verify_default_output_dir_without_env():
    assert default_output_dir() == "media"

def test_verify_default_output_dir_with_env(monkeypatch):
    monkeypatch.setenv("IAPP_OUTPUT_DIR", "/custom/path/out")
    assert default_output_dir() == "/custom/path/out"

def test_verify_build_output_path_explicit_wins(tmp_path):
    # If path is given, it wins, and the parent folder is created
    target_file = tmp_path / "custom_folder" / "voice_out.wav"
    result = build_output_path("ignored.wav", str(target_file))
    
    assert result == os.path.abspath(str(target_file))
    assert os.path.isdir(os.path.dirname(result))  # folder custom_folder created

def test_verify_build_output_path_default_fallback(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    # Default is current_dir/media/result.png
    result = build_output_path("result.png")
    
    assert result == os.path.join(str(tmp_path), "media", "result.png")
    assert os.path.isdir(os.path.join(str(tmp_path), "media"))
