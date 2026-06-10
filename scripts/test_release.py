"""Unit tests for the A-6 release helper version-bump logic."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import release  # noqa: E402


def test_set_project_version_replaces_first_only():
    text = 'name = "x"\nversion = "1.2.3"\n[other]\nversion = "9.9.9"\n'
    out = release.set_project_version(text, "1.3.0")
    assert 'version = "1.3.0"' in out
    assert 'version = "9.9.9"' in out  # second untouched
    assert '"1.2.3"' not in out


def test_set_project_version_tolerates_spacing():
    assert release.set_project_version('version="0.1.0"', "0.2.0") == 'version = "0.2.0"'


def test_set_project_version_errors_when_absent():
    with pytest.raises(ValueError):
        release.set_project_version('name = "x"\n', "1.0.0")


def test_set_dunder_version():
    assert release.set_dunder_version('__version__ = "2.0.0"\n', "2.1.0") == '__version__ = "2.1.0"\n'


def test_set_dunder_version_noop_when_absent():
    text = "x = 1\n"
    assert release.set_dunder_version(text, "2.1.0") == text


def test_build_order_is_core_first():
    assert release.BUILD_ORDER[0] == "core"
    assert set(release.BUILD_ORDER) == set(release.PACKAGES)
