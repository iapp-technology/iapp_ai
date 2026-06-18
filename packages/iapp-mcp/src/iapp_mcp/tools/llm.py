"""LLM tools: Chinda Thai LLM, DeepSeek, Thanoy Legal AI."""

import json
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from ..app import mcp
from ..client import IAppAPIError, format_json_response, request

# Maps model id -> OpenAI-compatible chat completions endpoint.
_MODEL_ENDPOINTS = {
    "chinda-qwen3-4b": "/v3/llm/chinda-thaillm-4b/chat/completions",
    "deepseek-reasoner": "/v3/llm/deepseek-3p2/chat/completions",
    "deepseek-chat": "/v3/llm/deepseek-3p2/chat/completions",
    "deepseek-v4-flash": "/v3/llm/deepseek-v4/chat/completions",
    "deepseek-v4-pro": "/v3/llm/deepseek-v4/chat/completions",
}


class ChatMessage(BaseModel):
    """A single chat message."""

    role: Literal["system", "user", "assistant"] = Field(description="Message role")
    content: str = Field(description="Message text")


@mcp.tool(
    name="iapp_llm_chat",
    annotations={
        "title": "iApp LLM Chat (Chinda Thai LLM / DeepSeek)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def iapp_llm_chat(
    prompt: str,
    model: Literal[
        "chinda-qwen3-4b",
        "deepseek-reasoner",
        "deepseek-chat",
        "deepseek-v4-flash",
        "deepseek-v4-pro",
    ] = "chinda-qwen3-4b",
    system_prompt: Optional[str] = None,
    messages: Optional[List[ChatMessage]] = None,
    max_tokens: int = 4096,
    temperature: float = 0.7,
) -> str:
    """Chat with LLMs hosted on the iApp AI Marketplace (OpenAI-compatible).

    Available models:
        - chinda-qwen3-4b: Chinda Thai LLM 4B, Thai/English, 40K context (free tier)
        - deepseek-reasoner: DeepSeek-V3.2 thinking model, 128K context
        - deepseek-chat: DeepSeek-V3.2 non-thinking, faster
        - deepseek-v4-flash: DeepSeek V4 Flash — chat, RAG, classification
        - deepseek-v4-pro: DeepSeek V4 Pro — deep reasoning, agents, math, coding

    Args:
        prompt: User message. Ignored if `messages` is provided.
        model: Model to use.
        system_prompt: Optional system prompt (prepended when using `prompt`).
        messages: Optional full conversation history; overrides prompt/system_prompt.
        max_tokens: Maximum output tokens (default 4096).
        temperature: Sampling temperature 0-2 (default 0.7).

    Returns:
        The assistant's reply text, followed by reasoning content (if any) and token usage.
        Pricing: chinda free; deepseek from 0.01 IC/1K input tokens.
    """
    try:
        if messages:
            message_dicts = [m.model_dump() for m in messages]
        else:
            message_dicts = []
            if system_prompt:
                message_dicts.append({"role": "system", "content": system_prompt})
            message_dicts.append({"role": "user", "content": prompt})

        response = await request(
            "POST",
            _MODEL_ENDPOINTS[model],
            json_body={
                "model": model,
                "messages": message_dicts,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False,
            },
        )
        payload = response.json()
        choice = (payload.get("choices") or [{}])[0]
        message = choice.get("message", {})
        parts = [message.get("content", "")]
        if message.get("reasoning_content"):
            parts.append(f"\n---\n[reasoning]\n{message['reasoning_content']}")
        usage = payload.get("usage")
        if usage:
            parts.append(f"\n---\n[usage] {json.dumps(usage)}")
        return "\n".join(parts)
    except IAppAPIError as e:
        return str(e)
    except (ValueError, KeyError) as e:
        return f"Error: Unexpected LLM response format: {e}"


@mcp.tool(
    name="iapp_thanoy_legal_qa",
    annotations={
        "title": "Thanoy Thai Legal AI",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def iapp_thanoy_legal_qa(query: str) -> str:
    """Ask a Thai legal question to Thanoy (ทนายAI), a Thai legal AI chatbot.

    Backed by a knowledge base of 10,000+ Thai legal articles. Answers questions about
    Thai law, offenses, penalties and legal procedures. Not OpenAI-compatible.

    Args:
        query: Legal question in Thai (e.g. 'โดนโจรตีหัว ผิดมาตราอะไร').

    Returns:
        JSON string with the legal answer and token usage. Response time up to 15s.
        Cost: 0.01 IC/1K input + 0.02 IC/1K output tokens.
    """
    try:
        response = await request(
            "POST", "/v3/store/llm/thanoy-legal-ai", json_body={"query": query}
        )
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)
