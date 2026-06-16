# Canonical API Endpoint Table (single source of truth)

**Status:** DRAFT — awaiting SA sign-off (meeting Action #4)
**Last updated:** 2026-06-16 · seeded from PR #43 live-verification

## Source-of-truth rule

> The **live iApp API (verified by a real `200` response)** is the single source of truth.
> The docs at iapp.co.th/docs are a guide only — PR #43 found **3 docs pages are wrong**
> (return 404/405 vs the live API, e.g. question-generation is GET not POST).
>
> A method's endpoint is only "DONE" when SDK and MCP use the **same** path/method/body
> **and** a live `200` has been observed. CI green ≠ verified (offline tests only assert the
> chosen contract).

Legend: ✅ live-verified (200) · ⚠️ not yet live-verified · ❌ SDK/MCP mismatch to resolve

## Thai NLP

| Method | Path | HTTP | Body | SDK (develop) | MCP (develop) | State |
|---|---|---|---|---|---|---|
| translate | `/v3/store/nlp/multilingual-translation` | POST | JSON `{text, source_lang, target_lang, max_length?}` | ✅ 200 | `/v1/text/translate` (form) ✅ 200 | ✅ both work (aliases) — pick one for consistency |
| summarize | `/v3/store/nlp/thai-text-summary` | POST | JSON `{text, style?, language?, max_output_tokens?}` | ✅ 200 | ✅ 200 | ✅ aligned |
| question generation | `/v3/store/nlp/question/generation` | **GET** | query `?text=` | ✅ 200 (live: GET, docs wrong) | ✅ GET | ✅ aligned |
| question answering | `/thai-qa` _or_ `/v3/store/nlp/question/answer/v3` | POST | JSON `{question, document}` | ✅ 200 | ✅ 200 | ✅ both return identical `{"answer"}` — #37 safe, pick canonical |
| sentiment | `/v3/store/nlp/sentiment-analysis` | POST | query `?text=` | ✅ 200 (#42) | ✅ 200 | ✅ |
| toxicity | `/v3/store/nlp/toxicity-classification` | POST | query `?text=` | ✅ 200 (#42) | ✅ 200 | ✅ |
| thanoy legal QA | `/thanoy` _or_ `/v3/store/llm/thanoy-legal-ai` | POST | JSON `{query}` | ✅ 200 (#42) | ✅ 200 | ✅ both work (aliases) |
| thai-holiday | `/v3/store/data/thai-holiday` | GET | query | ✅ 200 (#42) | ✅ 200 | ✅ |

> **Live-verified 2026-06-16** (real `200`). The contested `qa`/`translate`/`thanoy` paths are
> **aliases** — both members of each pair return an identical response, so PR #37 is **not broken**.
> Remaining decision is cosmetic: standardize SDK+MCP on ONE name per method.

## Speech

| Method | Path | HTTP | Body | SDK | MCP | State |
|---|---|---|---|---|---|---|
| TTS (kaitom/cee unified) | `/v3/store/audio/tts` | POST | JSON `{text, ...}` | ✅ (live) | n/a | ⚠️ add to MCP if needed |
| ASR (base) | `/v3/store/speech/speech-to-text/base` | POST | multipart `file` | ✅ (live) | ⚠️ confirm | ⚠️ verify MCP |

## Smart City

| Method | Path | HTTP | Body | SDK | MCP | State |
|---|---|---|---|---|---|---|
| power meter | `/v3/store/smart-city/power-meter-and-water-meter/base64` | POST | JSON base64 | ✅ (live) | `/...power-meter-and-water-meter/file` (multipart) | ⚠️ two variants — confirm both |
| water meter (file) | `/meter-number-ocr/file` | POST | multipart | ✅ (live) | unified meter endpoint | ⚠️ reconcile |
| license plate (file) | `/license-plate-recognition/file` | POST | multipart | ✅ (live) | `/v3/store/smart-city/license-plate-ocr` | ⚠️ reconcile |

## OCR / Document

| Method | Path | HTTP | SDK | MCP | State |
|---|---|---|---|---|---|
| document (text) | `/v3/store/ocr/document/ocr` | POST | ✅ (B-6) | ✅ (#37 leaves unchanged) | ✅ aligned |
| document (layout) | `/v3/store/ocr/document/layout` | POST | ✅ | ✅ | ✅ |
| document (docx) | `/v3/store/ocr/document/docx` | POST | ✅ | ✅ | ✅ |
| receipt / creditcard / tax / civil-reg | `/v3/store/ocr/<type>` | POST | ✅ (#42) | ✅ (#37) | ⚠️ live-verify |

## eKYC (PR #39 — aligned to docs, NOT live-verified)

All face/ekyc methods proposed to move to `/v3/store/ekyc/...`. ⚠️ **Must be live-verified
before merge** — docs proved unreliable, so the old `/face_compare`, `/passive-face-liveness-detection`
paths may still be the ones that return 200.

## Open items (for the PRs in flight)

- **#37 (MCP):** ✅ **cleared by live test** — its `thai_qa` path AND the SDK's `/thai-qa` both return
  200 with identical schema (aliases). #37 is safe to merge. Optional: standardize SDK+MCP on one name
  for `qa`/`translate`/`thanoy` (cosmetic).
- **#39 (eKYC):** live-verify every new `/v3/store/ekyc/...` path returns 200 before merge. Note SDK
  id-card front is `/thai-national-id-card/v3/front` (v3) while MCP #37 uses `v3.5` for both sides — reconcile.
- **#42 (17 new methods):** live-verify the 17 endpoints; they are docs-derived only.

## Sign-off

- [ ] SA reviewed & approved this table — name / date: ____________________
