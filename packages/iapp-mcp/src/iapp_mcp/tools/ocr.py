"""Thai document OCR tools: general documents, receipts, statements, certificates, CV/JD."""

from typing import Literal

from ..app import mcp
from ..client import IAppAPIError, format_json_response, request

_READONLY = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": True,
}


@mcp.tool(
    name="iapp_document_ocr",
    annotations={"title": "Thai Document OCR", **_READONLY},
)
async def iapp_document_ocr(
    file_path: str,
    mode: Literal["text", "layout", "docx"] = "text",
) -> str:
    """OCR any Thai (or mixed Thai/English) document into text, layout JSON, or a DOCX file.

    Supports PNG, JPEG, PDF, DOC(X), XLS(X), PPT(X) up to 30MB.

    Args:
        file_path: Local path to the document file.
        mode: 'text' returns plain text per page; 'layout' returns components with
            bounding boxes and types; 'docx' returns a signed download URL for a
            converted DOCX (valid 10 minutes).

    Returns:
        JSON string with OCR results. Cost: 1 IC per page.
    """
    endpoint = {
        "text": "/v3/store/ocr/document/ocr",
        "layout": "/v3/store/ocr/document/layout",
        "docx": "/v3/store/ocr/document/docx",
    }[mode]
    try:
        response = await request("POST", endpoint, file_fields=[("file", file_path)])
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)


async def _simple_file_ocr(endpoint: str, file_path: str, return_ocr: bool = False) -> str:
    """Shared implementation for single-file OCR endpoints with optional raw OCR text."""
    try:
        data = {"return_ocr": "true"} if return_ocr else None
        response = await request("POST", endpoint, data=data, file_fields=[("file", file_path)])
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)


@mcp.tool(
    name="iapp_receipt_ocr",
    annotations={"title": "Thai Receipt OCR", **_READONLY},
)
async def iapp_receipt_ocr(file_path: str, return_ocr: bool = False) -> str:
    """Extract structured data from a Thai receipt / tax invoice image or PDF.

    Args:
        file_path: Local path to the receipt (JPEG/PNG/PDF, max 10MB).
        return_ocr: Set True to also include the raw OCR text.

    Returns:
        JSON string with invoice info, issuer/customer details, line items, totals,
        VAT and per-field confidence. Cost: 1 IC per page.
    """
    return await _simple_file_ocr("/ocr/v3/receipt/file", file_path, return_ocr)


@mcp.tool(
    name="iapp_credit_card_statement_ocr",
    annotations={"title": "Thai Credit Card Statement OCR", **_READONLY},
)
async def iapp_credit_card_statement_ocr(file_path: str, return_ocr: bool = False) -> str:
    """Extract structured data from a Thai credit card statement (image or PDF up to 10 pages).

    Args:
        file_path: Local path to the statement (JPEG/PNG/HEIC/PDF, max 10MB).
        return_ocr: Set True to also include the raw OCR text.

    Returns:
        JSON string with card/bank details, balances, due dates, transactions list,
        reward points and confidence scores. Cost: 1 IC per page.
    """
    return await _simple_file_ocr("/ocr/v3/creditcard-statement/file", file_path, return_ocr)


@mcp.tool(
    name="iapp_tax_deduction_certificate_ocr",
    annotations={"title": "Thai Tax Deduction Certificate OCR", **_READONLY},
)
async def iapp_tax_deduction_certificate_ocr(file_path: str, return_ocr: bool = False) -> str:
    """Extract data from a Thai withholding tax deduction certificate (50 ทวิ).

    Processing takes ~25-30 seconds.

    Args:
        file_path: Local path to the certificate (JPEG/PNG/HEIC/PDF, max 10MB).
        return_ocr: Set True to also include the raw OCR text.

    Returns:
        JSON string with deductor/taxpayer info, payment types, total amounts and taxes.
        Cost: 1 IC per page.
    """
    return await _simple_file_ocr("/ocr/v3/tax-deduction-certificate/file", file_path, return_ocr)


@mcp.tool(
    name="iapp_civil_registration_ocr",
    annotations={"title": "Thai Civil Registration Certificate OCR", **_READONLY},
)
async def iapp_civil_registration_ocr(file_path: str, return_ocr: bool = False) -> str:
    """Extract data from a Thai civil registration certificate (ทะเบียนราษฎร).

    Args:
        file_path: Local path to the certificate (JPEG/PNG/PDF single page, max 10MB).
        return_ocr: Set True to also include the raw OCR text.

    Returns:
        JSON string with national ID, names, parents, address, registration office and
        confidence scores. Cost: 1 IC per page.
    """
    return await _simple_file_ocr(
        "/ocr/v3/civil-registeration-certificate/file", file_path, return_ocr
    )


@mcp.tool(
    name="iapp_resume_ocr",
    annotations={"title": "AI Resume / CV Extraction & Evaluation", **_READONLY},
)
async def iapp_resume_ocr(file_path: str) -> str:
    """Extract structured information from a resume/CV and get an AI evaluation.

    Args:
        file_path: Local path to the resume (PDF/JPG/PNG).

    Returns:
        JSON string with personal info, education, work experience, skills, plus an AI
        evaluation: scores, ATS compatibility, strengths/weaknesses, improvement
        suggestions. Cost: 1 IC per page.
    """
    return await _simple_file_ocr("/v3/store/ocr/curriculum-vitae", file_path)


@mcp.tool(
    name="iapp_job_description_ocr",
    annotations={"title": "AI Job Description Extraction", **_READONLY},
)
async def iapp_job_description_ocr(file_path: str) -> str:
    """Extract structured information from a job description document.

    Args:
        file_path: Local path to the job description (PDF/JPG/PNG).

    Returns:
        JSON string with job title, company, location, salary range, responsibilities,
        qualifications and AI-suggested skills. Cost: 1 IC per page.
    """
    return await _simple_file_ocr("/v3/store/ocr/job-description", file_path)
