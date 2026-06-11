"""URL-building helpers for iApp AI Marketplace clients.

Several SDK methods build request URLs by concatenating Thai text straight into
a query string (``...?text=สวัสดี``). Un-encoded non-ASCII produces invalid URLs
that fail or get mangled in transit. :func:`build_url` percent-encodes every
query value so domain methods can stop hand-building URLs (fixes D-05).
"""

from typing import Any, Dict, Optional
from urllib.parse import urlencode


def build_url(base: str, path: str = "", params: Optional[Dict[str, Any]] = None) -> str:
    """Join ``base`` and ``path`` and append a URL-encoded query string.

    ``params`` values are percent-encoded (so Thai text and other non-ASCII are
    safe). ``None`` values are dropped. Exactly one ``/`` is placed between
    ``base`` and ``path``. This helper never injects auth — callers decide
    whether an apikey belongs in the query or a header.

    >>> build_url("https://api.iapp.co.th", "translate/auto", {"text": "สวัสดี"})
    'https://api.iapp.co.th/translate/auto?text=%E0%B8%AA%E0%B8%A7%E0%B8%B1%E0%B8%94%E0%B8%94%E0%B8%B5'
    """
    url = base.rstrip("/")
    if path:
        url = f"{url}/{path.lstrip('/')}"
    if params:
        clean = {k: v for k, v in params.items() if v is not None}
        if clean:
            url = f"{url}?{urlencode(clean, doseq=True)}"
    return url
