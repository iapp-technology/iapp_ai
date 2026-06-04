"""eKYC tools: Thai ID card, passport, driver license, book bank, face APIs."""

from typing import Literal, Optional

from ..app import mcp
from ..client import IAppAPIError, format_json_response, request


@mcp.tool(
    name="iapp_thai_id_card_ocr",
    annotations={
        "title": "Thai National ID Card OCR",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def iapp_thai_id_card_ocr(
    file_path: str,
    side: Literal["front", "back"] = "front",
    options: Optional[str] = None,
) -> str:
    """Extract structured data from a Thai national ID card image (front or back).

    Front side returns ID number, Thai/English name, date of birth, address, religion,
    issue/expiry dates, gender and per-field confidence scores. Back side returns the
    laser code (back_number).

    Args:
        file_path: Local path to the card image (JPEG/PNG/HEIC/PDF, max 10MB).
        side: Which side of the card the image shows ('front' or 'back').
        options: Optional comma-separated flags: not_crop_card, not_rotate_card,
            get_bbox, get_image, get_original.

    Returns:
        JSON string with extracted fields and confidence scores.
        Cost: 1.25 IC (front) / 0.75 IC (back).
    """
    try:
        data = {"options": options} if options else None
        response = await request(
            "POST",
            f"/v3/store/ekyc/thai-national-id-card/{side}",
            data=data,
            file_fields=[("file", file_path)],
        )
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)


@mcp.tool(
    name="iapp_thai_id_card_photocopy_ocr",
    annotations={
        "title": "Thai ID Card (Photocopy) OCR with Signature Detection",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def iapp_thai_id_card_photocopy_ocr(file_path: str) -> str:
    """Extract data from a photographed/photocopied Thai national ID card, including signature detection.

    Use this for photocopies of ID cards (common in Thai KYC paperwork) instead of
    iapp_thai_id_card_ocr, which expects the physical card.

    Args:
        file_path: Local path to the photocopied card image (JPEG/PNG/HEIC, max 2MB,
            min 600x400 px).

    Returns:
        JSON string with national_id, names (TH/EN), date of birth/expiry, address fields,
        signature detection reason codes, and confidence scores. Cost: 1.25 IC.
    """
    try:
        response = await request(
            "POST",
            "/v3/store/ekyc/thai-national-id-card-with-signature",
            file_fields=[("file", file_path)],
        )
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)


@mcp.tool(
    name="iapp_passport_ocr",
    annotations={
        "title": "Passport OCR",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def iapp_passport_ocr(file_path: str, segmentation: bool = False) -> str:
    """Extract MRZ and personal data from a passport image (any country).

    Args:
        file_path: Local path to the passport image (JPEG/PNG/PDF, max 10MB).
        segmentation: Set True to handle skewed/angled photos.

    Returns:
        JSON string with passport number, names, nationality, dates, MRZ checksum
        validity flags and raw MRZ text. Cost: 0.75 IC per page.
    """
    try:
        data = {"options": "segmentation"} if segmentation else None
        response = await request(
            "POST",
            "/v3/store/ekyc/passport/v2",
            data=data,
            file_fields=[("file", file_path)],
        )
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)


@mcp.tool(
    name="iapp_thai_driver_license_ocr",
    annotations={
        "title": "Thai Driver License OCR",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def iapp_thai_driver_license_ocr(file_path: str) -> str:
    """Extract structured data from a Thai driver license card image.

    Args:
        file_path: Local path to the license image (JPEG/PNG, max 10MB).

    Returns:
        JSON string with license number, Thai/English name, date of birth, license type,
        issue/expiry dates. Cost: 1.25 IC.
    """
    try:
        response = await request(
            "POST",
            "/v3/store/ekyc/thai-driver-license",
            file_fields=[("file", file_path)],
        )
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)


@mcp.tool(
    name="iapp_book_bank_ocr",
    annotations={
        "title": "Thai Bank Book OCR",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def iapp_book_bank_ocr(file_path: str) -> str:
    """Extract account details from a Thai bank book (passbook) cover image.

    Args:
        file_path: Local path to the bank book image (JPEG/PNG).

    Returns:
        JSON string with bank name, account number, account name, branch and
        signature detection. Cost: 1.25 IC.
    """
    try:
        response = await request(
            "POST",
            "/v3/store/ekyc/book-bank",
            file_fields=[("file", file_path)],
        )
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)


@mcp.tool(
    name="iapp_face_verification",
    annotations={
        "title": "Face Verification (1:1 Compare)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def iapp_face_verification(
    image1_path: str,
    image2_path: str,
    threshold: Optional[float] = None,
) -> str:
    """Compare two face images and check whether they are the same person (1:1 verification).

    Args:
        image1_path: Local path to the first face image (JPG/PNG/HEIC, max 2MB, min 600x400).
        image2_path: Local path to the second face image (same constraints).
        threshold: Match threshold. Default 36; use 48 for high precision.

    Returns:
        JSON string with matched (boolean), score, threshold and duration. Cost: 0.3 IC.
    """
    try:
        data = {"threshold": threshold} if threshold is not None else None
        response = await request(
            "POST",
            "/v3/store/ekyc/face-verification",
            data=data,
            file_fields=[("file1", image1_path), ("file2", image2_path)],
        )
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)


@mcp.tool(
    name="iapp_face_detection",
    annotations={
        "title": "Face Detection",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def iapp_face_detection(
    file_path: str,
    mode: Literal["single", "multi"] = "single",
) -> str:
    """Detect face(s) in an image and return bounding boxes and detection scores.

    Args:
        file_path: Local path to the image (JPEG/PNG, max 10MB).
        mode: 'single' expects exactly one face; 'multi' detects all faces.

    Returns:
        JSON string with bbox coordinates, detection_score and cropped face (base64,
        truncated in output). Cost: 0.2-0.3 IC.
    """
    try:
        response = await request(
            "POST",
            f"/v3/store/ekyc/face-detection/{mode}",
            file_fields=[("file", file_path)],
        )
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)


@mcp.tool(
    name="iapp_face_liveness",
    annotations={
        "title": "Face Passive Liveness Detection",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def iapp_face_liveness(file_path: str) -> str:
    """Check whether a face photo is of a real live person or a spoof (screen/printout).

    iBeta Level 1 certified passive liveness detection — no user gestures required.

    Args:
        file_path: Local path to the face image (JPEG/PNG, max 10MB).

    Returns:
        JSON string with predict ('REAL' or 'SPOOF'), score (0-1) and darkness metric.
        Cost: 0.3 IC.
    """
    try:
        response = await request(
            "POST",
            "/v3/store/ekyc/face-passive-liveness",
            file_fields=[("file", file_path)],
        )
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)


@mcp.tool(
    name="iapp_face_id_card_kyc",
    annotations={
        "title": "Face + ID Card KYC Verification",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def iapp_face_id_card_kyc(id_card_path: str, selfie_path: str) -> str:
    """Verify that a selfie matches the face photo on a Thai national ID card (full KYC check).

    Args:
        id_card_path: Local path to the ID card image (JPG/PNG, min 600x400, max 10MB).
        selfie_path: Local path to the selfie image (same constraints).

    Returns:
        JSON string with per-image and total confidence plus isSamePerson verdicts.
        Cost: 1 IC.
    """
    try:
        response = await request(
            "POST",
            "/v3/store/ekyc/face-and-id-card-verification",
            file_fields=[("file0", id_card_path), ("file1", selfie_path)],
        )
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)


@mcp.tool(
    name="iapp_face_recognition",
    annotations={
        "title": "Face Recognition (1:N Search / Enroll)",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def iapp_face_recognition(
    action: Literal["recognize_single", "recognize_multi", "add", "remove", "check"],
    company: str,
    file_path: Optional[str] = None,
    name: Optional[str] = None,
    password: Optional[str] = None,
    face_id: Optional[str] = None,
) -> str:
    """Search, enroll or manage faces in a company face database (1:N recognition).

    Actions:
        - recognize_single: identify one face in the image (requires file_path)
        - recognize_multi: identify all faces in the image (requires file_path)
        - add: enroll a face (requires file_path, name, password) — modifies the database
        - remove: delete an enrolled face (requires name, password; optional face_id) — destructive
        - check: list enrolled faces (requires password)

    Args:
        action: Operation to perform.
        company: Company namespace of the face database.
        file_path: Local path to a face image (JPEG/PNG, max 2MB) for recognize/add.
        name: Person name for add/remove.
        password: Company password for add/remove/check.
        face_id: Specific face ID to remove (optional).

    Returns:
        JSON string with recognition matches/scores or operation status.
        Cost: 0.3 IC (recognize/check), 0.1 IC (add), 0 IC (remove).
    """
    try:
        endpoint_map = {
            "recognize_single": "/v3/store/ekyc/face-recognition/single",
            "recognize_multi": "/v3/store/ekyc/face-recognition/multi",
            "add": "/v3/store/ekyc/face-recognition/add",
            "remove": "/v3/store/ekyc/face-recognition/remove",
            "check": "/v3/store/ekyc/face-recognition/check",
        }
        data = {"company": company}
        if name:
            data["name"] = name
        if password:
            data["password"] = password
        if face_id:
            data["face_id"] = face_id

        needs_file = action in ("recognize_single", "recognize_multi", "add")
        if needs_file and not file_path:
            return f"Error: action '{action}' requires file_path."
        if action in ("add", "remove", "check") and not password:
            return f"Error: action '{action}' requires password."
        if action in ("add", "remove") and not name:
            return f"Error: action '{action}' requires name."

        response = await request(
            "POST",
            endpoint_map[action],
            data=data,
            file_fields=[("file", file_path)] if needs_file else None,
        )
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)
