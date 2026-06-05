# iapp-core

Shared internal core for the [iApp AI Marketplace](https://iapp.co.th) Python
clients. It is the single source of truth for talking to `api.iapp.co.th`:
base URL, API-key auth, error handling, response formatting, and both a
synchronous and an asynchronous HTTP transport.

You normally do **not** install this directly. It is a dependency of:

- [`iapp-ai`](../iapp-sdk) — the synchronous Python SDK (`from iapp_ai import api`)
- [`iapp-mcp`](../iapp-mcp) — the iApp AI Marketplace MCP server

## What it provides

```python
from iapp_core import (
    API_BASE, IAppAPIError, status_error_message,
    request_sync,            # requests-based, returns requests.Response
    request_async,           # httpx-based (needs the `async` extra), returns httpx.Response
    format_json_response, truncate_blobs,
    save_binary, save_pcm_as_wav,
    resolve_input_file, resolve_output_path, get_api_key,
)
```

The async transport requires `httpx`; install it with the extra:

```bash
pip install "iapp-core[async]"
```

The sync transport only needs `requests`, which is a base dependency.

## License

MIT © iApp Technology Co., Ltd.
