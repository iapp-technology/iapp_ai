# iapp-ai — iApp AI Marketplace Python SDK

Synchronous Python SDK for the [iApp AI Marketplace](https://iapp.co.th) APIs
(Thai OCR, eKYC, face, NLP, speech, and more). Each method is a thin wrapper that
returns the raw [`requests.Response`](https://requests.readthedocs.io/), so you
keep full control over status codes and parsing.

> Looking to connect an AI assistant (Claude, etc.) to iApp instead of calling
> from code? Use the MCP server: [`iapp-mcp`](../iapp-mcp).

## Install

```bash
pip install iapp-ai
```

### Pre-release builds (TestPyPI)

Test builds are published to [TestPyPI](https://test.pypi.org/) as `test-iapp-ai`.
You **must** add `--extra-index-url` so dependencies (`requests`, etc.) resolve
from real PyPI — TestPyPI only hosts our package, not its dependencies:

```bash
pip install -i https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            test-iapp-ai
```

> Using `-i` alone (`pip install -i https://test.pypi.org/simple/ test-iapp-ai`)
> fails — it makes TestPyPI the *only* index, so pip can't find dependencies like
> `charset_normalizer`. `--extra-index-url` adds PyPI back for those.

## Usage

```python
from iapp_ai import api

client = api("YOUR_API_KEY")

# OCR a Thai national ID card (front)
resp = client.idcard_front("id-card-front.jpg")
print(resp.status_code)
print(resp.json())

# Translate text
resp = client.eng_thai_translate("Hello, world")
print(resp.json())

# Speech-to-text
resp = client.thai_asr_api("audio.mp3")
print(resp.json())
```

Get an API key at [iapp.co.th](https://iapp.co.th) → **API Keys** → **Create New API Key**.

## Backward compatibility

This SDK is a **drop-in** for previous `iapp_ai` releases — the import path,
class, method names/signatures, target endpoints, and raw `requests.Response`
return values are all unchanged. Existing code keeps working without edits.

Internally the HTTP transport is now provided by the shared
[`iapp-core`](../iapp-core) package (installed automatically as a dependency).

## Available methods (selection)

`idcard_front`, `idcard_back`, `idcard_front_photocopied`, `passport_ocr`,
`book_bank_api`, `driver_card_ocr`, `document_ocr_plaintext`,
`document_ocr_json_layout`, `document_ocr_docx`, `license_plate_ocr`,
`water_meter_binary` / `water_meter_base64`, `face_verification`, `face_ver2`,
`face_detect_single` / `face_detect_multi`, `face_recog_*` (add/remove/check/
export/import/single/multi/facecrop), `face_liveness` / `info_face_liveness`,
`img_bg_removal_file` / `img_bg_removal_base64`, `thai_qa_api`, `thai_qgen_api`,
`thai_text_summarization`, `eng_thai_translate`, `thai_asr_api`,
`thai_thaitts_kaitom` / `thai_thaitts_cee`.

> Note: `thai_thaitts_kaitom`, `thai_thaitts_cee` and `img_bg_removal_file`
> write their output into a relative `media/` directory (legacy behavior; run
> from a directory that has a `media/` folder).

## License

MIT © iApp Technology Co., Ltd.
