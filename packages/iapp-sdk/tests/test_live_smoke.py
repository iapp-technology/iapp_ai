"""Live integration smoke tests for the docs-aligned NLP/Speech endpoints.

These hit the real ``api.iapp.co.th`` and require a valid ``IAPP_API_KEY``. They
are skipped automatically when the key is unset (see ``conftest.py``).

The text-only NLP tests (translate, summarize, QA, question generation) need no
media fixtures. The TTS tests synthesize audio and just assert a non-empty
response is written to disk. The ASR test prefers a real audio file via
``IAPP_TEST_AUDIO``, but falls back to a synthetic valid WAV it generates on the
fly (16 kHz mono PCM16 with a soft tone) so the endpoint can still be smoke-
tested without hunting for a sample — the transcript may be empty, but a 200
confirms the SDK reaches the live ASR endpoint correctly.

They exist to confirm the SDK still talks to the live API end to end after the
endpoints were repointed to match the live API.
"""

import math
import os
import struct
import wave

import requests

from iapp_ai import api

KEY = os.environ.get("IAPP_API_KEY", "")
AUDIO = os.environ.get("IAPP_TEST_AUDIO", "")

THAI_TEXT = (
    "ประเทศไทยมีวัฒนธรรมและประวัติศาสตร์อันยาวนาน "
    "และมีสถานที่ท่องเที่ยวที่มีชื่อเสียงมากมายทั่วทุกภูมิภาค"
)


def _make_wav(path, seconds=2.0, rate=16000, freq=220.0, amplitude=0.2):
    """Write a valid mono 16-bit PCM WAV with a soft sine tone (stdlib only).

    Not speech, so the transcript is typically empty — but it is a real,
    decodable audio file, which is enough to smoke-test that the ASR endpoint
    accepts the upload and returns 200.
    """
    n_frames = int(seconds * rate)
    peak = int(amplitude * 32767)
    frames = bytearray()
    for i in range(n_frames):
        sample = int(peak * math.sin(2 * math.pi * freq * (i / rate)))
        frames += struct.pack("<h", sample)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(bytes(frames))
    return str(path)


# =========================================================================== #
# Live smoke checks for the NLP / Speech endpoints. Each confirms the SDK
# reaches the live API and gets a 200 back.
#   * eng_thai_translate      -> POST /v3/store/nlp/multilingual-translation
#   * thai_text_summarization -> POST /v3/store/nlp/thai-text-summary
#   * thai_qa_api             -> POST /thai-qa
#   * thai_qgen_api           -> GET  /v3/store/nlp/question/generation?text=
#   * thai_thaitts_kaitom     -> POST /v3/store/audio/tts
#   * thai_asr_api            -> POST /v3/store/speech/speech-to-text/base
# =========================================================================== #


def test_translate_live():
    # POST /v3/store/nlp/multilingual-translation
    resp = api(KEY).eng_thai_translate("hello", source_lang="en", target_lang="th")
    assert isinstance(resp, requests.Response)
    assert resp.status_code == 200, resp.text


def test_summarization_live():
    # POST /v3/store/nlp/thai-text-summary
    resp = api(KEY).thai_text_summarization(THAI_TEXT, style="standard", language="th")
    assert isinstance(resp, requests.Response)
    assert resp.status_code == 200, resp.text


def test_qa_live():
    # POST /thai-qa
    resp = api(KEY).thai_qa_api(
        question="เมืองหลวงของประเทศไทยคือที่ไหน",
        document="กรุงเทพมหานครเป็นเมืองหลวงของประเทศไทย",
    )
    assert isinstance(resp, requests.Response)
    assert resp.status_code == 200, resp.text


def test_question_generation_live():
    # GET /v3/store/nlp/question/generation?text=
    resp = api(KEY).thai_qgen_api(THAI_TEXT)
    assert isinstance(resp, requests.Response)
    assert resp.status_code == 200, resp.text


def test_tts_kaitom_live(tmp_path):
    # POST /v3/store/audio/tts
    out = tmp_path / "kaitom.wav"
    resp = api(KEY).thai_thaitts_kaitom("สวัสดีครับ ทดสอบเสียง", output_path=str(out))
    assert isinstance(resp, requests.Response)
    assert resp.status_code == 200, resp.text
    assert out.exists() and out.stat().st_size > 0


def test_asr_live(tmp_path):
    # POST /v3/store/speech/speech-to-text/base
    # Prefer a real recording if provided, else generate a valid WAV on the fly.
    audio = AUDIO if (AUDIO and os.path.exists(AUDIO)) else _make_wav(tmp_path / "tone.wav")
    resp = api(KEY).thai_asr_api(audio)
    assert isinstance(resp, requests.Response)
    assert resp.status_code == 200, resp.text
