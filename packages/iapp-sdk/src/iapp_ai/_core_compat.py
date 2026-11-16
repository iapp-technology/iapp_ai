"""Copies of three iapp-core helpers that iapp-core 0.1.1, the newest release on PyPI, lacks.

The iapp-core in this repo has ``build_output_path``, ``build_url`` and ``open_input_files``,
but it lacks the timeout settings that only the published 0.1.1 has, so it cannot be released
as it is. Until one iapp-core release has both, iapp_ai uses these copies, which need only what
every iapp-core release on PyPI has. Once iapp-ai requires an iapp-core with these helpers,
import them from iapp_core again and delete this module.
"""

import os
from contextlib import contextmanager
from typing import Any, Dict, Iterator, List, Optional
from urllib.parse import urlencode

from iapp_core import resolve_input_file, resolve_output_path


def build_url(base: str, path: str = "", params: Optional[Dict[str, Any]] = None) -> str:
    """Join ``base`` and ``path`` and append a URL-encoded query string, as ``iapp_core.build_url``.

    ``params`` values are percent-encoded, so Thai text is safe, and ``None`` values are dropped.
    """
    url = base.rstrip("/")
    if path:
        url = f"{url}/{path.lstrip('/')}"
    if params:
        clean = {k: v for k, v in params.items() if v is not None}
        if clean:
            url = f"{url}?{urlencode(clean, doseq=True)}"
    return url


@contextmanager
def open_input_files(file_paths: List[str], mode: str = "rb") -> Iterator[List]:
    """Open several input files and close every handle on exit, as ``iapp_core.open_input_files``."""
    handles: List = []
    try:
        for file_path in file_paths:
            handles.append(open(resolve_input_file(file_path), mode))
        yield handles
    finally:
        for handle in handles:
            handle.close()


def default_output_dir() -> str:
    """``IAPP_OUTPUT_DIR``, or ``media`` when it is not set, as ``iapp_core.default_output_dir``."""
    return os.environ.get("IAPP_OUTPUT_DIR", "").strip() or "media"


def build_output_path(filename: str, output_path: Optional[str] = None) -> str:
    """Where to save a generated file, with its directory created, as ``iapp_core.build_output_path``:
    ``output_path`` when given, else ``default_output_dir()/filename``."""
    target = output_path if output_path else os.path.join(default_output_dir(), filename)
    return resolve_output_path(target)
