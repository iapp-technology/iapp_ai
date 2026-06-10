"""Unit tests for A-7: central output-path API (defect D-09).

Domain methods currently hardcode ``media/...``. build_output_path() gives them
a single API: caller path wins, otherwise default to default_output_dir() which
is ``media`` unless IAPP_OUTPUT_DIR overrides it.
"""

import os

import pytest

from iapp_core import build_output_path, default_output_dir


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch):
    monkeypatch.delenv("IAPP_OUTPUT_DIR", raising=False)


def test_default_dir_is_media_without_env():
    assert default_output_dir() == "media"


def test_default_dir_honors_env(monkeypatch):
    monkeypatch.setenv("IAPP_OUTPUT_DIR", "/tmp/iapp-out")
    assert default_output_dir() == "/tmp/iapp-out"


def test_explicit_output_path_wins(tmp_path):
    target = tmp_path / "sub" / "voice.wav"
    result = build_output_path("ignored.wav", str(target))
    assert result == os.path.abspath(str(target))
    assert os.path.isdir(os.path.dirname(result))  # parent dir created


def test_default_falls_back_to_media_dir(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    result = build_output_path("result.png")
    assert result == os.path.join(str(tmp_path), "media", "result.png")
    assert os.path.isdir(os.path.join(str(tmp_path), "media"))


def test_env_dir_used_when_no_explicit_path(monkeypatch, tmp_path):
    out = tmp_path / "generated"
    monkeypatch.setenv("IAPP_OUTPUT_DIR", str(out))
    result = build_output_path("a.png")
    assert result == os.path.join(str(out), "a.png")
    assert os.path.isdir(str(out))
