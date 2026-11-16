<p align="center">
  <img src="logo-iapp.png" alt="iApp Technology" width="240">
</p>

<p align="center">
  <a href="https://pypi.org/project/iapp-ai/"><img src="https://img.shields.io/pypi/v/iapp-ai?label=iapp-ai" alt="iapp-ai on PyPI"></a>
  <a href="https://pypi.org/project/iapp-mcp/"><img src="https://img.shields.io/pypi/v/iapp-mcp?label=iapp-mcp" alt="iapp-mcp on PyPI"></a>
  <a href="https://www.npmjs.com/package/iapp-mcp"><img src="https://img.shields.io/npm/v/iapp-mcp?label=npm%20iapp-mcp" alt="iapp-mcp on npm"></a>
  <a href="#license"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License: MIT"></a>
</p>

<p align="center">
  <a href="https://iapp.co.th">Website</a> |
  <a href="https://iapp.co.th/docs/intro">Documentation</a> |
  <a href="#api-key">Get an API key</a> |
  <a href="#support">Support</a>
</p>

Official Python clients for the [iApp AI Marketplace](https://iapp.co.th): 30+
Thai-focused AI APIs for OCR, eKYC, Thai NLP, LLMs, speech, image and video
generation, and smart city, plus a free Thai NLP library that runs offline.

## Packages

| Package | Install | Description |
|---|---|---|
| [iapp-ai](packages/iapp-sdk) | `pip install iapp-ai` | Python SDK for the iApp APIs |
| [iapp-mcp](packages/iapp-mcp) | `uvx iapp-mcp` | MCP server for AI assistants such as Claude |
| [iapp-nlp](packages/iapp-nlp) | `pip install iapp-nlp` | Offline Thai NLP, no API key needed |
| [iapp-core](packages/iapp-core) | installed as a dependency | Shared core of the SDK and the MCP server |

## What the APIs cover

| Category | Examples |
|---|---|
| eKYC | Thai ID card, passport, driver license and bank book OCR, face verification, face liveness |
| Document OCR | Thai documents to text, layout or DOCX, receipts, 50 ทวิ tax certificates, resumes |
| Thai NLP | Translation (28 languages), summarization, sentiment, toxicity, Thai QA |
| LLMs | Chinda Thai LLM, DeepSeek, Thanoy Thai legal AI |
| Speech | Thai speech-to-text with speaker labels, Thai text-to-speech, voice cloning |
| Image and video | Image generation, background removal, video generation |
| Smart city and data | License plates, water and power meters, route optimization, Thai holidays |

The full list of tools is in the [`iapp-mcp` README](packages/iapp-mcp/README.md#tools-reference).

## Quick start

### Python SDK

```bash
pip install iapp-ai
```

```python
from iapp_ai import api

client = api("YOUR_API_KEY")
resp = client.idcard_front("id.jpg")   # returns requests.Response
print(resp.json())
```

### MCP server

Add this to your MCP client's configuration:

```json
{
  "mcpServers": {
    "iapp-mcp": {
      "command": "uvx",
      "args": ["iapp-mcp"],
      "env": { "IAPP_API_KEY": "YOUR_API_KEY" }
    }
  }
}
```

Other ways to install and configure it are in the [`iapp-mcp` README](packages/iapp-mcp/README.md).

### Thai NLP, offline

```bash
pip install iapp-nlp
```

```python
from iapp_nlp import normalize, word_tokenize

text = "วันนี้ฝนตกหนักมาาาก"         # repeated vowel typo
word_tokenize(text)
# ['วัน', 'นี้', 'ฝน', 'ตก', 'หนัก', 'มาาาก']
word_tokenize(normalize(text))
# ['วัน', 'นี้', 'ฝน', 'ตก', 'หนัก', 'มาก']
```

## API key

The SDK and the MCP server need an API key; `iapp-nlp` does not.

1. Sign in or register at [iapp.co.th](https://iapp.co.th).
2. Open **API Keys** in the control panel.
3. Click **Create New API Key**, name it and copy the key. It is shown only once.

Most API calls use iApp credits (IC).

## Backward compatibility

Existing SDK users are unaffected: `pip install iapp_ai` and
`from iapp_ai import api` keep working exactly as before. The MCP server is
published separately as `iapp-mcp`.

## Development

This is a [uv](https://docs.astral.sh/uv/) workspace. From the repository root:

```bash
uv sync --all-packages   # one virtual environment with all four packages, editable
uv run pytest packages scripts -q
uv build --all-packages  # wheels and sdists for every package
```

The SDK and the MCP server depend on `iapp-core` through `[tool.uv.sources]`
during development and on a published `iapp-core` version when released.
Release order: `iapp-core`, then `iapp-ai` and `iapp-mcp`. `iapp-nlp` has no
internal dependency and is released on its own.

To release one package, push a tag named `<PyPI name>-v<version>`, such as
`iapp-nlp-v0.1.0`, whose version matches the package's `pyproject.toml`. The
[release workflow](.github/workflows/release.yml) builds and checks only that
package, then publishes it to PyPI once a reviewer approves the `pypi`
environment.

## Support

- Documentation: [iapp.co.th/docs/intro](https://iapp.co.th/docs/intro)
- Email: support@iapp.co.th

## License

MIT © iApp Technology Co., Ltd. `iapp-nlp` also includes Apache-2.0 code and
model files under CC BY-SA 4.0 (commercial use allowed); see
[its license section](packages/iapp-nlp/README.md#license).
