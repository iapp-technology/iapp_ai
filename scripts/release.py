#!/usr/bin/env python3
"""Release automation for the iApp AI monorepo (task A-6).

Subcommands::

    python scripts/release.py build [--tag TAG]
        Build into ./dist. With a release tag ``<PyPI name>-v<version>``, such
        as ``iapp-ai-v2.0.0``, build only that package, once the tag's version
        matches its pyproject.toml. Without one, build every package in
        dependency order (core -> sdk -> mcp): core first because the sdk and
        mcp depend on it.

    python scripts/release.py bump <core|sdk|mcp> <version>
        Set one package's version in its pyproject.toml and keep its
        __init__ __version__ in sync.

    python scripts/release.py check [--tag TAG]
        Check the files in ./dist, only the tagged package's with a tag: run
        ``twine check --strict``, pip install the wheels into a throwaway venv,
        then import each package and confirm its __version__ matches the wheel
        version. iapp-ai goes in with its nlp extra, and its offline Thai NLP
        is checked too: the model files against the SHA-256 in their manifest,
        the license files, and one sentence split into words. A second venv
        installs iapp-ai without the extra, where the SDK and normalize must
        import and the word tokenizer must say to install the extra.
        Needs twine, e.g. ``uv run --with twine python scripts/release.py check``.

Build uses ``python -m build`` (PEP 517), so no extra tooling is required; the
GitHub Actions release workflow calls the same entry point.
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

# name -> (package dir, module __init__ that carries __version__)
PACKAGES = {
    "core": ("packages/iapp-core", "packages/iapp-core/src/iapp_core/__init__.py"),
    "sdk": ("packages/iapp-sdk", "packages/iapp-sdk/src/iapp_ai/__init__.py"),
    "mcp": ("packages/iapp-mcp", "packages/iapp-mcp/src/iapp_mcp/__init__.py"),
}
# core first: sdk and mcp depend on it.
BUILD_ORDER = ["core", "sdk", "mcp"]
# The wheel installed with an extra in check(), and that extra
NLP_WHEEL, NLP_EXTRA = "iapp_ai", "nlp"

_VERSION_RE = re.compile(r'^version\s*=\s*"([^"]*)"', re.MULTILINE)
_DUNDER_RE = re.compile(r'^__version__\s*=\s*"[^"]*"', re.MULTILINE)
_NAME_RE = re.compile(r'^name\s*=\s*"([^"]*)"', re.MULTILINE)
# <PyPI name>-v<version>; the name may contain "-v", the version starts with a digit
_TAG_RE = re.compile(r"^(?P<name>.+)-v(?P<version>[0-9]\S*)$")

# Run in the throwaway venv after installing the iapp-ai wheel with its nlp extra
NLP_SMOKE_TEST = """
import hashlib, json
from importlib.metadata import files
from importlib.resources import files as package_files
from iapp_ai.nlp import word_tokenize

latte = package_files("iapp_ai.nlp") / "data" / "latte"
manifest = json.loads((latte / "manifest.json").read_text(encoding="utf-8"))
model = manifest["model"]
for name, digest in {model["file"]: model["sha256"], **manifest["files_sha256"]}.items():
    assert hashlib.sha256((latte / name).read_bytes()).hexdigest() == digest, f"{name} does not match manifest.json"
licenses = {str(f).split("/licenses/", 1)[1] for f in files("iapp-ai") if "/licenses/" in str(f)}
for name in ("LICENSE", "LICENSE-APACHE", "LICENSES/CC-BY-SA-4.0.txt", "LICENSES/Unicode-DFS-2016.txt", "NOTICE"):
    assert name in licenses, f"{name} is missing from the wheel"
words = word_tokenize("แม่น้ำเจ้าพระยาไหลผ่านกรุงเทพ")
assert words == ["แม่น้ำ", "เจ้าพระยา", "ไหล", "ผ่าน", "กรุงเทพ"], words
print("ok iapp_ai.nlp: model files match manifest.json, license files present, words:", "|".join(words))
"""

# Run in a second throwaway venv after installing the iapp-ai wheel without its nlp extra
WITHOUT_NLP_EXTRA_TEST = """
import importlib.util
from iapp_ai import api
from iapp_ai.nlp import normalize, word_tokenize

assert importlib.util.find_spec("numpy") is None and importlib.util.find_spec("onnxruntime") is None, (
    "numpy or onnxruntime is installed without the nlp extra"
)
assert normalize("เเปลก") == "แปลก"
try:
    word_tokenize("ไปเชียงใหม่")
except ImportError as e:
    assert 'pip install "iapp-ai[nlp]"' in str(e), e
else:
    raise AssertionError("word_tokenize worked without the nlp extra")
print("ok iapp_ai without the nlp extra: the SDK and normalize import, and the tokenizer names the extra")
"""


def set_project_version(pyproject_text: str, version: str) -> str:
    """Return ``pyproject_text`` with the first ``version = "..."`` set to ``version``."""
    new_text, n = _VERSION_RE.subn(f'version = "{version}"', pyproject_text, count=1)
    if n != 1:
        raise ValueError("no `version = \"...\"` line found in pyproject.toml")
    return new_text


def set_dunder_version(init_text: str, version: str) -> str:
    """Return ``init_text`` with ``__version__ = "..."`` set to ``version`` (if present)."""
    new_text, _ = _DUNDER_RE.subn(f'__version__ = "{version}"', init_text, count=1)
    return new_text


def project_name(pyproject_text: str) -> str:
    """Return the first ``name = "..."`` in pyproject.toml as a wheel name (``-`` -> ``_``)."""
    return _pypi_name(pyproject_text).replace("-", "_")


def project_version(pyproject_text: str) -> str:
    """Return the first ``version = "..."`` in pyproject.toml."""
    m = _VERSION_RE.search(pyproject_text)
    if not m:
        raise ValueError("no `version = \"...\"` line found in pyproject.toml")
    return m.group(1)


def _pypi_name(pyproject_text: str) -> str:
    m = _NAME_RE.search(pyproject_text)
    if not m:
        raise ValueError("no `name = \"...\"` line found in pyproject.toml")
    return m.group(1)


def projects() -> dict[str, tuple[str, str]]:
    """Map each package to the (PyPI name, version) in its pyproject.toml."""
    out = {}
    for pkg, (pkg_dir, _) in PACKAGES.items():
        text = (ROOT / pkg_dir / "pyproject.toml").read_text()
        out[pkg] = (_pypi_name(text), project_version(text))
    return out


def tag_package(tag: str, projects: dict[str, tuple[str, str]]) -> str:
    """Return the package that release tag ``tag`` names, once its version matches.

    ``projects`` maps each package to its (PyPI name, version), as :func:`projects`
    gives; with ``{"sdk": ("iapp-ai", "2.0.0")}``, ``iapp-ai-v2.0.0`` gives ``"sdk"``.
    """
    m = _TAG_RE.match(tag)
    for pkg, (name, version) in projects.items():
        if m and m.group("name") == name:
            if m.group("version") != version:
                raise ValueError(
                    f"tag {tag} is for {name} {m.group('version')}, "
                    f"but its pyproject.toml says version {version}"
                )
            return pkg
    examples = ", ".join(f"{name}-v{version}" for name, version in projects.values())
    raise ValueError(f"{tag!r} is not a release tag: use <PyPI name>-v<version>, e.g. {examples}")


def wheel_versions(wheel_names: list[str]) -> dict[str, str]:
    """Map wheel name to version from filenames like ``iapp_core-0.1.0-py3-none-any.whl``."""
    return dict(name.split("-")[:2] for name in wheel_names)


def with_nlp_extra(wheels: list[Path]) -> list[str]:
    """pip requirements for ``wheels``, the iapp-ai one with its nlp extra: ``.../iapp_ai-2.0.0-py3-none-any.whl[nlp]``."""
    return [f"{whl}[{NLP_EXTRA}]" if whl.name.split("-")[0] == NLP_WHEEL else str(whl) for whl in wheels]


def dist_files(wheel_names: set[str], dist: Path) -> list[Path]:
    """The wheels and sdists in ``dist`` of the packages with these wheel names."""
    return sorted(
        f for f in dist.glob("*")
        if f.name.endswith((".whl", ".tar.gz")) and f.name.split("-")[0] in wheel_names
    )


def _packages(tag: str | None) -> list[str]:
    if tag is None:
        return BUILD_ORDER
    try:
        return [tag_package(tag, projects())]
    except ValueError as e:
        raise SystemExit(str(e)) from None


def bump(pkg: str, version: str) -> None:
    if pkg not in PACKAGES:
        raise SystemExit(f"unknown package {pkg!r}; choose from {', '.join(PACKAGES)}")
    pkg_dir, init_rel = PACKAGES[pkg]
    pyproject = ROOT / pkg_dir / "pyproject.toml"
    pyproject.write_text(set_project_version(pyproject.read_text(), version))
    init_path = ROOT / init_rel
    if init_path.exists():
        init_path.write_text(set_dunder_version(init_path.read_text(), version))
    print(f"bumped {pkg} -> {version}")


def build(pkgs: list[str]) -> None:
    DIST.mkdir(exist_ok=True)
    for pkg in pkgs:
        pkg_dir = ROOT / PACKAGES[pkg][0]
        print(f"== building {pkg} ({pkg_dir.name}) ==")
        subprocess.run(
            [sys.executable, "-m", "build", "--outdir", str(DIST), str(pkg_dir)],
            check=True,
        )
    print(f"built {len(pkgs)} package(s) into {DIST}")


def check(pkgs: list[str]) -> None:
    names = {pkg: project_name((ROOT / PACKAGES[pkg][0] / "pyproject.toml").read_text()) for pkg in pkgs}
    files = dist_files(set(names.values()), DIST)
    wheels = [f for f in files if f.suffix == ".whl"]
    if not wheels:
        raise SystemExit(f"no wheels in {DIST}; run `build` first")
    if importlib.util.find_spec("twine") is None:
        raise SystemExit("check needs twine: uv run --with twine python scripts/release.py check")
    subprocess.run([sys.executable, "-m", "twine", "check", "--strict", *map(str, files)], check=True)
    versions = wheel_versions([whl.name for whl in wheels])
    with tempfile.TemporaryDirectory() as tmp:
        py = _clean_venv(tmp)
        # all wheels in one call so iapp-core resolves from ./dist, not PyPI, when it was built too
        subprocess.run([py, "-m", "pip", "install", *with_nlp_extra(wheels)], check=True)
        for pkg in pkgs:
            name = names[pkg]
            if name not in versions:
                raise SystemExit(f"no wheel for {pkg} ({name}) in {DIST}")
            mod = Path(PACKAGES[pkg][1]).parent.name
            want = versions[name]
            # -I: import the installed package, never one from the current directory
            subprocess.run(
                [py, "-I", "-c", f"import {mod}; assert {mod}.__version__ == {want!r}, {mod}.__version__"],
                check=True,
            )
            print(f"ok {mod} {want}", flush=True)  # before the smoke test's own output
            if name == NLP_WHEEL:
                subprocess.run([py, "-I", "-c", NLP_SMOKE_TEST], check=True)
    if NLP_WHEEL in names.values():
        with tempfile.TemporaryDirectory() as tmp:
            py = _clean_venv(tmp)
            subprocess.run([py, "-m", "pip", "install", *map(str, wheels)], check=True)
            subprocess.run([py, "-I", "-c", WITHOUT_NLP_EXTRA_TEST], check=True)
    print(f"checked {len(files)} files and installed and imported {len(wheels)} wheel(s) in a clean venv")


def _clean_venv(tmp: str) -> str:
    """Make a venv in ``tmp`` and return its python: the repo .venv has editable installs that would always import."""
    venv.create(tmp, with_pip=True)
    return str(Path(tmp) / "bin" / "python")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="iApp AI monorepo release helper")
    sub = parser.add_subparsers(dest="cmd", required=True)
    tag_help = "release tag <PyPI name>-v<version>, e.g. iapp-ai-v2.0.0: only that package"
    build_p = sub.add_parser("build", help="build core -> sdk -> mcp, or the tagged package, into ./dist")
    build_p.add_argument("--tag", help=tag_help)
    check_p = sub.add_parser("check", help="twine check the ./dist files, then install and import the wheels")
    check_p.add_argument("--tag", help=tag_help)
    bump_p = sub.add_parser("bump", help="set a package version")
    bump_p.add_argument("package", choices=list(PACKAGES))
    bump_p.add_argument("version")
    args = parser.parse_args(argv)
    if args.cmd == "build":
        build(_packages(args.tag))
    elif args.cmd == "check":
        check(_packages(args.tag))
    elif args.cmd == "bump":
        bump(args.package, args.version)


if __name__ == "__main__":
    main()
