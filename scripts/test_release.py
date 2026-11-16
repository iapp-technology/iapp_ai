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


def test_project_name_uses_wheel_spelling():
    assert release.project_name('[project]\nname = "iapp-ai"\nversion = "2.0.0"\n') == "iapp_ai"


def test_project_name_errors_when_absent():
    with pytest.raises(ValueError):
        release.project_name('version = "1.0.0"\n')


def test_wheel_versions_from_filenames():
    names = ["iapp_core-0.1.0-py3-none-any.whl", "iapp_ai-2.0.0-py3-none-any.whl"]
    assert release.wheel_versions(names) == {"iapp_core": "0.1.0", "iapp_ai": "2.0.0"}


def test_project_version():
    assert release.project_version('[project]\nname = "iapp-ai"\nversion = "2.0.0"\n') == "2.0.0"


def test_project_version_errors_when_absent():
    with pytest.raises(ValueError):
        release.project_version('name = "x"\n')


def test_projects_read_each_pyproject():
    projects = release.projects()
    assert set(projects) == set(release.PACKAGES)
    assert projects["sdk"][0] == "iapp-ai"


PROJECTS = {
    "core": ("iapp-core", "0.1.0"),
    "sdk": ("iapp-ai", "2.0.0"),
    "mcp": ("iapp-mcp", "2.0.0"),
}


@pytest.mark.parametrize(
    "tag, pkg",
    [("iapp-core-v0.1.0", "core"), ("iapp-ai-v2.0.0", "sdk"), ("iapp-mcp-v2.0.0", "mcp")],
)
def test_tag_package(tag, pkg):
    assert release.tag_package(tag, PROJECTS) == pkg


def test_tag_package_needs_the_pyproject_version():
    with pytest.raises(ValueError, match="pyproject.toml says version 2.0.0"):
        release.tag_package("iapp-ai-v2.0.1", PROJECTS)


# iapp-nlp-v0.1.0: iapp-nlp is no longer released from here; it moved into iapp-ai as iapp_ai.nlp
@pytest.mark.parametrize(
    "tag", ["v2.0.0", "iapp-ai-2.0.0", "iapp-ai-v", "ai-v2.0.0", "iapp-vision-v1.0.0", "iapp-nlp-v0.1.0"]
)
def test_tag_package_rejects_other_tags(tag):
    with pytest.raises(ValueError, match="not a release tag"):
        release.tag_package(tag, PROJECTS)


def test_dist_files_picks_one_package(tmp_path):
    for name in [
        "iapp_ai-2.0.0-py3-none-any.whl", "iapp_ai-2.0.0.tar.gz",
        "iapp_core-0.1.0-py3-none-any.whl", "iapp_core-0.1.0.tar.gz", ".gitignore",
    ]:
        (tmp_path / name).touch()
    assert [f.name for f in release.dist_files({"iapp_ai"}, tmp_path)] == [
        "iapp_ai-2.0.0-py3-none-any.whl", "iapp_ai-2.0.0.tar.gz",
    ]


def test_with_nlp_extra_adds_the_extra_to_iapp_ai_only():
    wheels = [Path("dist/iapp_core-0.1.0-py3-none-any.whl"), Path("dist/iapp_ai-2.0.0-py3-none-any.whl")]
    assert release.with_nlp_extra(wheels) == [
        "dist/iapp_core-0.1.0-py3-none-any.whl", "dist/iapp_ai-2.0.0-py3-none-any.whl[nlp]",
    ]
