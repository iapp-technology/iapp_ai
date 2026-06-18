"""Custom verification tests for A-6: Release Automation.

Ensures that:
1. pyproject version bumping correctly replaces only the project version.
2. __version__ dunder bumping works correctly.
3. Package build order is core -> sdk -> mcp.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import release

def test_verify_set_project_version():
    content = 'name = "iapp-core"\nversion = "0.1.0"\n[dependencies]\niapp-core = "0.1.0"\n'
    updated = release.set_project_version(content, "0.2.0")
    
    assert 'version = "0.2.0"' in updated
    assert 'iapp-core = "0.1.0"' in updated  # should not change dependency version

def test_verify_set_dunder_version():
    content = '__version__ = "1.0.0"\n'
    updated = release.set_dunder_version(content, "1.1.0")
    assert updated == '__version__ = "1.1.0"\n'

def test_verify_build_order():
    # Dependency order check
    assert release.BUILD_ORDER == ["core", "sdk", "mcp"]
    assert "core" in release.PACKAGES
    assert "sdk" in release.PACKAGES
    assert "mcp" in release.PACKAGES
