# iapp-nlp

Free Thai word tokenizer from [iApp Technology](https://iapp.co.th).
No API key, runs offline, and the Thai dictionary is included.

```bash
pip install iapp-nlp
```

```python
from iapp_nlp import word_tokenize, tokenize

word_tokenize("นายกรัฐมนตรีเดินทางไปเชียงใหม่เมื่อวานนี้")
# ['นายกรัฐมนตรี', 'เดินทาง', 'ไป', 'เชียงใหม่', 'เมื่อวาน', 'นี้']

tokenize("สวัสดี hello")
# [Token(text='สวัสดี', start=0, end=6), Token(text=' ', start=6, end=7), Token(text='hello', start=7, end=12)]
```

`tokenize` returns each word with its `start`/`end` offset in the input, so
`text[token.start:token.end] == token.text`.

## Options

| Option | Default | What it does |
|---|---|---|
| `keep_whitespace` | `True` | `False` drops tokens made only of spaces. Tabs, new lines and zero-width spaces stay. |
| `join_broken_num` | `True` | Rejoins numbers like `19:32`, `1,234.5` and `127.0.0.1` (Thai digits too) into one token. |

```python
word_tokenize("วันนี้ อากาศดีมาก", keep_whitespace=False)
# ['วันนี้', 'อากาศ', 'ดีมาก']

word_tokenize("นัดเวลา 19:32น.")
# ['นัด', 'เวลา', ' ', '19:32', 'น.']
word_tokenize("นัดเวลา 19:32น.", join_broken_num=False)
# ['นัด', 'เวลา', ' ', '19', ':', '32', 'น.']
```

## Command line

```bash
iapp-tokenize "Hello, world! สวัสดีครับ ยินดีต้อนรับ"
# Hello | , | world | ! | สวัสดี | ครับ | ยินดีต้อนรับ
```

## How it works

Words are found with [nlpO3](https://github.com/PyThaiNLP/nlpo3), a Rust
version of PyThaiNLP's default `newmm` engine, using a dictionary of 62,107
Thai words. The tokenizer is built for Thai: English is split at digits, so
`iPhone15` becomes `iPhone` `15`.

The earlier rule-based tokenizer is still available as `iapp_nlp.tokenizer`.

## Notes

- Needs Python 3.9 or later.
- nlpO3 has no prebuilt wheel for Linux on ARM (aarch64), so there pip builds it
  from source and needs a [Rust toolchain](https://rustup.rs).
- The dictionary `iapp_nlp/data/words_th.txt` is `words_th.txt` from
  [PyThaiNLP](https://github.com/PyThaiNLP/pythainlp), released under
  [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
