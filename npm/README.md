# iApp AI MCP Server

[MCP (Model Context Protocol)](https://modelcontextprotocol.io) server for the
[iApp AI Marketplace](https://iapp.co.th) — connect AI assistants to 30+
Thai-focused AI APIs: OCR, eKYC, Thai NLP, LLMs, speech, and image/video generation.

This npm package is a thin launcher for the Python server
([`iapp-ai` on PyPI](https://pypi.org/project/iapp-ai/)). It requires
[uv](https://docs.astral.sh/uv/getting-started/installation/) to be installed.

## Usage

Add to your MCP client's configuration file:

```json
{
  "mcpServers": {
    "iapp-ai": {
      "command": "npx",
      "args": ["-y", "iapp-ai"],
      "env": {
        "IAPP_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

Get an API key at [iapp.co.th](https://iapp.co.th) → **API Keys** → **Create New API Key**.

Full documentation: https://github.com/iapp-ai/iapp-ai

## Support

- Documentation: [iapp.co.th/docs/intro](https://iapp.co.th/docs/intro)
- Email: support@iapp.co.th
