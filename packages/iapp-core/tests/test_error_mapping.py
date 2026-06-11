"""Unit tests for A-4: HTTP status -> actionable message mapping.

Confirms the main statuses (400/401/402/403/404/413/429/500) each get a
specific message, and anything else falls back to the generic one.
"""

import pytest

from iapp_core.errors import status_error_message

MAPPED = [400, 401, 402, 403, 404, 413, 429, 500]


@pytest.mark.parametrize("status", MAPPED)
def test_mapped_status_mentions_its_code(status):
    msg = status_error_message(status, "body")
    assert str(status) in msg
    assert msg.startswith("Error:")


def test_400_403_404_500_were_added():
    for status in (400, 403, 404, 500):
        msg = status_error_message(status, "detail-text")
        # Specific (not the generic "request failed with status N") message.
        assert "request failed with status" not in msg


def test_body_snippet_included_and_truncated():
    long_body = "x" * 1000
    msg = status_error_message(500, long_body)
    assert "x" * 500 in msg
    assert "x" * 501 not in msg


def test_unmapped_status_uses_generic_message():
    msg = status_error_message(418, "teapot")
    assert "request failed with status 418" in msg
