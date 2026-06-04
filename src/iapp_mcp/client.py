"""Shared HTTP client utilities for calling iApp AI Marketplace APIs."""

import json
import os
import re
import wave
from typing import Any, Dict, List, Optional, Tuple

import httpx

API_BASE = "https://api.iapp.co.th"
TIMEOUT = httpx.Timeout(300.0, connect=15.0)

# Strings longer than this that look like base64 blobs (e.g. cropped face
# images embedded in OCR responses) are truncated to keep tool output small.
_BASE64_TRUNCATE_THRESHOLD = 2048
_BASE64_RE = re.compile(r"^[A-Za-z0-9+/=\s]+$")


class IAppAPIError(Exception):
    """Raised for actionable iApp API errors."""


def get_api_key() -> str:
    """Read the API key from the IAPP_API_KEY environment variable."""
    api_key = os.environ.get("IAPP_API_KEY", "").strip()
    if not api_key:
        raise IAppAPIError(
            "IAPP_API_KEY environment variable is not set. "
            "Get an API key from https://iapp.co.th and set it in the MCP server config."
        )
    return api_key


def resolve_input_file(file_path: str) -> str:
    """Expand and validate a local input file path."""
    path = os.path.expanduser(file_path)
    if not os.path.isfile(path):
        raise IAppAPIError(
            f"Input file not found: {file_path}. Provide an absolute path to an existing file."
        )
    return path


def resolve_output_path(output_path: str) -> str:
    """Expand an output path and make sure its directory exists."""
    path = os.path.abspath(os.path.expanduser(output_path))
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    return path


def _status_error_message(response: httpx.Response) -> str:
    status = response.status_code
    snippet = response.text[:500]
    if status == 401:
        return (
            "Error: Authentication failed (401). Check that IAPP_API_KEY is a valid "
            "iApp API key from https://iapp.co.th."
        )
    if status == 402:
        return (
            "Error: Insufficient credits (402). Top up iApp credits (IC) at https://iapp.co.th. "
            f"Details: {snippet}"
        )
    if status == 413:
        return "Error: File too large (413). Check the size limit for this service and resize/compress the file."
    if status == 429:
        return "Error: Rate limit exceeded (429). Wait a moment before retrying."
    return f"Error: iApp API request failed with status {status}. Details: {snippet}"


async def request(
    method: str,
    path: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    json_body: Optional[Any] = None,
    file_fields: Optional[List[Tuple[str, str]]] = None,
) -> httpx.Response:
    """Make an authenticated request to the iApp API.

    file_fields is a list of (form_field_name, local_file_path) tuples sent as multipart.
    """
    headers = {"apikey": get_api_key()}
    open_files = []
    files = None
    try:
        if file_fields:
            files = []
            for field_name, file_path in file_fields:
                path_resolved = resolve_input_file(file_path)
                fh = open(path_resolved, "rb")
                open_files.append(fh)
                files.append((field_name, (os.path.basename(path_resolved), fh)))
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.request(
                method,
                f"{API_BASE}{path}",
                headers=headers,
                params=params,
                data=data,
                json=json_body,
                files=files,
            )
        if response.status_code >= 400:
            raise IAppAPIError(_status_error_message(response))
        return response
    except httpx.TimeoutException:
        raise IAppAPIError(
            "Error: Request to the iApp API timed out. The service may be processing a large "
            "file — try again or use a smaller input."
        )
    except httpx.HTTPError as e:
        raise IAppAPIError(f"Error: Network error calling the iApp API: {type(e).__name__}: {e}")
    finally:
        for fh in open_files:
            fh.close()


def _truncate_blobs(value: Any) -> Any:
    """Recursively truncate base64-looking blobs (embedded images) in API responses."""
    if isinstance(value, dict):
        return {k: _truncate_blobs(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_truncate_blobs(v) for v in value]
    if (
        isinstance(value, str)
        and len(value) > _BASE64_TRUNCATE_THRESHOLD
        and _BASE64_RE.match(value)
    ):
        return f"<base64 data omitted: {len(value)} chars>"
    return value


def format_json_response(response: httpx.Response) -> str:
    """Format an API JSON response as a pretty-printed string with blobs truncated."""
    try:
        payload = response.json()
    except (json.JSONDecodeError, ValueError):
        return response.text
    return json.dumps(_truncate_blobs(payload), ensure_ascii=False, indent=2)


def save_binary(content: bytes, output_path: str) -> str:
    """Save binary content to output_path and return the resolved path."""
    path = resolve_output_path(output_path)
    with open(path, "wb") as f:
        f.write(content)
    return path


def save_pcm_as_wav(pcm_data: bytes, output_path: str, sample_rate: int = 24000) -> str:
    """Wrap raw signed 16-bit mono PCM in a WAV container and save it."""
    path = resolve_output_path(output_path)
    with wave.open(path, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)
    return path
