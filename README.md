# iApp AI

Official Python clients for the [iApp AI Marketplace](https://iapp.co.th) —
30+ Thai-focused AI APIs (OCR, eKYC, Thai NLP, LLMs, speech, image/video
generation, smart city), plus a free offline Thai NLP library. This repository
is a monorepo of four packages: the SDK and the MCP server share a single core,
and `iapp-nlp` stands on its own.

## Packages

| Package | PyPI | What it is |
|---|---|---|
| [`packages/iapp-sdk`](packages/iapp-sdk) | [`iapp-ai`](https://pypi.org/project/iapp-ai/) | Synchronous Python **SDK** — `from iapp_ai import api`. Thin wrappers returning raw `requests.Response`. |
| [`packages/iapp-mcp`](packages/iapp-mcp) | [`iapp-mcp`](https://pypi.org/project/iapp-mcp/) | **MCP server** for AI assistants (Claude, etc.) exposing the marketplace as tools. Also on [npm](https://www.npmjs.com/package/iapp-mcp). |
| [`packages/iapp-core`](packages/iapp-core) | [`iapp-core`](https://pypi.org/project/iapp-core/) | Shared **core**: base URL, API-key auth, error handling, response formatting, and the sync + async HTTP transport. A dependency of the SDK and the MCP server. |
| [`packages/iapp-nlp`](packages/iapp-nlp) | `iapp-nlp` | Free Thai **NLP** library that runs offline and requires no API key. Its tools include word tokenization with the OpenThai2.0-LATTE-WordSeg-Lite model, text normalization, and more. |

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
- **Using free Thai NLP tools without an API key?** → the NLP library: `pip install iapp-nlp`
  ```python
  from iapp_nlp import normalize, word_tokenize
  text = "วันนี้ฝนตกหนักมาาาก"         # repeated vowel typo
  word_tokenize(text)
  # ['วัน', 'นี้', 'ฝน', 'ตก', 'หนัก', 'มาาาก']
  word_tokenize(normalize(text))
  # ['วัน', 'นี้', 'ฝน', 'ตก', 'หนัก', 'มาก']
  ```

The SDK and the MCP server need an API key: get one at [iapp.co.th](https://iapp.co.th) → **API Keys** → **Create New API Key**.

## Development

This is a [uv](https://docs.astral.sh/uv/) workspace. From the repo root:

```bash
uv sync --all-packages  # create a venv with all four packages installed editable
uv run pytest packages/iapp-sdk/tests -q
uv build --all-packages # build wheels/sdists for every package
```

The SDK and MCP server both depend on `iapp-core` via `[tool.uv.sources]`
(workspace) for local dev, and on a published `iapp-core` version when released.
Release order: **iapp-core → iapp-ai / iapp-mcp**. `iapp-nlp` has no internal
dependency and can be released on its own.

To release one package, push a tag named `<PyPI name>-v<version>`, such as
`iapp-nlp-v0.1.0`, whose version matches the package's `pyproject.toml`. The
[release workflow](.github/workflows/release.yml) builds and checks only that
package, then publishes it to PyPI once a reviewer approves the `pypi`
environment.

## Support

- Documentation: [iapp.co.th/docs/intro](https://iapp.co.th/docs/intro)
- Email: support@iapp.co.th

## License

MIT © iApp Technology Co., Ltd. `iapp-nlp` also includes Apache-2.0 code, and model files under CC BY-SA 4.0 (commercial use allowed); see [its README](packages/iapp-nlp/README.md#license).
