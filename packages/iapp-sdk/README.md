# iapp-ai — iApp AI Marketplace Python SDK

Synchronous Python SDK for the [iApp AI Marketplace](https://iapp.co.th) APIs
(Thai OCR, eKYC, face, NLP, speech, and more). Each method is a thin wrapper that
returns the raw [`requests.Response`](https://requests.readthedocs.io/), so you
keep full control over status codes and parsing. It also includes
[offline Thai NLP](#offline-thai-nlp), `iapp_ai.nlp`, which needs no API key.

> Looking to connect an AI assistant (Claude, etc.) to iApp instead of calling
> from code? Use the MCP server: [`iapp-mcp`](../iapp-mcp).

## Install

```bash
pip install iapp-ai
pip install "iapp-ai[nlp]"   # also the offline Thai word tokenizer
```

Requires Python 3.10 or later; on Python 3.8 and 3.9, pip installs iapp-ai 1.4.0.

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

## Offline Thai NLP

`iapp_ai.nlp` splits Thai text into words and cleans up and converts Thai text
on your own machine, with no API key, no network calls and no iApp credits.

```bash
pip install "iapp-ai[nlp]"
```

```python
from iapp_ai.nlp import normalize, word_tokenize

word_tokenize("แม่น้ำเจ้าพระยาไหลผ่านกรุงเทพ")
# ['แม่น้ำ', 'เจ้าพระยา', 'ไหล', 'ผ่าน', 'กรุงเทพ']
word_tokenize(normalize("วันนี้ฝนตกหนักมาาาก"))   # fixes the repeated vowel first
# ['วัน', 'นี้', 'ฝน', 'ตก', 'หนัก', 'มาก']
```

- The word tokenizers (`word_tokenize`, `tokenize`, `word_tokenize_nbest`,
  `Tokenizer` and the `iapp-tokenize` command) use the
  OpenThai2.0-LATTE-WordSeg-Lite model, which needs NumPy and ONNX Runtime from
  the `nlp` extra. Without it they raise an `ImportError` that says to install it.
- `normalize`, the Thai number and date helpers in `iapp_ai.nlp.util`, the word
  lists in `iapp_ai.nlp.corpus` and the province tagger in `iapp_ai.nlp.tag`
  work with plain `pip install iapp-ai`.
- The NLP methods of `api`, such as `sentiment_analysis`, run on iApp's servers
  and need an API key; `iapp_ai.nlp` does not.

Units, your own words, batches, several readings, dates and the command line
are in the [`iapp_ai.nlp` guide](https://github.com/iapp-technology/iapp_ai/blob/main/packages/iapp-sdk/docs/nlp.md).
`iapp_ai.nlp` replaces the `iapp-nlp` package: install `iapp-ai[nlp]` and
change `from iapp_nlp import ...` to `from iapp_ai.nlp import ...`.

## Backward compatibility

This SDK is a **drop-in** for previous `iapp_ai` releases — the import path,
class, method names/signatures, target endpoints, and raw `requests.Response`
return values are all unchanged. Existing code keeps working without edits.
It needs Python 3.10 or later; on Python 3.8 and 3.9, pip keeps installing
iapp-ai 1.4.0.

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

`iapp_ai.nlp` includes code under the Apache License 2.0 and model files under
CC BY-SA 4.0 (commercial use allowed), so the package as a whole is
`MIT AND Apache-2.0 AND CC-BY-SA-4.0 AND Unicode-DFS-2016`; see the
[license section of the `iapp_ai.nlp` guide](https://github.com/iapp-technology/iapp_ai/blob/main/packages/iapp-sdk/docs/nlp.md#license).
