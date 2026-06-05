"""Speech tools: speech-to-text (TH/EN/ZH), text-to-speech, voice cloning, AI audio detection."""

from typing import Literal, Optional

from ..app import mcp
from ..client import (
    IAppAPIError,
    format_json_response,
    request,
    save_binary,
    save_pcm_as_wav,
)

# (language, quality) -> endpoint path
_STT_ENDPOINTS = {
    ("th", "base"): "/v3/store/speech/speech-to-text/base",
    ("th", "pro"): "/v3/store/speech/speech-to-text/pro",
    ("en", "base"): "/v3/store/speech/speech-to-text/base/en",
    ("en", "pro"): "/v3/store/speech/speech-to-text/pro/en",
    ("zh", "base"): "/v3/store/speech/speech-to-text/base/zh",
    ("zh", "pro"): "/v3/store/speech/speech-to-text/pro/zh",
}


@mcp.tool(
    name="iapp_speech_to_text",
    annotations={
        "title": "Speech-to-Text (Thai/English/Chinese)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def iapp_speech_to_text(
    file_path: str,
    language: Literal["th", "en", "zh"] = "th",
    quality: Literal["base", "pro"] = "base",
    chunk_size: Optional[int] = None,
) -> str:
    """Transcribe an audio file to text with timestamps and speaker diarization.

    Args:
        file_path: Local path to the audio file (.mp3/.wav/.aac/.m4a and more).
        language: Audio language — 'th' (Thai), 'en' (English), 'zh' (Chinese).
        quality: 'base' (1 IC/min) or 'pro' (LLM-enhanced, 2 IC/min).
        chunk_size: Optional chunk size in seconds (recommended 7 for Thai, 20 for EN/ZH).

    Returns:
        JSON string with transcript segments: text, start/end timestamps, speaker labels.
    """
    try:
        data = {}
        if chunk_size is not None:
            data["chunk_size"] = str(chunk_size)
        if quality == "pro":
            data["use_asr_pro"] = "1"
        response = await request(
            "POST",
            _STT_ENDPOINTS[(language, quality)],
            data=data or None,
            file_fields=[("file", file_path)],
        )
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)


@mcp.tool(
    name="iapp_text_to_speech",
    annotations={
        "title": "Thai Text-to-Speech",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def iapp_text_to_speech(
    text: str,
    output_path: str,
    voice: Literal["kaitom-v3", "kaitom-v2", "kaitom-v1", "cee"] = "kaitom-v3",
    speed: float = 1.0,
) -> str:
    """Convert Thai (or mixed Thai/English) text to speech and save the audio locally.

    Voices:
        - kaitom-v3: latest Kaitom voice, Thai+English auto-detect, WAV 24kHz (recommended)
        - kaitom-v2: Kaitom voice V2, WAV
        - kaitom-v1: young boy voice (น้องไข่ต้ม), MP3
        - cee: female celebrity voice (ฉัตรปวีณ์ ตรีชัชวาลวงศ์), WAV

    Args:
        text: Text to synthesize (max 10,000 chars for v3; ~1,000 recommended per call).
        output_path: Local path to save the audio file (use .wav, or .mp3 for kaitom-v1).
        voice: Voice to use.
        speed: Speaking speed for kaitom-v3 only (natural range 0.8-1.2, default 1.0).

    Returns:
        Confirmation message with the saved audio file path. Cost: 1 IC per 400 chars
        (kaitom-v3 free until 2026-05-31).
    """
    try:
        if voice == "kaitom-v3":
            response = await request(
                "POST",
                "/v3/store/audio/tts",
                json_body={"text": text, "speed": speed},
            )
            path = save_pcm_as_wav(response.content, output_path)
        elif voice == "kaitom-v2":
            response = await request(
                "POST",
                "/v3/store/speech/text-to-speech/kaitom",
                data={"text": text, "language": "TH_MIX_EN"},
            )
            path = save_binary(response.content, output_path)
        elif voice == "kaitom-v1":
            response = await request(
                "GET",
                "/v3/store/speech/text-to-speech/kaitom/v1",
                params={"text": text},
            )
            path = save_binary(response.content, output_path)
        else:  # cee
            response = await request(
                "GET",
                "/v3/store/speech/text-to-speech/cee",
                params={"text": text},
            )
            path = save_binary(response.content, output_path)
        return f"Audio saved to {path} ({len(response.content)} bytes, voice={voice})"
    except IAppAPIError as e:
        return str(e)


@mcp.tool(
    name="iapp_voice_clone_tts",
    annotations={
        "title": "Thai Voice Cloning TTS",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def iapp_voice_clone_tts(
    text: str,
    ref_audio_path: str,
    ref_text: str,
    output_path: str,
    speed: float = 1.0,
) -> str:
    """Synthesize Thai speech in a cloned voice from a short reference audio sample.

    Args:
        text: Thai text to synthesize.
        ref_audio_path: Local path to reference audio (WAV/MP3, 8-12s optimal, max 15s,
            clean single-speaker Thai).
        ref_text: Exact word-for-word Thai transcript of the reference audio.
        output_path: Local path to save the synthesized audio (.wav).
        speed: Speaking speed (default 1.0).

    Returns:
        Confirmation message with the saved audio file path. Cost: 1 IC per 400 chars
        (free until 2026-05-31).
    """
    try:
        response = await request(
            "POST",
            "/v3/store/audio/tts/clone",
            data={"text": text, "ref_text": ref_text, "speed": str(speed)},
            file_fields=[("ref_audio", ref_audio_path)],
        )
        path = save_pcm_as_wav(response.content, output_path)
        return f"Cloned-voice audio saved to {path} ({len(response.content)} bytes)"
    except IAppAPIError as e:
        return str(e)


@mcp.tool(
    name="iapp_ai_audio_detection",
    annotations={
        "title": "AI-Generated Audio Detection",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def iapp_ai_audio_detection(audio_path: str) -> str:
    """Detect whether an audio file was generated by iApp TTS (AI watermark detection).

    Args:
        audio_path: Local path to the audio file (WAV any sample rate, or raw PCM
            24kHz mono int16).

    Returns:
        JSON string with is_ai_generated (boolean) and confidence (0-1). Free.
    """
    try:
        response = await request(
            "POST",
            "/v3/store/audio/tts/detect",
            file_fields=[("audio", audio_path)],
        )
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)
