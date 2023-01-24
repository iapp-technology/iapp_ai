# iApp AI API pip package


[![Pip](https://img.shields.io/pypi/v/iapp_ai.svg)](https://pypi.python.org/pypi/iapp_ai)

## iApp AI API pip package

* Free software: MIT license
* Documentation: https://docs.iapp.co.th
* Request API Key: https://ai.iapp.co.th
* Full Google Colab Example: https://colab.research.google.com/drive/1CH3NlohPMn1BpepXvJS9sgG-_isrYHPC?usp=sharing


Features
--------

* iApp Image Recognition Service
  1. Thai National ID Card OCR (Support Card) [NEW]
  1. Thai National ID Card OCR (Support Photocopied)[NEW]
  1. Passport OCR [NEW]
  1. Thai Vehicle License Plate
  1. Book Bank OCR
  1. Face Verification (Comparison)
  1. Face Recognition
  1. Face Detection
  1. Face Passive Liveness Detection
  1. Thai Document OCR [NEW]
  1. Thai Driver License Card OCR [NEW]
  1. Power Meter OCR
  1. Water Meter OCR
  1. Image Background Remover

* iApp Thai NLP Service
  1. Thai Auto Question Answering
  1. Question Generator
  1. Thai-English Machine Translation
  1. Thai Text Parser
  1. Thai Text Summarization

* iApp Voice and Speech Service
  1. Thai Automatic Speech Recognition (ASR) [NEW]
  2. Thai Text to Speech (TTS)
  3. Music Source Seperator
  4. Noise Subtraction

Running Unit Test
-------
Slient Test
``$ pytest``

Verbose Test
``$ pytest -s``

Filter Test
``pytest -rP tests/test_thai_asr.py``

Filter Test with specific method
``pytest -rP tests/test_idcard.py::test_idcard_front``

Credits
-------

* [Cookiecutter](https://github.com/audreyr/cookiecutter)
* [`audreyr/cookiecutter-pypackage`](https://github.com/audreyr/cookiecutter-pypackage)
