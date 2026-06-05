# iApp AI MCP Server

[MCP (Model Context Protocol)](https://modelcontextprotocol.io) server for the
[iApp AI Marketplace](https://iapp.co.th) — connect AI assistants like Claude to
30+ Thai-focused AI APIs: OCR, eKYC, Thai NLP, LLMs, speech, and image/video generation.

## Features

| Category | Tools |
|---|---|
| **eKYC** | Thai ID card OCR (front/back/photocopy), passport OCR, driver license OCR, bank book OCR, face verification, face detection, face liveness, face+ID KYC, face recognition (1:N) |
| **Document OCR** | General Thai document OCR (text/layout/DOCX), receipt, credit card statement, tax deduction certificate (50 ทวิ), civil registration certificate, resume/CV extraction + AI evaluation, job description extraction |
| **Thai NLP** | Multilingual translation (28 languages), summarization, sentiment analysis, toxicity classification, Thai QA, question generation |
| **LLM** | Chinda Thai LLM 4B (free), DeepSeek-V3.2, DeepSeek V4 (Flash/Pro), Thanoy Thai Legal AI |
| **Speech** | Speech-to-text (Thai/English/Chinese, base/pro with diarization), Thai text-to-speech (4 voices), voice cloning, AI audio watermark detection |
| **Image/Video** | Image generation (Google Nano Banana / Pro), background removal, Seedance 2.0 video generation (async submit + status) |
| **Smart City & Data** | Thai license plate recognition, power/water meter OCR, route optimization, Thai holiday data |

## Prerequisites

- An iApp API key:
  1. Login / register at [iapp.co.th](https://iapp.co.th)
  2. Go to **API Keys** in the control panel
  3. Click **Create New API Key**, name it, and create
  4. Copy the key — it is only shown once!

## Installation

The server is published as [`iapp-ai` on PyPI](https://pypi.org/project/iapp-ai/) and
[`iapp-ai` on npm](https://www.npmjs.com/package/iapp-ai) — use whichever package
manager you prefer:

### Python (3.10+)

| Package manager | Run without installing | Install permanently |
|---|---|---|
| [uv](https://docs.astral.sh/uv/) | `uvx iapp-ai` | `uv tool install iapp-ai` |
| pip | — | `pip install iapp-ai` |

### Node.js (18+)

> The npm package is a thin launcher for the Python server, so
> [uv](https://docs.astral.sh/uv/getting-started/installation/) must be installed
> (one time): `curl -LsSf https://astral.sh/uv/install.sh | sh` or `brew install uv`

| Package manager | Run without installing | Install permanently |
|---|---|---|
| npm | `npx -y iapp-ai` | `npm install -g iapp-ai` |
| yarn | `yarn dlx iapp-ai` | `yarn global add iapp-ai` |
| pnpm | `pnpm dlx iapp-ai` | `pnpm add -g iapp-ai` |

Every "install permanently" option gives you the same `iapp-ai` command:

```bash
IAPP_API_KEY=YOUR_API_KEY iapp-ai
```

## Configuration

Add the server to your MCP client's configuration file. Pick the block matching how
you installed:

**PyPI + uv (recommended):**

```json
{
  "mcpServers": {
    "iapp-ai": {
      "command": "uvx",
      "args": ["iapp-ai"],
      "env": {
        "IAPP_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

**npm:**

```json
{
  "mcpServers": {
    "iapp-ai": {
      "command": "npx",
      "args": ["-y", "iapp-ai"],
      "env": {
        "IAPP_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

**Installed permanently (pip / uv tool / npm / yarn / pnpm):**

```json
{
  "mcpServers": {
    "iapp-ai": {
      "command": "iapp-ai",
      "env": {
        "IAPP_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

The server runs over stdio, so any MCP client (desktop apps, IDEs, custom apps using
the MCP SDK) can launch it with any of the commands above and the `IAPP_API_KEY`
environment variable set.

## Tools Reference

All 37 tools, what they do, and their key inputs. File inputs are **local file
paths**; generated files are saved to the `output_path` you specify.

### 🪪 eKYC

| Tool | What it does | Key inputs |
|---|---|---|
| `iapp_thai_id_card_ocr` | Read data from a Thai national ID card photo | `file_path`, `side` (front/back) |
| `iapp_thai_id_card_photocopy_ocr` | Read a photocopied ID card + detect signature | `file_path` |
| `iapp_passport_ocr` | Read MRZ + personal data from any passport | `file_path`, `segmentation` (for skewed photos) |
| `iapp_thai_driver_license_ocr` | Read a Thai driver license | `file_path` |
| `iapp_book_bank_ocr` | Read account name/number from a bank book page | `file_path` |
| `iapp_face_verification` | Check if two face photos are the same person (1:1) | `image1_path`, `image2_path`, `threshold` |
| `iapp_face_detection` | Find face(s) + bounding boxes in a photo | `file_path`, `mode` (single/multi) |
| `iapp_face_liveness` | Detect photo-of-photo / screen spoofing | `file_path` |
| `iapp_face_id_card_kyc` | Match a selfie against the face on an ID card | `id_card_path`, `selfie_path` |
| `iapp_face_recognition` | Enroll & search faces in a company database (1:N) | `action` (add/remove/check/recognize_single/recognize_multi), `company`, `file_path`, `name`, `password` |

### 🔍 Thai Document OCR

| Tool | What it does | Key inputs |
|---|---|---|
| `iapp_document_ocr` | OCR any Thai document | `file_path`, `mode`: `text` (raw text), `layout` (structure + bounding boxes), `docx` (convert to Word) |
| `iapp_receipt_ocr` | Extract line items & totals from Thai receipts | `file_path`, `return_ocr` |
| `iapp_credit_card_statement_ocr` | Extract transactions from card statements | `file_path`, `return_ocr` |
| `iapp_tax_deduction_certificate_ocr` | Read withholding tax certificates (50 ทวิ) | `file_path`, `return_ocr` |
| `iapp_civil_registration_ocr` | Read Thai civil registration certificates | `file_path`, `return_ocr` |
| `iapp_resume_ocr` | Extract structured data from a resume/CV + AI evaluation | `file_path` |
| `iapp_job_description_ocr` | Extract structured data from a job description | `file_path` |

### 🤖 Large Language Model

| Tool | What it does | Key inputs |
|---|---|---|
| `iapp_llm_chat` | Chat with LLMs hosted on iApp (OpenAI-compatible) | `prompt` (or full `messages`), `model`: `chinda-qwen3-4b` (Thai, free) / `deepseek-chat` / `deepseek-reasoner` / `deepseek-v4-flash` / `deepseek-v4-pro`, `system_prompt`, `max_tokens`, `temperature` |
| `iapp_thanoy_legal_qa` | Ask Thai legal questions (Thanoy Legal AI) | `query` |

### 🌐 Thai NLP

| Tool | What it does | Key inputs |
|---|---|---|
| `iapp_translate` | Translate between 28 languages (Thai-optimized) | `text`, `source_lang`, `target_lang` (e.g. th, en, ja, zh, ko, …) |
| `iapp_summarize` | Summarize Thai/English text | `text`, `style` (standard/clarify/friendly), `language` (th/en) |
| `iapp_sentiment_analysis` | Classify Thai text as positive/neutral/negative | `text` |
| `iapp_toxicity_classification` | Detect toxic Thai text | `text` |
| `iapp_thai_qa` | Answer a question from a given Thai document (extractive QA) | `question`, `document` |
| `iapp_question_generation` | Generate Q&A pairs from Thai text | `text` |

### 🎙️ Speech Technology

| Tool | What it does | Key inputs |
|---|---|---|
| `iapp_speech_to_text` | Transcribe audio with speaker diarization | `file_path`, `language` (th/en/zh), `quality` (base/pro) |
| `iapp_text_to_speech` | Synthesize Thai speech and save an audio file | `text`, `output_path`, `voice` (kaitom-v3/kaitom-v2/kaitom-v1/cee), `speed` |
| `iapp_voice_clone_tts` | Speak any text in a voice cloned from a sample | `text`, `ref_audio_path`, `ref_text`, `output_path` |
| `iapp_ai_audio_detection` | Check if audio was AI-generated | `audio_path` |

### 🖼️ Image & 🎬 Video Generation

| Tool | What it does | Key inputs |
|---|---|---|
| `iapp_image_generation` | Generate an image from text (Google Nano Banana) | `prompt`, `output_path`, `model` (nanobanana / nanobanana-pro) |
| `iapp_remove_background` | Remove the background from an image | `file_path`, `output_path` |
| `iapp_video_generation_submit` | Submit an async Seedance 2.0 video job | `prompt`, `model` (seedance/seedance-fast), `duration` (4–15 s), `ratio`, `resolution`, `generate_audio` |
| `iapp_video_generation_status` | Poll a video job and get the download URL | `task_id` |

### ♻️ Smart City AI & 📊 Thai Data

| Tool | What it does | Key inputs |
|---|---|---|
| `iapp_license_plate_ocr` | Read Thai vehicle license plates from photos | `file_path` |
| `iapp_meter_ocr` | Read power/water meter values from photos | `file_path` |
| `iapp_route_optimization` | Optimize delivery routes for multiple drivers (≤100 stops) | `origin_address` + coordinates, `stops`, `driver_count` |
| `iapp_thai_holidays` | Look up Thai public holidays | `year`, or `start_date`+`end_date`, or nothing (around today) |

## Usage Examples

Once connected, ask your AI assistant things like:

### 1. Electronic Know Your Customer (eKYC)

- *"อ่านข้อมูลจากบัตรประชาชนในไฟล์ idcard.jpg"* — Thai National ID Card OCR (`iapp_thai_id_card_ocr`, front/back)
- *"อ่านสำเนาบัตรประชาชนที่มีลายเซ็นในไฟล์ copy.png"* — Photocopied ID Card With Signature Detection (`iapp_thai_id_card_photocopy_ocr`)
- *"Extract the MRZ data from passport.jpg"* — Passport OCR (`iapp_passport_ocr`)
- *"อ่านข้อมูลใบขับขี่จาก license.png"* — Thai Driver License OCR (`iapp_thai_driver_license_ocr`)
- *"อ่านเลขบัญชีจากหน้าสมุดบัญชี bookbank.png"* — Thai Bank Book OCR (`iapp_book_bank_ocr`)
- *"เช็คว่ารูป selfie.jpg กับ idcard.jpg เป็นคนเดียวกันไหม"* — Face Verification (`iapp_face_verification`)
- *"หาใบหน้าทั้งหมดในรูป group.jpg"* — Face Detection (`iapp_face_detection`, single/multi)
- *"ตรวจว่ารูป face.jpg เป็นภาพถ่ายคนจริงหรือภาพปลอม"* — Face Passive Liveness / Spoofing Check (`iapp_face_liveness`)
- *"ทำ KYC: เทียบหน้าใน selfie.jpg กับรูปบนบัตรประชาชน idcard.jpg"* — Face and ID Card Verification for KYC (`iapp_face_id_card_kyc`)
- *"ลงทะเบียนใบหน้าพนักงานใหม่ แล้วลองค้นหาว่าใบหน้าในรูปนี้คือใคร"* — Face Recognition 1:N (`iapp_face_recognition`: add / recognize / check / remove)

### 2. Large Language Model

- *"ถาม Chinda Thai LLM ว่า ส้มตำมีกี่แคลอรี่"* — Chinda Thai LLM 4B, free (`iapp_llm_chat`, model=chinda-qwen3-4b)
- *"ใช้ DeepSeek V4 Flash ช่วยจัดหมวดหมู่ข้อความลูกค้าพวกนี้"* — DeepSeek V4 Flash/Pro (`iapp_llm_chat`, model=deepseek-v4-flash / deepseek-v4-pro)
- *"ใช้ DeepSeek reasoner วิเคราะห์โจทย์คณิตข้อนี้แบบละเอียด"* — DeepSeek-V3.2 thinking/non-thinking (`iapp_llm_chat`, model=deepseek-reasoner / deepseek-chat)
- *"ถามทนอย: สัญญาเช่าบ้านไม่มีลายเซ็นพยานมีผลไหม"* — Thanoy Thai Legal AI Chatbot (`iapp_thanoy_legal_qa`)

### 3. Image Generation

- *"สร้างรูปแมวใส่ชุดไทยนั่งริมเจ้าพระยา เซฟเป็น cat.png"* — Google Nano Banana Image Generation (`iapp_image_generation`, nanobanana / nanobanana-pro)
- *"ลบพื้นหลังออกจากรูปสินค้า product.jpg"* — Background Removal (`iapp_remove_background`)

### 4. Thai Document OCR

- *"OCR เอกสาร contract.pdf เอาข้อความทั้งหมด"* — General Thai Document OCR, raw text (`iapp_document_ocr`, mode=text)
- *"วิเคราะห์โครงสร้างเอกสาร report.jpg เอา bounding box ด้วย"* — Document Structure Analysis + OCR (`iapp_document_ocr`, mode=layout)
- *"แปลงเอกสารสแกนนี้เป็นไฟล์ Word"* — OCR to DOCX (`iapp_document_ocr`, mode=docx)
- *"สกัดข้อมูลจาก resume.pdf แล้วประเมินความเหมาะสมกับตำแหน่ง"* — AI Resume / CV Extraction + Evaluation (`iapp_resume_ocr`)
- *"อ่านรายการใช้จ่ายจาก statement บัตรเครดิต statement.jpg"* — Thai Credit Card Statement OCR (`iapp_credit_card_statement_ocr`)
- *"สกัดข้อมูลตำแหน่งงานจากไฟล์ jd.pdf"* — Job Description OCR + Extraction (`iapp_job_description_ocr`)
- *"อ่านข้อมูลทะเบียนบ้านจาก house_reg.jpg"* — Thai Civil Registration Certificate OCR (`iapp_civil_registration_ocr`)
- *"OCR ใบเสร็จ receipt.jpg แล้วรวมยอดให้หน่อย"* — Thai Receipt OCR (`iapp_receipt_ocr`)
- *"อ่านหนังสือรับรองหักภาษี ณ ที่จ่าย (50 ทวิ) ไฟล์นี้"* — Thai Tax Deduction Certificate OCR (`iapp_tax_deduction_certificate_ocr`)

### 5. Video Generation

- *"Generate a 5-second video of a cat surfing at sunset"* — Seedance 2.0 Video Generation (`iapp_video_generation_submit` → `iapp_video_generation_status`)

### 6. Speech Technology

- *"ถอดเสียงไฟล์ประชุม meeting.wav พร้อมระบุว่าใครพูด"* — Thai Speech-to-Text Base/PRO with diarization (`iapp_speech_to_text`, language=th)
- *"Transcribe interview.mp3 (English audio)"* — English Speech-to-Text Base/PRO (`iapp_speech_to_text`, language=en)
- *"ถอดเสียงไฟล์เสียงภาษาจีนนี้"* — Chinese Speech-to-Text Base/PRO (`iapp_speech_to_text`, language=zh)
- *"อ่านข้อความนี้เป็นเสียงพูดด้วยเสียงไข่ต้ม เซฟเป็น speech.wav"* — Thai Text-to-Speech V1/V2/V3, Kaitom & Cee voices (`iapp_text_to_speech`)
- *"โคลนเสียงจาก ref.wav แล้วให้พูดประโยคนี้"* — Voice Cloning TTS (`iapp_voice_clone_tts`)
- *"เช็คว่าไฟล์เสียง audio.wav เป็นเสียง AI สร้างหรือเสียงคนจริง"* — AI Audio Detection (`iapp_ai_audio_detection`)

### 7. Smart City AI

- *"จัดเส้นทางส่งของ 20 จุดนี้ให้คนขับ 3 คน เริ่มจากคลังสินค้า"* — Automatic Route Optimization (`iapp_route_optimization`)
- *"อ่านป้ายทะเบียนรถจากภาพกล้องวงจรปิด cctv.jpg"* — Thai Vehicle License Plate OCR (`iapp_license_plate_ocr`)
- *"อ่านเลขมิเตอร์น้ำ/ไฟจากรูป meter.jpg"* — Power & Water Meter OCR (`iapp_meter_ocr`)

### 8. Thai Natural Language Processing

- *"สรุปบทความยาว ๆ นี้ให้เหลือย่อหน้าเดียว"* — Text Summarization (`iapp_summarize`)
- *"จากเอกสารนี้ ช่วยตอบคำถาม: โครงการเริ่มเมื่อไหร่"* — Thai Auto Question Answering / ThaiQA (`iapp_thai_qa`)
- *"สร้างคำถาม-คำตอบจากเนื้อหาบทเรียนนี้ไว้ทำแบบทดสอบ"* — Thai Question Generator (`iapp_question_generation`)
- *"แปลข้อความนี้เป็นภาษาญี่ปุ่น"* — Multilingual Translation, 28 languages (`iapp_translate`)
- *"วิเคราะห์ว่ารีวิวลูกค้าพวกนี้เป็นบวกหรือลบ"* — Thai Sentiment Analysis (`iapp_sentiment_analysis`)
- *"ตรวจว่าคอมเมนต์พวกนี้มีข้อความ toxic ไหม"* — Thai Text Toxicity Classification (`iapp_toxicity_classification`)

### 9. Thai Data API

- *"วันหยุดราชการไทยปีหน้ามีวันไหนบ้าง"* — Thai Holiday Data API (`iapp_thai_holidays`)

## Notes

- Most tools consume iApp credits (IC) per call — costs are documented in each tool description.
- File-based tools accept **local file paths**; generated audio/images are saved to the path you specify.
- Large base64 blobs in API responses (e.g. cropped face images) are truncated in tool output to keep context small.
- Seedance video generation requires a paid iApp account (any IC package purchase unlocks it).

## Support

- Documentation: [iapp.co.th/docs/intro](https://iapp.co.th/docs/intro)
- Email: support@iapp.co.th

## License

© iApp Technology Co., Ltd.
