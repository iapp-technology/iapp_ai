# iApp MCP Server

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

- Python 3.10+
- An iApp API key:
  1. Login / register at [iapp.co.th](https://iapp.co.th)
  2. Go to **API Keys** in the control panel
  3. Click **Create New API Key**, name it, and create
  4. Copy the key — it is only shown once!

## Installation

No installation needed if you use [uv](https://docs.astral.sh/uv/) — see the configuration below (`uvx` fetches and runs the server automatically).

To install manually:

```bash
pip install git+https://github.com/iapp-ai/iapp-ai.git
```

Or from source:

```bash
git clone https://github.com/iapp-ai/iapp-ai
cd iapp-ai
pip install -e .
```

## Configuration

Add the server to your MCP client's configuration file (with [uv](https://docs.astral.sh/uv/), no install needed):

```json
{
  "mcpServers": {
    "iapp-ai": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/iapp-ai/iapp-ai", "iapp-mcp"],
      "env": {
        "IAPP_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

Or if you installed with pip:

```json
{
  "mcpServers": {
    "iapp-ai": {
      "command": "iapp-mcp",
      "env": {
        "IAPP_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

The server runs over stdio, so any MCP client can launch it with the command
`uvx --from git+https://github.com/iapp-ai/iapp-ai iapp-mcp` and the
`IAPP_API_KEY` environment variable set.

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

## Support

- Documentation: [iapp.co.th/docs/intro](https://iapp.co.th/docs/intro)
- Email: support@iapp.co.th

## License

© iApp Technology Co., Ltd.
