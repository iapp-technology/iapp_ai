"""Response formatting and local-file helpers for iApp AI Marketplace clients.

These helpers are response-type-agnostic: they only use ``.json()``/``.text``/
``.content``, so they work with both ``requests.Response`` (sync SDK) and
``httpx.Response`` (async MCP server).
"""

import json
import os
import re
import wave
from typing import Any, Optional

from .errors import IAppAPIError

# Strings longer than this that look like base64 blobs (e.g. cropped face
# images embedded in OCR responses) are truncated to keep tool output small.
_BASE64_TRUNCATE_THRESHOLD = 2048
_BASE64_RE = re.compile(r"^[A-Za-z0-9+/=\s]+$")


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


def default_output_dir() -> str:
    """Base directory for generated output files.

    Honors the ``IAPP_OUTPUT_DIR`` environment variable; falls back to ``media``
    to preserve the legacy on-disk layout when nothing is configured.
    """
    return os.environ.get("IAPP_OUTPUT_DIR", "").strip() or "media"


def build_output_path(filename: str, output_path: Optional[str] = None) -> str:
    """Resolve where to save a generated file, creating the directory.

    Central output-path API for domain methods that currently hardcode
    ``media/...`` (defect D-09):

    * ``output_path`` given  -> use it verbatim (caller is in full control),
    * ``output_path`` omitted -> ``default_output_dir()/filename``.

    The default stays ``media/`` so behavior is unchanged out of the box, but
    callers (and ops, via ``IAPP_OUTPUT_DIR``) can now redirect output instead
    of being locked to a hardcoded folder.
    """
    target = output_path if output_path else os.path.join(default_output_dir(), filename)
    return resolve_output_path(target)


def truncate_blobs(value: Any) -> Any:
    """Recursively truncate base64-looking blobs (embedded images) in API responses."""
    if isinstance(value, dict):
        return {k: truncate_blobs(v) for k, v in value.items()}
    if isinstance(value, list):
        return [truncate_blobs(v) for v in value]
    if (
        isinstance(value, str)
        and len(value) > _BASE64_TRUNCATE_THRESHOLD
        and _BASE64_RE.match(value)
    ):
        return f"<base64 data omitted: {len(value)} chars>"
    return value


# Backwards-compatible private alias (the original lived in iapp_mcp.client).
_truncate_blobs = truncate_blobs


def format_json_response(response: Any) -> str:
    """Format an API JSON response as a pretty-printed string with blobs truncated."""
    try:
        payload = response.json()
    except (json.JSONDecodeError, ValueError):
        return response.text
    return json.dumps(truncate_blobs(payload), ensure_ascii=False, indent=2)


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
