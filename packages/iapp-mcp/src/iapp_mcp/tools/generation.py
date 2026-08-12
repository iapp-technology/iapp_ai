"""Image and video generation tools: Nano Banana, background removal, Seedance video."""

import base64
from typing import Literal, Optional

from ..app import mcp
from ..client import (
    IAppAPIError,
    format_json_response,
    request,
    save_binary,
)

_VIDEO_MODELS = {
    "seedance": "dreamina-seedance-2-0-260128",
    "seedance-fast": "dreamina-seedance-2-0-fast-260128",
}


@mcp.tool(
    name="iapp_image_generation",
    annotations={
        "title": "Image Generation (Google Nano Banana)",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def iapp_image_generation(
    prompt: str,
    output_path: str,
    model: Literal["nanobanana", "nanobanana-pro"] = "nanobanana",
) -> str:
    """Generate an image from a text prompt using Google Nano Banana via iApp and save it locally.

    Args:
        prompt: Text prompt describing the image (max 32,000 chars).
        output_path: Local path to save the generated image (.png).
        model: 'nanobanana' (Gemini 2.5 Flash Image, 3 IC) or 'nanobanana-pro'
            (Gemini 3 Pro Image, 8 IC).

    Returns:
        Confirmation message with the saved image path, plus any text the model returned.
        Latency 5-30 seconds.
    """
    # Both routes confirmed correct with the iApp team (verified 2026-06).
    endpoint = (
        "/v3/image/generation/google/nanobanana/generate"
        if model == "nanobanana"
        else "/v3/image/generation/google/nanobananapro/generate"
    )
    try:
        response = await request(
            "POST",
            endpoint,
            json_body={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
            },
        )
        payload = response.json()
        saved_path = None
        text_parts = []
        for candidate in payload.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                inline = part.get("inlineData")
                if inline and inline.get("data") and saved_path is None:
                    saved_path = save_binary(base64.b64decode(inline["data"]), output_path)
                elif part.get("text"):
                    text_parts.append(part["text"])
        if saved_path is None:
            return f"Error: No image data in response. Raw response: {str(payload)[:500]}"
        result = f"Image saved to {saved_path}"
        if text_parts:
            result += "\n\nModel notes: " + "\n".join(text_parts)
        return result
    except IAppAPIError as e:
        return str(e)
    except (ValueError, KeyError) as e:
        return f"Error: Unexpected image generation response format: {e}"


@mcp.tool(
    name="iapp_slide_generation",
    annotations={
        "title": "Slide Generation (presentation slide as an image)",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def iapp_slide_generation(
    title: str,
    content: str,
    output_path: str,
    style: Optional[str] = None,
    aspect_ratio: Literal["16:9", "4:3"] = "16:9",
) -> str:
    """Generate a finished presentation slide as an image and save it locally.

    Renders the headline, body points and any chart or diagram together on one
    slide. Built on Nano Banana Pro so text and figures stay legible. Call once
    per slide to build a deck, keeping `style` identical across calls so the
    deck reads as one set. For a plain picture with no slide framing, use
    iapp_image_generation instead.

    Args:
        title: Slide headline, kept short — rendered large at the top.
        content: What the slide should say or show — bullet points one per line,
            a chart description ('bar chart of revenue by quarter: Q1 12M, ...'),
            or a diagram description.
        output_path: Local path to save the slide (.png).
        style: Visual style, reused across the deck. Defaults to clean corporate.
        aspect_ratio: '16:9' for normal decks, '4:3' for legacy projectors.

    Returns:
        Confirmation message with the saved slide path. Cost: 8 IC per slide
        (Nano Banana Pro), paid accounts only.
    """
    slide_style = style or (
        "clean corporate presentation, white background, a single accent colour, "
        "generous whitespace, flat vector illustration"
    )
    dimensions = "2048x1152" if aspect_ratio == "16:9" else "2048x1536"
    # The layout rules are spelled out because the expensive failure is not a slow
    # render — it is a slide that comes back with text on top of other text, which
    # the caller throws away and rebuilds by hand, paying for the render twice.
    prompt = (
        f"A single {aspect_ratio} presentation slide, {dimensions}, high resolution.\n"
        f"Headline across the top, rendered exactly as written and spelled correctly: "
        f'"{title}"\n\n'
        f"Slide body:\n{content}\n\n"
        f"Style: {slide_style}.\n\n"
        "Layout rules (follow strictly):\n"
        "- Keep a clear margin of at least 6% of the slide on every edge; nothing "
        "touches the edge.\n"
        "- Text must NEVER overlap other text, icons, charts or shapes. If the content "
        "will not fit, use fewer words — shortening is always preferred to crowding.\n"
        "- At most 6 bullet points, at most ~12 words each, in one column (or two "
        "clearly separated columns).\n"
        "- One idea per line. Do not wrap a bullet into more than two lines.\n"
        "- Render ONLY the slide content: no speaker notes, no notes panel, no slide "
        "numbers, no footer, no thumbnail strip, no presenter UI.\n"
        "- Do not draw a laptop, monitor, projector, room, desk, hands or any frame "
        "around the slide.\n"
        "- All text sharp, correctly spelled, and large enough to read from the back "
        "of a room.\n"
        "- No lorem ipsum, no placeholder text, no watermark, no signature."
    )
    return await iapp_image_generation(
        prompt=prompt, output_path=output_path, model="nanobanana-pro"
    )


@mcp.tool(
    name="iapp_remove_background",
    annotations={
        "title": "Image Background Removal",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def iapp_remove_background(file_path: str, output_path: str) -> str:
    """Remove the background from an image and save the result locally.

    Args:
        file_path: Local path to the input image (PNG/JPEG, max 2MB).
        output_path: Local path to save the background-removed image.

    Returns:
        Confirmation message with the saved image path. Cost: 1 IC.
    """
    try:
        response = await request(
            "POST",
            "/v3/store/smart-city/remove-background",
            file_fields=[("file", file_path)],
        )
        path = save_binary(response.content, output_path)
        return f"Background-removed image saved to {path} ({len(response.content)} bytes)"
    except IAppAPIError as e:
        return str(e)


@mcp.tool(
    name="iapp_video_generation_submit",
    annotations={
        "title": "Video Generation — Submit Job (Seedance 2.0)",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def iapp_video_generation_submit(
    prompt: str,
    model: Literal["seedance", "seedance-fast"] = "seedance-fast",
    duration: int = 5,
    ratio: Literal["16:9", "9:16", "1:1", "4:3", "3:4", "21:9"] = "16:9",
    resolution: Literal["480p", "720p", "1080p"] = "720p",
    generate_audio: bool = True,
    watermark: bool = False,
    first_frame_image_url: Optional[str] = None,
    reference_image_url: Optional[str] = None,
) -> str:
    """Submit an async video generation job (Seedance 2.0). Poll with iapp_video_generation_status.

    Args:
        prompt: Text description of the video to generate.
        model: 'seedance' (higher quality) or 'seedance-fast' (cheaper/faster).
        duration: Video length in seconds (4-15, default 5).
        ratio: Aspect ratio.
        resolution: Output resolution ('1080p' not available on seedance-fast).
        generate_audio: Whether to generate audio.
        watermark: Whether to add a watermark.
        first_frame_image_url: Optional public image URL to use as the first frame.
        reference_image_url: Optional public image URL to use as a style/content reference.

    Returns:
        JSON string with the task id — pass it to iapp_video_generation_status.
        Pricing: ~0.14-0.33 IC per 1K output tokens; failed jobs cost 0 IC.
    """
    try:
        content = [{"type": "text", "text": prompt}]
        if first_frame_image_url:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": first_frame_image_url},
                    "role": "first_frame",
                }
            )
        if reference_image_url:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": reference_image_url},
                    "role": "reference_image",
                }
            )
        response = await request(
            "POST",
            "/v3/store/video/seedance/tasks",
            json_body={
                "model": _VIDEO_MODELS[model],
                "content": content,
                "duration": duration,
                "ratio": ratio,
                "resolution": resolution,
                "generate_audio": generate_audio,
                "watermark": watermark,
            },
        )
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)


@mcp.tool(
    name="iapp_video_generation_status",
    annotations={
        "title": "Video Generation — Check Job Status",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def iapp_video_generation_status(task_id: str) -> str:
    """Check the status of a Seedance video generation job and get the video URL when done.

    Poll every ~5 seconds. Terminal states: succeeded, failed, cancelled, expired.

    Args:
        task_id: Task id returned by iapp_video_generation_submit.

    Returns:
        JSON string with status and, when succeeded, the video download URL
        (URL expires ~24 hours after generation).
    """
    try:
        response = await request("GET", f"/v3/store/video/seedance/tasks/{task_id}")
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)
