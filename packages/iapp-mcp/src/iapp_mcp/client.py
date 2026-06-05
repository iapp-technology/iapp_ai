"""Backwards-compatible shim over :mod:`iapp_core`.

The HTTP client, error type and formatting helpers now live in the shared
``iapp_core`` package so the SDK and the MCP server have a single source of
truth. This module re-exports them under the names the tool modules already
import, so ``iapp_mcp.tools.*`` need no changes:

    from ..client import IAppAPIError, format_json_response, request, save_binary, save_pcm_as_wav
"""

from iapp_core.config import API_BASE
from iapp_core.errors import IAppAPIError
from iapp_core.formatting import (
    format_json_response,
    resolve_input_file,
    resolve_output_path,
    save_binary,
    save_pcm_as_wav,
)
from iapp_core.transport import request_async as request

__all__ = [
    "API_BASE",
    "IAppAPIError",
    "format_json_response",
    "request",
    "resolve_input_file",
    "resolve_output_path",
    "save_binary",
    "save_pcm_as_wav",
]
