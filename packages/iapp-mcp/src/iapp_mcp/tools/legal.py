"""Thai legal tools: statute lookup/search, ฎีกา (Supreme Court decisions), grounded Q&A."""

from typing import Literal, Optional

from ..app import mcp
from ..client import IAppAPIError, format_json_response, request

_READONLY = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": True,
}

_BASE = "/v3/store/data/thai-legal"

# Appended to responses that carry ฎีกา so answers cite verifiably.
_CITE_NOTE = (
    "\n\nCITATION FORMAT: when you present rulings from this result to the user, cite each as "
    "'ฎีกาที่ <case_id> — ตรวจสอบต้นฉบับ: <official_url>' (include the official_url link every time), "
    "and end with a note that the data is for research, not legal advice."
)


@mcp.tool(
    name="iapp_thai_law_list",
    annotations={"title": "Thai Law Catalogue", **_READONLY},
)
async def iapp_thai_law_list(q: Optional[str] = None) -> str:
    """List every Thai statute available in the iApp legal corpus.

    Call this first: iapp_thai_law_section needs the law name to match
    character-for-character, and this returns the exact strings to use.

    Args:
        q: Optional substring filter on the law name.

    Returns:
        JSON string with law names and section counts. Cost: FREE (0 IC).
    """
    try:
        params = {"q": q} if q else None
        response = await request("GET", f"{_BASE}/laws", params=params)
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)


@mcp.tool(
    name="iapp_thai_law_section",
    annotations={"title": "Thai Statute Section Lookup (มาตรา)", **_READONLY},
)
async def iapp_thai_law_section(law: str, section: str, with_deka: bool = False) -> str:
    """Fetch the exact current text of one Thai statute section (มาตรา).

    Deterministic lookup, no model involved — use this when you already know the
    section number and need its verbatim wording.

    Args:
        law: Exact law name, e.g. 'ประมวลกฎหมายอาญา'. Get valid values from iapp_thai_law_list.
        section: Section number as a string, e.g. '335' or '112/1'.
        with_deka: Also return Supreme Court decisions that cite this section.

    Returns:
        JSON string with the verbatim section text, and when with_deka is true the
        ฎีกา citing it. Returns found:false with suggestions on a miss. Cost: 0.1 IC.
    """
    try:
        params = {"law": law, "section": section}
        if with_deka:
            params["with_deka"] = "true"
        response = await request("GET", f"{_BASE}/section", params=params)
        return format_json_response(response) + _CITE_NOTE
    except IAppAPIError as e:
        return str(e)


@mcp.tool(
    name="iapp_thai_law_search",
    annotations={"title": "Thai Statute Semantic Search", **_READONLY},
)
async def iapp_thai_law_search(query: str, top_k: int = 8) -> str:
    """Search 39 Thai statutes (6,363 sections) by meaning, not keywords.

    Hybrid BM25 + Qwen3 dense retrieval with a reranker. Use this when you need
    the right มาตรา but do not know its number.

    Args:
        query: Legal question or fact pattern, in Thai.
        top_k: Sections to return (1-20).

    Returns:
        JSON string with law, section, verbatim text and relevance score. Cost: 0.1 IC.
    """
    try:
        response = await request(
            "POST", f"{_BASE}/search",
            json_body={"query": query, "top_k": min(max(top_k, 1), 20)},
        )
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)


@mcp.tool(
    name="iapp_thai_deka_search",
    annotations={"title": "Thai Supreme Court Decision Search (ฎีกา)", **_READONLY},
)
async def iapp_thai_deka_search(
    query: Optional[str] = None,
    cites_law: Optional[str] = None,
    cites_section: Optional[str] = None,
    year_from: int = 2540,
    year_to: Optional[int] = None,
    top_k: int = 5,
) -> str:
    """Search real Thai Supreme Court decisions (คำพิพากษาศาลฎีกา) from a licensed corpus.

    Every result is a real, retrievable decision with its ฎีกา number and a link to
    the official court record. This tool NEVER invents citations: when nothing
    matches it returns an empty result set. Do not fill that gap from your own
    knowledge — say that no decision was found.

    Combine cites_law + cites_section to answer "which ฎีกา interpret this มาตรา?".

    Args:
        query: Fact pattern or legal issue, in Thai. Optional if citing filters are given.
        cites_law: Restrict to decisions citing this law, abbreviated as the court
            writes it, e.g. 'ป.อ.' (อาญา) or 'ป.พ.พ.' (แพ่งและพาณิชย์).
        cites_section: Restrict to decisions citing this section, e.g. '335'.
        year_from: Earliest Buddhist-era year. Defaults to 2540 — older rulings cite
            superseded section numbering.
        year_to: Latest Buddhist-era year.
        top_k: Decisions to return (1-20).

    Returns:
        JSON string with case_id, year, หลักกฎหมาย headnote, cited sections, a
        citation_join confidence flag and the official court URL. Cost: 0.1 IC.
    """
    try:
        body = {"top_k": min(max(top_k, 1), 20), "year_from": year_from}
        for k, v in (("query", query), ("cites_law", cites_law),
                     ("cites_section", cites_section), ("year_to", year_to)):
            if v is not None:
                body[k] = v
        response = await request("POST", f"{_BASE}/deka/search", json_body=body)
        return format_json_response(response) + _CITE_NOTE
    except IAppAPIError as e:
        return str(e)


@mcp.tool(
    name="iapp_thai_deka_get",
    annotations={"title": "Thai Supreme Court Decision by Number", **_READONLY},
)
async def iapp_thai_deka_get(case_id: str, include_body: bool = False) -> str:
    """Fetch one Thai Supreme Court decision by its ฎีกา number.

    Args:
        case_id: ฎีกา number, '1234/2565' or '1234-2565'. Both forms accepted.
        include_body: Also return the ruling text (capped at 4,000 characters).

    Returns:
        JSON string with the headnote, cited laws and sections, source provenance
        and the official court URL. Cost: 0.1 IC.
    """
    try:
        cid = case_id.replace("/", "-")
        params = {"include": "body"} if include_body else None
        response = await request("GET", f"{_BASE}/deka/{cid}", params=params)
        return format_json_response(response) + _CITE_NOTE
    except IAppAPIError as e:
        return str(e)


@mcp.tool(
    name="iapp_thai_legal_ask",
    annotations={"title": "Grounded Thai Legal Q&A (statutes + ฎีกา)", **_READONLY},
)
async def iapp_thai_legal_ask(
    question: str,
    include_deka: bool = True,
    statute_top_k: int = 6,
    deka_top_k: int = 3,
    max_tokens: int = 1024,
) -> str:
    """Answer a Thai legal question grounded in real statute text AND real ฎีกา.

    Retrieves the applicable มาตรา and Supreme Court decisions first, then answers
    only from what it found. Every ฎีกา number in the answer is machine-verified
    against the retrieved set; if the model cites one that was not provided the
    answer is regenerated once and then refused rather than returned. When nothing
    relevant is retrieved it returns grounded:false instead of guessing.

    Prefer this over iapp_openthai_legal_chat when the answer must cite case law.

    Args:
        question: Legal question in Thai.
        include_deka: Also retrieve and cite Supreme Court decisions.
        statute_top_k: Statute sections to ground on (1-20).
        deka_top_k: Decisions to ground on (1-20).
        max_tokens: Maximum answer length.

    Returns:
        JSON string with the answer, a `grounded` flag, statute and ฎีกา citations
        with official URLs, and any unverified citations. Cost: 0.1 IC.
    """
    try:
        response = await request(
            "POST", f"{_BASE}/ask",
            json_body={"question": question, "include_deka": include_deka,
                       "statute_top_k": min(max(statute_top_k, 1), 20),
                       "deka_top_k": min(max(deka_top_k, 1), 20),
                       "max_tokens": min(max_tokens, 4096)},
        )
        return format_json_response(response) + _CITE_NOTE
    except IAppAPIError as e:
        return str(e)
