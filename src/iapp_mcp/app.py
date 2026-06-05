"""FastMCP application instance shared by all tool modules."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "iapp_ai",
    instructions=(
        "MCP server for the iApp AI Marketplace (https://iapp.co.th) — Thai-focused AI APIs: "
        "OCR (documents, receipts, ID cards), eKYC (face verification/liveness), Thai NLP "
        "(translation, summarization, sentiment, QA), LLM chat (Chinda Thai LLM, DeepSeek), "
        "speech-to-text, text-to-speech, image/video generation, and smart-city utilities. "
        "Requires the IAPP_API_KEY environment variable. Get an API key at https://iapp.co.th. "
        "Most tools accept local file paths for images/documents/audio and consume iApp credits (IC) per call."
    ),
)
