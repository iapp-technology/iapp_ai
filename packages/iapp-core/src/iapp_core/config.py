"""Shared configuration for iApp AI Marketplace clients."""

import os

# Base URL for the iApp AI Marketplace API.
API_BASE = "https://api.iapp.co.th"


def _env_float(name: str, default: float) -> float:
    """Read a positive float from the environment, ignoring junk values."""
    try:
        value = float(os.environ[name])
        return value if value > 0 else default
    except (KeyError, ValueError):
        return default


# Default per-request timeouts, in seconds. Kept as plain floats here so the
# sync (requests) path does not need httpx; the async path builds an
# httpx.Timeout from these values where httpx is available.
#
# READ_TIMEOUT covers the whole upstream job, not just the first byte: speech-to-text
# transcribes the clip before responding, so a 10-minute file measured 160-280s of
# proxy time in production. The old 300s ceiling sat inside that spread, so the
# longest clips had the client hang up mid-transcription — the gateway logged 499,
# the user got an error, and the work was thrown away after the audio had already
# been processed. 30 minutes leaves room for hour-long audio.
CONNECT_TIMEOUT = _env_float("IAPP_CONNECT_TIMEOUT", 15.0)
READ_TIMEOUT = _env_float("IAPP_READ_TIMEOUT", 1800.0)
