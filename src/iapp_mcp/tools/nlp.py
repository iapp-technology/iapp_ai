"""Thai NLP tools: translation, summarization, sentiment, toxicity, QA, question generation."""

from typing import Literal, Optional

from ..app import mcp
from ..client import IAppAPIError, format_json_response, request

_READONLY = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": True,
}

LANGUAGE_CODES = (
    "ar, bn, cs, de, en, es, fa, fr, he, hi, id, it, ja, km, ko, lo, ms, my, nl, pl, "
    "pt, ru, th, tl, tr, ur, vi, zh"
)


@mcp.tool(
    name="iapp_translate",
    annotations={"title": "Multilingual Translation", **_READONLY},
)
async def iapp_translate(
    text: str,
    source_lang: str,
    target_lang: str,
    max_length: Optional[int] = None,
) -> str:
    """Translate text between 28 languages (Thai-optimized).

    Supported language codes: ar, bn, cs, de, en, es, fa, fr, he, hi, id, it, ja, km,
    ko, lo, ms, my, nl, pl, pt, ru, th, tl, tr, ur, vi, zh.

    Args:
        text: Text to translate.
        source_lang: Source language code (e.g. 'en', 'th', 'zh').
        target_lang: Target language code (e.g. 'th', 'en', 'ja').
        max_length: Optional maximum output tokens.

    Returns:
        JSON string with the translation and processing time. Cost: 1 IC per 400 chars.
    """
    try:
        data = {"text": text, "source_lang": source_lang, "target_lang": target_lang}
        if max_length is not None:
            data["max_length"] = max_length
        response = await request("POST", "/v1/text/translate", data=data)
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)


@mcp.tool(
    name="iapp_summarize",
    annotations={"title": "Thai Text Summarization", **_READONLY},
)
async def iapp_summarize(
    text: str,
    style: Literal["standard", "clarify", "friendly"] = "standard",
    language: Literal["th", "en"] = "th",
    max_output_tokens: Optional[int] = None,
) -> str:
    """Summarize Thai or English text.

    Args:
        text: Text to summarize.
        style: 'standard' (formal with intro/conclusion), 'clarify' (notes unresolved
            points), or 'friendly' (simple language).
        language: Output language ('th' or 'en').
        max_output_tokens: Optional output token limit (default 8192).

    Returns:
        JSON string with the summary. Cost: 1 IC per 400 chars.
    """
    try:
        body = {"text": text, "style": style, "language": language}
        if max_output_tokens is not None:
            body["max_output_tokens"] = max_output_tokens
        response = await request("POST", "/v3/store/nlp/thai-text-summary/v2", json_body=body)
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)


@mcp.tool(
    name="iapp_sentiment_analysis",
    annotations={"title": "Thai Sentiment Analysis", **_READONLY},
)
async def iapp_sentiment_analysis(text: str) -> str:
    """Classify the sentiment of Thai text as positive, neutral, or negative.

    Args:
        text: Thai text to analyze.

    Returns:
        JSON string with label ('pos'/'neu'/'neg') and confidence score (0-1).
        Cost: 1 IC per 400 chars.
    """
    try:
        response = await request(
            "POST", "/v3/store/nlp/sentiment-analysis", params={"text": text}
        )
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)


@mcp.tool(
    name="iapp_toxicity_classification",
    annotations={"title": "Thai Toxicity Classification", **_READONLY},
)
async def iapp_toxicity_classification(text: str) -> str:
    """Classify whether Thai text is toxic or non-toxic.

    Args:
        text: Thai text to classify.

    Returns:
        JSON string with label ('toxic'/'non_toxic') and confidence score (0-1).
        Cost: 1 IC per 400 chars.
    """
    try:
        response = await request(
            "POST", "/v3/store/nlp/toxicity-classification", params={"text": text}
        )
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)


@mcp.tool(
    name="iapp_thai_qa",
    annotations={"title": "Thai Question Answering", **_READONLY},
)
async def iapp_thai_qa(question: str, document: str) -> str:
    """Answer a Thai question using a provided Thai document as context (extractive QA).

    Args:
        question: Question in Thai.
        document: Thai text passage to extract the answer from.

    Returns:
        JSON string with the answer. Cost: 1 IC per 400 chars.
    """
    try:
        # Note: the documented /v3/store/nlp/question/answer path returns 404;
        # the working route is /thai-qa (verified 2026-06).
        response = await request(
            "POST",
            "/thai-qa",
            json_body={"question": question, "document": document},
        )
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)


@mcp.tool(
    name="iapp_question_generation",
    annotations={"title": "Thai Question Generation", **_READONLY},
)
async def iapp_question_generation(text: str) -> str:
    """Generate question-answer pairs from Thai text (useful for quizzes and study material).

    Args:
        text: Thai text to generate questions from.

    Returns:
        JSON string with a list of {question, answer} pairs. Cost: 1 IC per 400 chars.
    """
    try:
        response = await request(
            "POST", "/v3/store/nlp/question/generation", json_body={"text": text}
        )
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)
