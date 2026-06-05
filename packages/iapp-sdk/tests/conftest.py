"""Pytest configuration for the iApp AI SDK test suite.

Live integration tests (files named ``test_live_*``) hit the real
``api.iapp.co.th`` and need a valid ``IAPP_API_KEY``. They are skipped
automatically when the key is not set, so the offline suite stays green in CI.
"""

import os

import pytest


def pytest_collection_modifyitems(config, items):
    if os.environ.get("IAPP_API_KEY"):
        return
    skip_live = pytest.mark.skip(
        reason="live integration test — set IAPP_API_KEY to run"
    )
    for item in items:
        if "test_live_" in os.path.basename(str(item.fspath)):
            item.add_marker(skip_live)
