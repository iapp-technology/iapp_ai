#!/usr/bin/env python3
"""Release automation for the iApp AI monorepo (task A-6).

Subcommands::

    python scripts/release.py build
        Build all three packages in dependency order (core -> sdk -> mcp) into
        ./dist with a single command. core is built first because the sdk and
        mcp depend on it.

    python scripts/release.py bump <core|sdk|mcp> <version>
        Set one package's version in its pyproject.toml and keep its
        __init__ __version__ in sync.

Build uses ``python -m build`` (PEP 517), so no extra tooling is required; the
GitHub Actions release workflow calls the same entry point.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
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

_VERSION_RE = re.compile(r'^version\s*=\s*"[^"]*"', re.MULTILINE)
_DUNDER_RE = re.compile(r'^__version__\s*=\s*"[^"]*"', re.MULTILINE)


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


def build() -> None:
    DIST.mkdir(exist_ok=True)
    for pkg in BUILD_ORDER:
        pkg_dir = ROOT / PACKAGES[pkg][0]
        print(f"== building {pkg} ({pkg_dir.name}) ==")
        subprocess.run(
            [sys.executable, "-m", "build", "--outdir", str(DIST), str(pkg_dir)],
            check=True,
        )
    print(f"built {len(BUILD_ORDER)} packages into {DIST}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="iApp AI monorepo release helper")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build", help="build core -> sdk -> mcp into ./dist")
    bump_p = sub.add_parser("bump", help="set a package version")
    bump_p.add_argument("package", choices=list(PACKAGES))
    bump_p.add_argument("version")
    args = parser.parse_args(argv)
    if args.cmd == "build":
        build()
    elif args.cmd == "bump":
        bump(args.package, args.version)


if __name__ == "__main__":
    main()
