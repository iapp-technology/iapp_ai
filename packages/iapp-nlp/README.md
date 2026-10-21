# iapp-nlp

Free Thai/English tokenizer from [iApp Technology](https://iapp.co.th).
No dependencies, no API key, runs offline.

```bash
pip install iapp-nlp
```

```python
from iapp_nlp import word_tokenize, tokenize

word_tokenize("ซื้อ iPhone15ราคา 30000 บาท!")
# ['ซื้อ', 'iPhone15', 'ราคา', '30000', 'บาท', '!']

tokenize("สวัสดี hello")
# [Token(text='สวัสดี', start=0, end=6), Token(text='hello', start=7, end=12)]
```

```bash
iapp-tokenize "Hello, world! สวัสดีครับ"
# Hello | , | world | ! | สวัสดีครับ
```

Thai text written without spaces is kept as one token for now; dictionary or
model-based Thai word segmentation is planned for a later release.