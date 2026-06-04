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

```bash
pip install iapp-mcp
```

Or from source:

```bash
git clone https://github.com/iapp-technology/iapp-mcp
cd iapp-mcp
pip install -e .
```

## Configuration

### Claude Desktop

Add to `claude_desktop_config.json`:

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

Or with [uv](https://docs.astral.sh/uv/) (no install needed):

```json
{
  "mcpServers": {
    "iapp-ai": {
      "command": "uvx",
      "args": ["iapp-mcp"],
      "env": {
        "IAPP_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

### Claude Code

```bash
claude mcp add iapp-ai -e IAPP_API_KEY=YOUR_API_KEY -- uvx iapp-mcp
```

## Usage Examples

Once connected, ask your AI assistant things like:

- *"อ่านข้อมูลจากบัตรประชาชนในไฟล์ idcard.jpg"* — Thai ID card OCR
- *"Transcribe meeting.mp3 (Thai audio) with speaker labels"* — speech-to-text
- *"แปลข้อความนี้เป็นภาษาญี่ปุ่น"* — translation
- *"OCR receipt.pdf and total up the line items"* — receipt OCR
- *"สร้างเสียงพูดจากข้อความนี้ด้วยเสียงไข่ต้ม"* — text-to-speech
- *"Generate a video of a cat surfing at sunset"* — Seedance video generation
- *"วันหยุดราชการไทยปีหน้ามีวันไหนบ้าง"* — Thai holiday data

## Notes

- Most tools consume iApp credits (IC) per call — costs are documented in each tool description.
- File-based tools accept **local file paths**; generated audio/images are saved to the path you specify.
- Large base64 blobs in API responses (e.g. cropped face images) are truncated in tool output to keep context small.

## Support

- Documentation: [iapp.co.th/docs/intro](https://iapp.co.th/docs/intro)
- Email: support@iapp.co.th

## License

MIT — © iApp Technology Co., Ltd.
