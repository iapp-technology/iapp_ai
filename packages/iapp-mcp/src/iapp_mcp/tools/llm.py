"""LLM tools: DeepSeek, Thanoy Legal AI."""

import json
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from ..app import mcp
from ..client import IAppAPIError, format_json_response, request

# Maps model id -> OpenAI-compatible chat completions endpoint.
_MODEL_ENDPOINTS = {
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
        "title": "iApp LLM Chat (DeepSeek)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def iapp_llm_chat(
    prompt: str,
    model: Literal[
        "deepseek-reasoner",
        "deepseek-chat",
        "deepseek-v4-flash",
        "deepseek-v4-pro",
    ] = "deepseek-chat",
    system_prompt: Optional[str] = None,
    messages: Optional[List[ChatMessage]] = None,
    max_tokens: int = 4096,
    temperature: float = 0.7,
) -> str:
    """Chat with LLMs hosted on the iApp AI Marketplace (OpenAI-compatible).

    Available models:
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
        Pricing: deepseek from 0.01 IC/1K input tokens.
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


@mcp.tool(
    name="iapp_openthai_legal_chat",
    annotations={
        "title": "OpenThai 2.0 Legal ThaiLLM (RAG-grounded Thai law)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def iapp_openthai_legal_chat(
    prompt: str,
    system_prompt: Optional[str] = None,
    messages: Optional[List[ChatMessage]] = None,
    rag: bool = True,
    rag_top_k: int = 8,
    rag_inject: Literal["user", "system"] = "user",
    max_tokens: int = 1024,
    temperature: float = 0.7,
) -> str:
    """Ask Thai legal questions with OpenThai 2.0 Legal — answers grounded in real statute text.

    Open-weight Thai legal LLM (Nemotron-3-Nano-30B-A3B) that is RAG-connected server-side:
    every request hybrid-searches a 39-law, 6,300-section Thai statute corpus and grounds the
    answer in the current law text, returning the sections it used so you can cite or audit
    them. OpenAI-compatible.

    Prefer this over iapp_thanoy_legal_qa when you need verifiable มาตรา citations.

    Args:
        prompt: Legal question in Thai. Ignored if `messages` is provided.
        system_prompt: Optional system prompt (prepended when using `prompt`).
        messages: Optional full conversation history; overrides prompt/system_prompt.
        rag: Retrieve statute sections and ground the answer. False = closed-book model.
        rag_top_k: Sections injected into the prompt (max 20; 6 when rag_inject='system').
        rag_inject: 'user' = trained citation scaffold, best for JSON citation answers.
            'system' = advisory reference, best for essay/long-form analysis.
        max_tokens: Maximum output tokens (default 1024).
        temperature: Sampling temperature 0-2 (default 0.7).

    Returns:
        The answer, the retrieved statute sections (law/section/score) when RAG is on, and
        token usage. FREE with an API key until 24 Aug 2026 (then 0.01 IC/1K input +
        0.02 IC/1K output).
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
            "/v3/llm/openthai2p0-legal/chat/completions",
            json_body={
                "model": "openthai2.0-legal",
                "messages": message_dicts,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False,
                "rag": rag,
                "rag_top_k": min(rag_top_k, 20),
                "rag_inject": rag_inject,
            },
        )
        payload = response.json()
        choice = (payload.get("choices") or [{}])[0]
        message = choice.get("message", {})
        parts = [message.get("content", "")]

        if message.get("reasoning"):
            parts.append(f"\n---\n[reasoning]\n{message['reasoning']}")

        retrieved = payload.get("retrieved_documents") or []
        if retrieved:
            lines = [f"\n---\n[retrieved sections] rag={payload.get('rag')}"]
            for doc in retrieved:
                score = doc.get("score")
                score_txt = f" (score {score:.4f})" if isinstance(score, (int, float)) else ""
                lines.append(
                    f"- {doc.get('law', '?')} มาตรา {doc.get('section', '?')}{score_txt}\n"
                    f"    {(doc.get('text') or '').strip()[:300]}"
                )
            parts.append("\n".join(lines))
        elif rag:
            parts.append("\n---\n[retrieved sections] none returned")

        usage = payload.get("usage")
        if usage:
            parts.append(f"\n---\n[usage] {json.dumps(usage)}")
        return "\n".join(parts)
    except IAppAPIError as e:
        return str(e)
    except (ValueError, KeyError) as e:
        return f"Error: Unexpected OpenThai Legal response format: {e}"
