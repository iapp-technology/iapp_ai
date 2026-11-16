"""iapp_ai's copies of the iapp-core helpers that iapp-core 0.1.1, the newest on PyPI, lacks."""

import subprocess
import sys

import iapp_core
import pytest

from iapp_ai import _core_compat


def test_iapp_ai_works_with_an_iapp_core_without_the_helpers():
    # as with iapp-core 0.1.1 from PyPI, whose iapp_core has none of these names
    code = (
        "import iapp_core\n"
        "for name in ('build_output_path', 'build_url', 'default_output_dir', 'open_input_files'):\n"
        "    if hasattr(iapp_core, name):\n"
        "        delattr(iapp_core, name)\n"
        "from iapp_ai import api\n"
        "print(api('key').apikey)\n"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "key"


# While this repo's iapp-core has the helpers, the copies must behave the same.


@pytest.mark.parametrize(
    "args",
    [
        ("https://api.iapp.co.th", "translate/auto", {"text": "สวัสดี", "lang": None}),
        ("https://api.iapp.co.th/", "/v3/store/ocr", None),
        ("https://api.iapp.co.th", "", {"ids": [1, 2]}),
        ("https://api.iapp.co.th", "path", {"a": None}),
    ],
)
def test_build_url_matches_iapp_core(args):
    assert _core_compat.build_url(*args) == iapp_core.build_url(*args)


def test_build_output_path_matches_iapp_core(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("IAPP_OUTPUT_DIR", raising=False)
    assert _core_compat.build_output_path("kaitom.wav") == iapp_core.build_output_path("kaitom.wav")
    monkeypatch.setenv("IAPP_OUTPUT_DIR", str(tmp_path / "out"))
    assert _core_compat.build_output_path("kaitom.wav") == iapp_core.build_output_path("kaitom.wav")
    assert (tmp_path / "out").is_dir()
    explicit = str(tmp_path / "chosen" / "bg.jpg")
    assert _core_compat.build_output_path("bg.jpg", explicit) == iapp_core.build_output_path("bg.jpg", explicit)


def test_open_input_files_closes_every_handle(tmp_path):
    paths = []
    for name in ("front.jpg", "back.jpg"):
        path = tmp_path / name
        path.write_bytes(name.encode())
        paths.append(str(path))
    with _core_compat.open_input_files(paths) as handles:
        assert [handle.read() for handle in handles] == [b"front.jpg", b"back.jpg"]
    assert all(handle.closed for handle in handles)


def test_open_input_files_closes_on_error(tmp_path):
    path = tmp_path / "front.jpg"
    path.write_bytes(b"x")
    with pytest.raises(RuntimeError):
        with _core_compat.open_input_files([str(path)]) as handles:
            raise RuntimeError("upload failed")
    assert handles[0].closed
