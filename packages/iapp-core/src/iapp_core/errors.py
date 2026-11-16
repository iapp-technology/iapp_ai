"""Errors and HTTP status mapping for iApp AI Marketplace clients."""


class IAppAPIError(Exception):
    """Raised for actionable iApp API errors."""


def status_error_message(status: int, text: str) -> str:
    """Map an HTTP error status (and response body) to an actionable message."""
    snippet = text[:500]
    if status == 400:
        return (
            "Error: Bad request (400). The request was malformed or a required parameter "
            f"is missing/invalid. Details: {snippet}"
        )
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
    if status == 403:
        return (
            "Error: Access forbidden (403). Your API key is valid but not allowed to use "
            f"this endpoint — check your plan or permissions at https://iapp.co.th. Details: {snippet}"
        )
    if status == 404:
        return (
            "Error: Not found (404). The endpoint or resource does not exist — check the "
            f"URL/path for this service. Details: {snippet}"
        )
    if status == 413:
        return "Error: File too large (413). Check the size limit for this service and resize/compress the file."
    if status == 429:
        return "Error: Rate limit exceeded (429). Wait a moment before retrying."
    if status == 500:
        return (
            "Error: iApp server error (500). The service failed to process the request — "
            f"retry shortly; if it persists, contact iApp support. Details: {snippet}"
        )
    return f"Error: iApp API request failed with status {status}. Details: {snippet}"
