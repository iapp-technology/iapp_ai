"""Shared configuration for iApp AI Marketplace clients."""

# Base URL for the iApp AI Marketplace API.
API_BASE = "https://api.iapp.co.th"

# Default per-request timeouts, in seconds. Kept as plain floats here so the
# sync (requests) path does not need httpx; the async path builds an
# httpx.Timeout from these values where httpx is available.
CONNECT_TIMEOUT = 15.0
READ_TIMEOUT = 300.0
