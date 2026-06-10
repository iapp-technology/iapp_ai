"""HTTP transport for iApp AI Marketplace clients.

Two helpers share auth-header injection, the base URL and the error mapping but
keep separate bodies because their file-handling contracts differ:

* ``request_sync``  — uses ``requests``; returns the raw ``requests.Response``;
  by default does NOT raise on HTTP errors (the legacy SDK returns the response
  as-is on 4xx/5xx). Used by the ``iapp_ai`` SDK.
* ``request_async`` — uses ``httpx`` (imported lazily so the sync install does
  not require it); raises ``IAppAPIError`` on >=400. Used by the MCP server.
"""

import os
import time
from typing import Any, Dict, List, Optional, Tuple

from .config import API_BASE, CONNECT_TIMEOUT, READ_TIMEOUT
from .errors import IAppAPIError, status_error_message
from .formatting import resolve_input_file


def _is_retryable_status(status: int) -> bool:
    """Transient statuses worth retrying: rate limiting and server errors."""
    return status == 429 or 500 <= status < 600


def request_sync(
    method: str,
    url: str,
    *,
    apikey: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Any] = None,
    json_body: Optional[Any] = None,
    files: Optional[Any] = None,
    raise_for_error: bool = False,
    timeout: Optional[float] = None,
    retries: int = 0,
    backoff_factor: float = 0.5,
):
    """Make an authenticated sync request and return the raw ``requests.Response``.

    ``url`` is a full absolute URL, passed through to ``requests`` verbatim.
    ``files`` is a pre-built ``requests`` files list, also passed through
    verbatim (callers pick their own field names and content types). The
    ``apikey`` header is injected first; any ``headers`` provided by the caller
    are merged on top (so a caller can add e.g. ``Content-Type``).

    Retry/backoff is opt-in and off by default (``retries=0``), so existing
    callers are unaffected. When ``retries`` > 0, transient responses (429 and
    5xx) are retried up to ``retries`` extra times with exponential backoff
    (``backoff_factor * 2**attempt`` seconds). Retries re-send the request as-is,
    so use it for calls without an already-consumed file body.
    """
    import requests

    request_headers = {"apikey": apikey}
    if headers:
        request_headers.update(headers)
    attempt = 0
    while True:
        response = requests.request(
            method,
            url,
            headers=request_headers,
            params=params,
            data=data,
            json=json_body,
            files=files,
            timeout=timeout,
        )
        if attempt < retries and _is_retryable_status(response.status_code):
            time.sleep(backoff_factor * (2 ** attempt))
            attempt += 1
            continue
        break
    if raise_for_error and response.status_code >= 400:
        raise IAppAPIError(status_error_message(response.status_code, response.text))
    return response


async def request_async(
    method: str,
    path: str,
    *,
    apikey: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    json_body: Optional[Any] = None,
    file_fields: Optional[List[Tuple[str, str]]] = None,
    raise_for_error: bool = True,
):
    """Make an authenticated async request to the iApp API.

    ``path`` is appended to :data:`iapp_core.config.API_BASE`. ``file_fields``
    is a list of ``(form_field_name, local_file_path)`` tuples sent as multipart;
    the files are opened and closed internally. ``apikey`` defaults to the
    ``IAPP_API_KEY`` environment variable.
    """
    import httpx

    from .formatting import get_api_key

    key = apikey if apikey is not None else get_api_key()
    headers = {"apikey": key}
    timeout = httpx.Timeout(READ_TIMEOUT, connect=CONNECT_TIMEOUT)
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
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(
                method,
                f"{API_BASE}{path}",
                headers=headers,
                params=params,
                data=data,
                json=json_body,
                files=files,
            )
        if raise_for_error and response.status_code >= 400:
            raise IAppAPIError(status_error_message(response.status_code, response.text))
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
