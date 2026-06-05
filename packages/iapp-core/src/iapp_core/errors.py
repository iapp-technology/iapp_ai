"""Errors and HTTP status mapping for iApp AI Marketplace clients."""


class IAppAPIError(Exception):
    """Raised for actionable iApp API errors."""


def status_error_message(status: int, text: str) -> str:
    """Map an HTTP error status (and response body) to an actionable message."""
    snippet = text[:500]
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
