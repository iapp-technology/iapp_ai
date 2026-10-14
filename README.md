# iApp AI

Official Python clients for the [iApp AI Marketplace](https://iapp.co.th) —
30+ Thai-focused AI APIs (OCR, eKYC, Thai NLP, LLMs, speech, image/video
generation, smart city). This repository is a monorepo of three packages that
share a single core.

## Packages

| Package | PyPI | What it is |
|---|---|---|
| [`packages/iapp-sdk`](packages/iapp-sdk) | [`iapp-ai`](https://pypi.org/project/iapp-ai/) | Synchronous Python **SDK** — `from iapp_ai import api`. Thin wrappers returning raw `requests.Response`. |
| [`packages/iapp-mcp`](packages/iapp-mcp) | [`iapp-mcp`](https://pypi.org/project/iapp-mcp/) | **MCP server** for AI assistants (Claude, etc.) exposing the marketplace as tools. Also on [npm](https://www.npmjs.com/package/iapp-mcp). |
| [`packages/iapp-core`](packages/iapp-core) | [`iapp-core`](https://pypi.org/project/iapp-core/) | Shared **core**: base URL, API-key auth, error handling, response formatting, and the sync + async HTTP transport. A dependency of the other two. |

> **Backward compatibility:** existing SDK users are unaffected — `pip install iapp_ai`
> and `from iapp_ai import api` keep working exactly as before. The MCP server is
> published separately as `iapp-mcp`.

## Which one do I want?

- **Calling iApp APIs from Python code?** → the SDK: `pip install iapp-ai`
  ```python
  from iapp_ai import api
  client = api("YOUR_API_KEY")
  resp = client.idcard_front("id.jpg")   # returns requests.Response
  print(resp.json())
  ```
- **Connecting an AI assistant (Claude, etc.) to iApp?** → the MCP server:
  `uvx iapp-mcp` (see [its README](packages/iapp-mcp/README.md) for client config).

Get an API key at [iapp.co.th](https://iapp.co.th) → **API Keys** → **Create New API Key**.

## Development

This is a [uv](https://docs.astral.sh/uv/) workspace. From the repo root:

```bash
uv sync                 # create a venv with all three packages installed editable
uv run pytest packages/iapp-sdk/tests -q
uv build --all-packages # build wheels/sdists for every package
```

The SDK and MCP server both depend on `iapp-core` via `[tool.uv.sources]`
(workspace) for local dev, and on a published `iapp-core` version when released.
Release order: **iapp-core → iapp-ai / iapp-mcp**.

## Support

- Documentation: [iapp.co.th/docs/intro](https://iapp.co.th/docs/intro)
- Email: support@iapp.co.th

## License

MIT © iApp Technology Co., Ltd.
