"""Entry point for the iApp AI Marketplace MCP server."""

from .app import mcp

# Importing tool modules registers their tools on the shared FastMCP instance.
from .tools import ekyc, generation, llm, nlp, ocr, smartcity, speech  # noqa: F401, E402


def main() -> None:
    """Run the MCP server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
