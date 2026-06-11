"""iapp_core — shared transport, auth, errors and formatting for iApp AI Marketplace clients.

This package is the single source of truth for talking to the iApp AI
Marketplace API (https://iapp.co.th). It backs both the synchronous ``iapp_ai``
SDK and the asynchronous ``iapp_mcp`` MCP server.
"""

__version__ = "0.1.0"

from .config import API_BASE, CONNECT_TIMEOUT, READ_TIMEOUT
from .errors import IAppAPIError, status_error_message
from .formatting import (
    build_output_path,
    default_output_dir,
    format_json_response,
    get_api_key,
    open_input_files,
    resolve_input_file,
    resolve_output_path,
    save_binary,
    save_pcm_as_wav,
    truncate_blobs,
)
from .transport import request_async, request_sync
from .urls import build_url

__all__ = [
    "API_BASE",
    "CONNECT_TIMEOUT",
    "READ_TIMEOUT",
    "IAppAPIError",
    "status_error_message",
    "build_url",
    "build_output_path",
    "default_output_dir",
    "format_json_response",
    "get_api_key",
    "open_input_files",
    "resolve_input_file",
    "resolve_output_path",
    "save_binary",
    "save_pcm_as_wav",
    "truncate_blobs",
    "request_async",
    "request_sync",
]
