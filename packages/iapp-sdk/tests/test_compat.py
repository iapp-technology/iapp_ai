"""Offline backward-compatibility guard for the iApp AI SDK.

These tests monkeypatch the shared ``request_sync`` so they run with no network
and no API key. They lock down the behaviors existing users depend on:

* methods return the raw ``requests.Response`` and do NOT raise on 4xx,
* the API key is injected,
* endpoint URLs (including legacy quirks: leading space, plain http, the
  non-iApp host) are preserved verbatim,
* multipart file tuples keep their exact field names and content types.
"""

import base64
import json

import pytest
import requests

import iapp_ai
import iapp_ai.module_api as module_api
from iapp_ai import api


@pytest.fixture
def captured(monkeypatch):
    """Replace request_sync with a recorder that returns a fake 403 Response."""
    calls = {}

    def fake_request_sync(
        method,
        url,
        *,
        apikey,
        headers=None,
        params=None,
        data=None,
        json_body=None,
        files=None,
        raise_for_error=False,
        timeout=None,
    ):
        # Close any opened file handles to avoid ResourceWarnings.
        for item in files or []:
            handle = item[1][1] if isinstance(item[1], (list, tuple)) and len(item[1]) > 1 else None
            if hasattr(handle, "close"):
                handle.close()
        calls.clear()
        calls.update(
            method=method,
            url=url,
            apikey=apikey,
            headers=headers,
            params=params,
            data=data,
            json_body=json_body,
            files=files,
            raise_for_error=raise_for_error,
            timeout=timeout,
        )
        resp = requests.Response()
        resp.status_code = 403
        resp._content = b'{"ok": false}'
        resp.url = url.strip()
        return resp

    monkeypatch.setattr(module_api, "request_sync", fake_request_sync)
    return calls


def test_version_is_fixed():
    # __version__ must stay in sync with pyproject for the 2.0.0 release.
    assert iapp_ai.__version__ == "2.0.0"


def test_returns_raw_response_and_does_not_raise(captured):
    client = api("MY_KEY")
    resp = client.eng_thai_translate("hello")
    assert isinstance(resp, requests.Response)
    assert resp.status_code == 403  # 4xx is RETURNED, never raised
    assert captured["apikey"] == "MY_KEY"
    # Translation is a POST with a JSON body (no query string).
    assert captured["method"] == "POST"
    assert captured["url"] == "https://api.iapp.co.th/v3/store/nlp/multilingual-translation"
    assert captured["json_body"] == {"text": "hello", "source_lang": "en", "target_lang": "th"}
    assert captured["raise_for_error"] is False


def test_json_endpoint_sets_content_type(captured):
    client = api("K")
    client.thai_qa_api(question="q", document="d")
    assert captured["url"] == "https://api.iapp.co.th/v3/store/nlp/question/answer/v3"
    assert captured["headers"].get("Content-Type") == "application/json"
    assert json.loads(captured["data"]) == {"question": "q", "document": "d"}


def test_idcard_front_url_and_content_type(captured, tmp_path):
    f = tmp_path / "id.jpg"
    f.write_bytes(b"\xff\xd8\xff")
    api("K").idcard_front(str(f))
    assert captured["url"] == "https://api.iapp.co.th/v3/store/ekyc/thai-national-id-card/front"
    field, filetuple = captured["files"][0]
    assert field == "file"
    assert filetuple[0] == "id.jpg"      # basename used as filename
    assert filetuple[2] == "image/jpg"   # exact legacy content type, not image/jpeg


def test_photocopied_url_is_trimmed(captured, tmp_path):
    f = tmp_path / "id.jpg"
    f.write_bytes(b"x")
    api("K").idcard_front_photocopied(str(f))
    assert captured["url"] == "https://api.iapp.co.th/v3/store/ekyc/thai-national-id-card-with-signature"


def test_face_verification_two_files_octet_stream(captured, tmp_path):
    f1 = tmp_path / "a.jpg"
    f1.write_bytes(b"a")
    f2 = tmp_path / "b.jpg"
    f2.write_bytes(b"b")
    api("K").face_verification(str(f1), str(f2), "acme", 0.5)
    assert captured["url"] == "https://api.iapp.co.th/v3/store/ekyc/face-verification"
    assert captured["data"]["company"] == "acme"
    assert captured["data"]["threshold"] == 0.5
    fields = [item[0] for item in captured["files"]]
    assert fields == ["file1", "file2"]
    assert all(item[1][2] == "application/octet-stream" for item in captured["files"])


def test_face_id_card_verification_uses_file0_file1(captured, tmp_path):
    idc = tmp_path / "idcard.jpg"
    idc.write_bytes(b"idcard")
    selfie = tmp_path / "selfie.jpg"
    selfie.write_bytes(b"selfie")
    api("K").face_id_card_verification(str(idc), str(selfie))
    assert captured["url"] == "https://api.iapp.co.th/v3/store/ekyc/face-and-id-card-verification"
    fields = [item[0] for item in captured["files"]]
    assert fields == ["file0", "file1"]  # file0=id card, file1=selfie
    assert all(item[1][2] == "application/octet-stream" for item in captured["files"])


def test_asr_uses_v3_base_path_filename_and_mpga(captured, tmp_path):
    f = tmp_path / "speech.mp3"
    f.write_bytes(b"x")
    api("K").thai_asr_api(str(f))
    assert captured["url"] == "https://api.iapp.co.th/v3/store/speech/speech-to-text/base"
    _field, filetuple = captured["files"][0]
    assert filetuple[0] == str(f)        # raw path used as filename (legacy quirk preserved)
    assert filetuple[2] == "audio/mpga"


def test_power_meter_uses_official_endpoint(captured, tmp_path):
    # Official iApp host (no private titipakorn.xyz); the image is read in binary
    # and base64-encoded into the JSON body (round-trips). Because it sends a
    # base64 JSON body, it must hit the /base64 variant (the /file variant is
    # multipart per the docs).
    raw = b"\xff\xd8\xff\x00meter"
    f = tmp_path / "m.jpg"
    f.write_bytes(raw)
    api("K").power_meter(image=str(f))
    assert captured["url"] == "https://api.iapp.co.th/v3/store/smart-city/power-meter-and-water-meter"
    assert "titipakorn" not in captured["url"]
    assert captured["headers"].get("Content-Type") == "application/json"
    assert base64.b64decode(json.loads(captured["data"])["image"]) == raw


def test_passport_ocr_uses_two_tuple_file(captured, tmp_path):
    f = tmp_path / "p.jpg"
    f.write_bytes(b"x")
    api("K").passport_ocr(str(f))
    assert captured["url"] == "https://api.iapp.co.th/v3/store/ekyc/passport"
    # passport uses a 2-tuple (no content type) — must not gain one
    assert len(captured["files"][0][1]) == 2


# =========================================================================== #
# NLP / Speech endpoint contract tests.
#
# These lock down the request shape (method, URL, JSON body, Content-Type and
# multipart fields) of every NLP/Speech method against the iApp AI API. They
# reuse the `captured` fixture above (which returns a fake response with the
# body b'{"ok": false}'), so the TTS tests assert that body is what gets written
# to the output file.
#
# Endpoints under test:
#   * eng_thai_translate      -> POST /v3/store/nlp/multilingual-translation  (JSON)
#   * thai_text_summarization -> POST /v3/store/nlp/thai-text-summary         (JSON)
#   * thai_qa_api             -> POST /thai-qa                                (JSON)
#   * thai_qgen_api           -> GET  /v3/store/nlp/question/generation       (query)
#   * thai_thaitts_kaitom     -> POST /v3/store/audio/tts                     (JSON)
#   * thai_thaitts_cee        -> POST /v3/store/audio/tts                     (JSON)
#   * thai_asr_api            -> POST /v3/store/speech/speech-to-text/base    (multipart)
# =========================================================================== #


# --- eng_thai_translate -> POST /v3/store/nlp/multilingual-translation ------ #
def test_translate_posts_json_to_multilingual_endpoint(captured):
    api("K").eng_thai_translate("hello")
    assert captured["method"] == "POST"
    assert captured["url"] == "https://api.iapp.co.th/v3/store/nlp/multilingual-translation"
    # Required fields present; defaults keep the original eng->thai direction.
    assert captured["json_body"] == {"text": "hello", "source_lang": "en", "target_lang": "th"}
    assert captured["headers"]["Content-Type"] == "application/json"
    assert captured["files"] is None  # JSON body, not multipart/query


def test_translate_passes_source_target_and_max_length(captured):
    api("K").eng_thai_translate("สวัสดี", source_lang="th", target_lang="ja", max_length=128)
    assert captured["json_body"] == {
        "text": "สวัสดี",
        "source_lang": "th",
        "target_lang": "ja",
        "max_length": 128,
    }


# --- thai_text_summarization -> POST /v3/store/nlp/thai-text-summary -------- #
def test_summarization_posts_json_to_summary_endpoint(captured):
    api("K").thai_text_summarization("ข้อความยาว ๆ")
    assert captured["method"] == "POST"
    assert captured["url"] == "https://api.iapp.co.th/v3/store/nlp/thai-text-summary"
    # With no options, only the required `text` field is sent as a JSON body.
    assert captured["json_body"] == {"text": "ข้อความยาว ๆ"}
    assert "output_length" not in captured["json_body"]
    assert captured["headers"]["Content-Type"] == "application/json"


def test_summarization_includes_optional_fields_only_when_set(captured):
    api("K").thai_text_summarization(
        "text", style="friendly", language="en", max_output_tokens=256
    )
    assert captured["json_body"] == {
        "text": "text",
        "style": "friendly",
        "language": "en",
        "max_output_tokens": 256,
    }


# --- thai_qa_api -> POST /v3/store/nlp/question/answer/v3 -------------------- #
def test_qa_posts_json_to_thai_qa(captured):
    api("K").thai_qa_api(question="ใครเป็นนายก", document="บริบท")
    assert captured["method"] == "POST"
    assert captured["url"] == "https://api.iapp.co.th/v3/store/nlp/question/answer/v3"
    assert captured["headers"]["Content-Type"] == "application/json"
    assert json.loads(captured["data"]) == {"question": "ใครเป็นนายก", "document": "บริบท"}


# --- thai_qgen_api -> GET /v3/store/nlp/question/generation?text= ----------- #
def test_qgen_uses_get_with_query_param(captured):
    # Question generation is a GET endpoint: the text rides the query string
    # (https, percent-encoded) and the apikey is sent via header, so neither the
    # key nor raw Thai leaks into the URL.
    api("SECRET").thai_qgen_api("ประเทศไทย & test")
    url = captured["url"]
    assert captured["method"] == "GET"
    assert url.startswith("https://api.iapp.co.th/v3/store/nlp/question/generation?text=")
    assert "http://" not in url
    assert "ประเทศไทย" not in url                # Thai is percent-encoded, not raw
    assert "apikey" not in url and "SECRET" not in url
    assert captured["apikey"] == "SECRET"       # still delivered via header


# --- thai_thaitts_kaitom / thai_thaitts_cee -> POST /v3/store/audio/tts ----- #
def test_tts_kaitom_posts_json_to_v3_tts(captured, tmp_path):
    out = tmp_path / "kaitom.wav"
    api("K").thai_thaitts_kaitom("สวัสดีครับ", output_path=str(out))
    assert captured["method"] == "POST"
    assert captured["url"] == "https://api.iapp.co.th/v3/store/audio/tts"
    assert captured["json_body"] == {"text": "สวัสดีครับ"}
    assert captured["headers"]["Content-Type"] == "application/json"
    # The raw response bytes are written to the requested output path.
    assert out.read_bytes() == b'{"ok": false}'


def test_tts_cee_shares_the_v3_tts_endpoint(captured, tmp_path):
    out = tmp_path / "cee.wav"
    api("K").thai_thaitts_cee("ทดสอบ", output_path=str(out))
    assert captured["method"] == "GET"
    assert captured["url"] == "https://api.iapp.co.th/v3/store/speech/text-to-speech/cee"
    assert captured["params"] == {"text": "ทดสอบ"}
    assert out.read_bytes() == b'{"ok": false}'


# --- thai_asr_api -> POST /v3/store/speech/speech-to-text/base (multipart) -- #
def test_asr_posts_multipart_to_v3_base(captured, tmp_path):
    f = tmp_path / "speech.mp3"
    f.write_bytes(b"\x00\x01")
    api("K").thai_asr_api(str(f))
    assert captured["method"] == "POST"
    assert captured["url"] == "https://api.iapp.co.th/v3/store/speech/speech-to-text/base"
    field, filetuple = captured["files"][0]
    assert field == "file"               # audio is uploaded under the "file" field
    assert filetuple[2] == "audio/mpga"


def test_asr_forwards_extra_form_fields(captured, tmp_path):
    f = tmp_path / "speech.mp3"
    f.write_bytes(b"\x00")
    api("K").thai_asr_api(str(f), data_payload={"chunk_size": "7", "use_asr_pro": "0"})
    assert captured["data"] == {"chunk_size": "7", "use_asr_pro": "0"}


# =========================================================================== #
# Smart-city OCR endpoint contract tests (water meter / license plate).
# Each method has a file (multipart) and a base64 (JSON) variant.
# =========================================================================== #


def test_water_meter_binary_uploads_file_multipart(captured, tmp_path):
    f = tmp_path / "meter.jpg"
    f.write_bytes(b"\xff\xd8\xff")
    api("K").water_meter_binary(str(f))
    assert captured["method"] == "POST"
    assert captured["url"] == "https://api.iapp.co.th/v3/store/smart-city/power-meter-and-water-meter/file"
    field, filetuple = captured["files"][0]
    assert field == "file"
    assert filetuple[0] == "meter.jpg"
    assert filetuple[2] == "image/jpg"


def test_water_meter_base64_sends_json_image(captured):
    api("K").water_meter_base64(data_payload="BASE64DATA")
    assert captured["method"] == "POST"
    assert captured["url"] == "https://api.iapp.co.th/v3/store/smart-city/power-meter-and-water-meter/base64"
    assert captured["headers"].get("Content-Type") == "application/json"
    assert json.loads(captured["data"]) == {"image": "BASE64DATA"}


def test_license_plate_ocr_uploads_file_multipart(captured, tmp_path):
    f = tmp_path / "car.jpg"
    f.write_bytes(b"\xff\xd8\xff")
    api("K").license_plate_ocr(str(f))
    assert captured["method"] == "POST"
    assert captured["url"] == "https://api.iapp.co.th/v3/store/smart-city/license-plate-ocr"
    field, filetuple = captured["files"][0]
    assert field == "file"
    assert filetuple[0] == "car.jpg"     # basename used as filename
    assert filetuple[2] == "image/jpg"


def test_license_plate_base64_sends_json_image(captured):
    api("K").license_plate_base64(data_payload="BASE64DATA")
    assert captured["method"] == "POST"
    assert captured["url"] == "https://api.iapp.co.th/v3/store/smart-city/license-plate-ocr/base64"
    assert captured["headers"].get("Content-Type") == "application/json"
    assert json.loads(captured["data"]) == {"image": "BASE64DATA"}


# =========================================================================== #
# Contract tests for methods that previously had no coverage: OCR document
# family, NLP extras, holiday data, LLM chat, image/video generation, voice.
# Each locks the endpoint + HTTP method + body/field shape against the API.
# =========================================================================== #


# --- OCR doc family (return_ocr flag): POST multipart, field "file" --------- #
@pytest.mark.parametrize(
    "method_name, expected_url",
    [
        ("receipt_ocr", "https://api.iapp.co.th/v3/store/ocr/receipt"),
        ("credit_card_statement_ocr", "https://api.iapp.co.th/v3/store/ocr/creditcard-statement"),
        ("tax_deduction_certificate_ocr", "https://api.iapp.co.th/v3/store/ocr/tax-deduction-certificate"),
        ("civil_registration_ocr", "https://api.iapp.co.th/v3/store/ocr/civil-registeration-certificate"),
    ],
)
def test_return_ocr_doc_family_endpoint_and_file_field(captured, tmp_path, method_name, expected_url):
    f = tmp_path / "doc.pdf"
    f.write_bytes(b"%PDF-1.4")
    getattr(api("K"), method_name)(str(f))
    assert captured["method"] == "POST"
    assert captured["url"] == expected_url
    field, filetuple = captured["files"][0]
    assert field == "file"
    assert filetuple[0] == "doc.pdf"   # basename used as the multipart filename
    assert captured["data"] == {}       # return_ocr defaults off -> no flag sent


def test_return_ocr_flag_sent_only_when_true(captured, tmp_path):
    f = tmp_path / "r.jpg"
    f.write_bytes(b"x")
    api("K").receipt_ocr(str(f), return_ocr=True)
    assert captured["data"] == {"return_ocr": "true"}


# --- resume / job description: POST multipart "file", no extra form data ----- #
@pytest.mark.parametrize(
    "method_name, expected_url",
    [
        ("resume_ocr", "https://api.iapp.co.th/v3/store/ocr/curriculum-vitae"),
        ("job_description_ocr", "https://api.iapp.co.th/v3/store/ocr/job-description"),
    ],
)
def test_resume_and_jd_ocr_endpoint_and_file_field(captured, tmp_path, method_name, expected_url):
    f = tmp_path / "cv.pdf"
    f.write_bytes(b"%PDF")
    getattr(api("K"), method_name)(str(f))
    assert captured["method"] == "POST"
    assert captured["url"] == expected_url
    assert captured["files"][0][0] == "file"
    assert captured["files"][0][1][0] == "cv.pdf"


# --- sentiment / toxicity: POST with `text` carried as a query param -------- #
@pytest.mark.parametrize(
    "method_name, expected_url",
    [
        ("sentiment_analysis", "https://api.iapp.co.th/v3/store/nlp/sentiment-analysis"),
        ("toxicity_classification", "https://api.iapp.co.th/v3/store/nlp/toxicity-classification"),
    ],
)
def test_nlp_classification_sends_text_as_param(captured, method_name, expected_url):
    getattr(api("K"), method_name)("ข้อความทดสอบ")
    assert captured["method"] == "POST"
    assert captured["url"] == expected_url
    assert captured["params"] == {"text": "ข้อความทดสอบ"}
    assert captured["files"] is None


# --- thai_holidays: GET; year goes in the path, type defaults to "public" --- #
def test_thai_holidays_by_year_uses_path_and_default_type(captured):
    api("K").thai_holidays(year=2026)
    assert captured["method"] == "GET"
    assert captured["url"] == "https://api.iapp.co.th/v3/store/data/thai-holiday/year/2026"
    assert captured["params"] == {"holiday_type": "public"}


def test_thai_holidays_by_range_switches_endpoint(captured):
    api("K").thai_holidays(start_date="2026-01-01", end_date="2026-12-31")
    assert captured["url"] == "https://api.iapp.co.th/v3/store/data/thai-holiday/range"
    assert captured["params"]["start_date"] == "2026-01-01"
    assert captured["params"]["end_date"] == "2026-12-31"


# --- llm_chat: POST JSON to the per-model chat-completions endpoint ---------- #
def test_llm_chat_default_model_endpoint_and_messages(captured):
    api("K").llm_chat("สวัสดี")
    assert captured["method"] == "POST"
    assert captured["url"] == "https://api.iapp.co.th/v3/llm/chinda-thaillm-4b/chat/completions"
    assert captured["headers"]["Content-Type"] == "application/json"
    body = json.loads(captured["data"])
    assert body["model"] == "chinda-qwen3-4b"
    assert body["messages"] == [{"role": "user", "content": "สวัสดี"}]
    assert body["stream"] is False


def test_llm_chat_prepends_system_prompt(captured):
    api("K").llm_chat("hi", system_prompt="be brief")
    body = json.loads(captured["data"])
    assert body["messages"][0] == {"role": "system", "content": "be brief"}
    assert body["messages"][1] == {"role": "user", "content": "hi"}


# --- thanoy_legal_qa: its own endpoint, NOT an alias of llm_chat ------------ #
def test_thanoy_legal_qa_posts_query_to_store_endpoint(captured):
    api("K").thanoy_legal_qa("ถามกฎหมาย")
    assert captured["method"] == "POST"
    assert captured["url"] == "https://api.iapp.co.th/v3/store/llm/thanoy-legal-ai"
    assert json.loads(captured["data"]) == {"query": "ถามกฎหมาย"}


# --- image_generation: POST JSON to the Google nano-banana endpoint --------- #
def test_image_generation_default_model_endpoint(captured):
    api("K").image_generation("a cat")
    assert captured["method"] == "POST"
    assert captured["url"] == "https://api.iapp.co.th/v3/image/generation/google/nanobanana/generate"
    body = json.loads(captured["data"])
    assert body["contents"][0]["parts"][0]["text"] == "a cat"


def test_image_generation_pro_model_uses_nanobananapro_slug(captured):
    api("K").image_generation("x", model="nanobanana-pro")
    assert captured["url"] == "https://api.iapp.co.th/v3/image/generation/google/nanobananapro/generate"


# --- seedance video: async submit (POST JSON) + status (GET by id) ---------- #
def test_seedance_submit_posts_json_with_mapped_model(captured):
    api("K").seedance_video_submit("a dog running")
    assert captured["method"] == "POST"
    assert captured["url"] == "https://api.iapp.co.th/v3/store/video/seedance/tasks"
    body = json.loads(captured["data"])
    assert body["model"] == "dreamina-seedance-2-0-fast-260128"  # default "seedance-fast"
    assert body["content"] == [{"type": "text", "text": "a dog running"}]


def test_seedance_status_is_get_with_task_id_in_path(captured):
    api("K").seedance_video_status("task-123")
    assert captured["method"] == "GET"
    assert captured["url"] == "https://api.iapp.co.th/v3/store/video/seedance/tasks/task-123"


# --- voice_clone_tts: POST multipart "ref_audio" + text/ref_text/speed ------ #
def test_voice_clone_tts_uploads_ref_audio_and_fields(captured, tmp_path):
    ref = tmp_path / "ref.wav"
    ref.write_bytes(b"\x00\x01")
    api("K").voice_clone_tts("พูดตามนี้", str(ref), "reference text", speed=1.5)
    assert captured["method"] == "POST"
    assert captured["url"] == "https://api.iapp.co.th/v3/store/audio/tts/clone"
    assert captured["files"][0][0] == "ref_audio"
    assert captured["files"][0][1][0] == "ref.wav"
    assert captured["data"] == {"text": "พูดตามนี้", "ref_text": "reference text", "speed": "1.5"}


# --- ai_audio_detection: POST multipart under the "audio" field ------------- #
def test_ai_audio_detection_uploads_under_audio_field(captured, tmp_path):
    a = tmp_path / "clip.wav"
    a.write_bytes(b"\x00")
    api("K").ai_audio_detection(str(a))
    assert captured["method"] == "POST"
    assert captured["url"] == "https://api.iapp.co.th/v3/store/audio/tts/detect"
    assert captured["files"][0][0] == "audio"
    assert captured["files"][0][1][0] == "clip.wav"
