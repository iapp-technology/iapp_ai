# iapp-nlp

Free Thai word tokenizer and text normalizer from [iApp Technology](https://iapp.co.th).
No API key, runs offline, and the Thai models are included.

```bash
pip install iapp-nlp
```

```python
from iapp_nlp import word_tokenize, tokenize

word_tokenize("แม่น้ำเจ้าพระยาไหลผ่านกรุงเทพ")
# ['แม่น้ำ', 'เจ้าพระยา', 'ไหล', 'ผ่าน', 'กรุงเทพ']

tokenize("สวัสดี hello")
# [Token(text='สวัสดี', start=0, end=6), Token(text=' ', start=6, end=7), Token(text='hello', start=7, end=12)]
```

`tokenize` returns each word with its `start`/`end` offset in the input, so
`text[token.start:token.end] == token.text`. Words are found by the
OpenThai2.0-LATTE-WordSeg-Lite model, which runs on the CPU (see
[How it works](#how-it-works)).

## Options

| Option | Default | What it does |
|---|---|---|
| `keep_whitespace` | `True` | Each whitespace character is a token of its own. `False` drops spaces; tabs, new lines and zero-width spaces stay. |
| `join_broken_num` | `True` | Rejoins numbers like `4.1`, `19:32`, `1,234.5` and `127.0.0.1` (Thai digits too) into one token. |
| `unit` | `"short"` | How finely to split: `"long"`, `"short"` or `"minimal"` (see [Units](#units)). |
| `extra_words` | `None` | Words for the model to look out for, such as names (see [Your own words](#your-own-words)). |

```python
word_tokenize("วันนี้ อากาศดีมาก", keep_whitespace=False)
# ['วัน', 'นี้', 'อากาศ', 'ดี', 'มาก']

word_tokenize("ข้อ 4.1 ระบุว่า")
# ['ข้อ', ' ', '4.1', ' ', 'ระบุ', 'ว่า']
word_tokenize("ข้อ 4.1 ระบุว่า", join_broken_num=False)
# ['ข้อ', ' ', '4', '.', '1', ' ', 'ระบุ', 'ว่า']
```

A run of Latin letters or of digits, Thai digits too, is never split, but a
letter run and a digit run can be: `iPhone15` gives `iPhone` `15`.

## Units

Thai has no single rule for what a word is, so the model gives three units,
from coarse to fine: `long` keeps compounds whole, `short` gives words, and
`minimal` splits words into their smallest meaningful parts.

| `unit` | เจ้าหน้าที่การศึกษาเปิดเผยว่า |
|---|---|
| `"long"` | เจ้าหน้าที่ \| การศึกษา \| เปิดเผย \| ว่า |
| `"short"` (default) | เจ้า \| หน้าที่ \| การ \| ศึกษา \| เปิด \| เผย \| ว่า |
| `"minimal"` | เจ้า \| หน้า \| ที่ \| การ \| ศึกษา \| เปิด \| เผย \| ว่า |

```python
word_tokenize("เจ้าหน้าที่การศึกษาเปิดเผยว่า", unit="long")
# ['เจ้าหน้าที่', 'การศึกษา', 'เปิดเผย', 'ว่า']
```

## Your own words

Names and new words can come out in pieces. `extra_words` adds them to the
model's dictionary:

```python
word_tokenize("ไอแอพพ์เทคโนโลยีอยู่ที่กรุงเทพ")
# ['ไอแอพพ์', 'เทคโนโลยี', 'อยู่', 'ที่', 'กรุงเทพ']
word_tokenize("ไอแอพพ์เทคโนโลยีอยู่ที่กรุงเทพ", extra_words=["ไอแอพพ์เทคโนโลยี"])
# ['ไอแอพพ์เทคโนโลยี', 'อยู่', 'ที่', 'กรุงเทพ']
```

- The words are hints, not rules: the model weighs them against the text around
  them and can still split them. `unit="long"` keeps them whole most often.
- Words with spaces, or shorter than 2 or longer than 16 characters, are left
  out with a `UserWarning`.
- Each distinct set of words loads the model again, which takes about 0.1
  seconds and 10 MB that stays in memory until the process ends. Keep to a few
  fixed word sets rather than building new ones per request.
- `iapp_nlp.corpus.thai_words()` returns PyThaiNLP's list of 62,106 Thai words.
  The model does not use it.

## Many texts at once

`Tokenizer` loads the model when you make it, so a server can load it at
start-up. Its batch methods split many texts in one call, which is faster than
one call per text.

```python
from iapp_nlp import Tokenizer

tokenizer = Tokenizer()  # also takes unit= and extra_words=
tokenizer.word_tokenize_batch(["ฉันกินข้าวที่บ้าน", "วันนี้อากาศดีมาก"])
# [['ฉัน', 'กิน', 'ข้าว', 'ที่', 'บ้าน'], ['วัน', 'นี้', 'อากาศ', 'ดี', 'มาก']]
```

`tokenize_batch` gives the tokens with their offsets, and `tokenize` and
`word_tokenize` work as the functions of the same name. One tokenizer can serve
many threads at once. About 1% of texts can come out slightly differently in a
batch than alone (see [How it works](#how-it-works)).

## Normalize

`normalize` fixes common Thai typing errors before you tokenize: repeated or
misordered vowels and tone marks, spaces before a mark, zero-width characters
and duplicate spaces.

```python
from iapp_nlp import normalize

normalize("เเปลก")       # two Sara E
# 'แปลก'
normalize("แล้้ว")       # repeated tone mark
# 'แล้ว'
normalize("พ ุ่มดอกไม้")  # space before a vowel
# 'พุ่มดอกไม้'
```

It also trims spaces at both ends and collapses blank lines. Letters are never
changed, so a misspelled word stays misspelled. The rules are from PyThaiNLP's
`normalize`, used under the Apache License 2.0 (see `LICENSE-APACHE`).

## Stopwords and provinces

`iapp_nlp.corpus` has two word lists, and `iapp_nlp.tag.tag_provinces` marks the
words that are province names.

```python
from iapp_nlp import word_tokenize
from iapp_nlp.corpus import provinces, thai_stopwords
from iapp_nlp.tag import tag_provinces

words = word_tokenize("ผมไปเชียงใหม่กับกรุงเทพมหานคร", keep_whitespace=False)
[w for w in words if w not in thai_stopwords()]
# ['ผม', 'เชียงใหม่', 'กรุงเทพมหานคร']
tag_provinces(words)
# [('ผม', 'O'), ('ไป', 'O'), ('เชียงใหม่', 'B-LOCATION'), ('กับ', 'O'), ('กรุงเทพมหานคร', 'B-LOCATION')]
len(provinces())
# 77
```

`provinces(details=True)` also gives each province's abbreviation and English
name. Names are matched exactly, so `กทม` and `Bangkok` are not tagged.

## Numbers and digits

`iapp_nlp.util` reads numbers and amounts of money aloud in Thai, and converts
between Thai and Arabic digits. This helps prepare text for text-to-speech, or
clean up digits read by OCR.

```python
from iapp_nlp.util import (
    arabic_digit_to_thai_digit,
    bahttext,
    digit_to_text,
    num_to_thaiword,
    thai_digit_to_arabic_digit,
)

bahttext(150.50)
# 'หนึ่งร้อยห้าสิบบาทห้าสิบสตางค์'
num_to_thaiword(2569)
# 'สองพันห้าร้อยหกสิบเก้า'
digit_to_text("โทร 0812345678")
# 'โทร ศูนย์แปดหนึ่งสองสามสี่ห้าหกเจ็ดแปด'
thai_digit_to_arabic_digit("ยอด ๑๒,๕๐๐.๕๐ บาท")
# 'ยอด 12,500.50 บาท'
arabic_digit_to_thai_digit("พ.ศ. 2569")
# 'พ.ศ. ๒๕๖๙'
```

`num_to_thaiword_float` reads decimals digit by digit (`3.14` → `สามจุดหนึ่งสี่`), and
`text_to_arabic_digit` / `text_to_thai_digit` turn one Thai digit word into a
digit (`"เก้า"` → `"9"`). The code follows PyThaiNLP, used under the Apache
License 2.0 (see `LICENSE-APACHE`).

## Thai dates

`iapp_nlp.util` converts Buddhist Era years and reads and writes dates with Thai
month and weekday names.

```python
from datetime import datetime
from iapp_nlp.util import convert_years, thai_strftime, thai_strptime, thaiword_to_date

convert_years("2569", src="be", target="ad")
# '2026'
thai_strptime("15 ก.ค. 2565", "%d %B %Y")
# datetime.datetime(2022, 7, 15, 0, 0, tzinfo=zoneinfo.ZoneInfo(key='Asia/Bangkok'))
thai_strftime(datetime(2026, 10, 30), "%A %d %B %Y")
# 'วันศุกร์ 30 ตุลาคม 2569'
thai_strftime(datetime(2026, 10, 30), "%a %-d %b %y")
# 'ศ 30 ต.ค. 69'
thaiword_to_date("พรุ่งนี้", datetime(2026, 10, 30))
# datetime.datetime(2026, 10, 31, 0, 0)
```

`reign_year_to_ad` and `now_reign_year` convert reign years. The Thai time zone
comes from the `tzdata` package, which pip installs, so it also works on systems
without a time zone database such as Windows or slim containers. The code
follows PyThaiNLP, used under the Apache License 2.0 (see `LICENSE-APACHE`).

## Command line

```bash
iapp-tokenize "Hello, world! สวัสดีครับ ยินดีต้อนรับ"
# Hello | , | world | ! | สวัสดี | ครับ | ยินดี | ต้อนรับ
iapp-tokenize --unit long "เจ้าหน้าที่การศึกษาเปิดเผยว่า"
# เจ้าหน้าที่ | การศึกษา | เปิดเผย | ว่า
```

Without text, `iapp-tokenize` reads standard input.

## How it works

Words are found by OpenThai2.0-LATTE-WordSeg-Lite, a model from OpenThai and
iApp Technology with 1.17 million parameters and a dictionary of 177,385 words.
For each character it reads the dictionary words around it and decides whether
a word starts there, for all three units at once. Its authors measured an
average word F1 of 85.6 on seven Thai test sets, against 70.9 for PyThaiNLP's
dictionary-based `newmm`.

- It runs on the CPU with [ONNX Runtime](https://onnxruntime.ai) and NumPy,
  which pip installs. The model (3 MB) and its dictionary (0.8 MB) are in the
  package.
- The model loads on first use, in about 0.2 seconds, and a process that uses
  it takes up to about 140 MB of memory.
- On one CPU thread it splits about 60,000 characters per second one text at a
  time, and about 100,000 with the batch methods. For more, run several
  processes rather than more threads.
- The model's int8 scales are worked out per batch, so 0.4 to 1.3% of lines can
  come out slightly differently in a batch than alone.
- It is built for Thai: other scripts pass through.

## Notes

- Needs Python 3.10 or later. pip also installs NumPy, ONNX Runtime and
  `tzdata` (for the Thai time zone).
- ONNX Runtime has wheels for Linux (x86-64 and ARM64, glibc), macOS and
  Windows, so pip cannot install iapp-nlp on Alpine Linux and other musl-based
  systems, or on 32-bit Linux. Intel Macs and Python 3.10 get ONNX Runtime
  1.23, its last release for them.
- The word list `iapp_nlp/data/words_th.txt` is `words_th.txt` from
  [PyThaiNLP](https://github.com/PyThaiNLP/pythainlp), released under
  [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
- The stopword list `iapp_nlp/data/stopwords_th.txt` and the province list
  `iapp_nlp/data/thailand_provinces_th.csv` are from PyThaiNLP, released under
  CC0 1.0. The stopwords come from a thesis by เพ็ญศิริ ลี้ตระกูล (Thammasat
  University, 2008). The loaders and `tag_provinces` follow PyThaiNLP's code,
  used under the Apache License 2.0 (see `LICENSE-APACHE`).

## License

`MIT AND Apache-2.0 AND CC-BY-SA-4.0 AND Unicode-DFS-2016`:

- iApp Technology's own code: MIT (see `LICENSE`).
- Code from PyThaiNLP: Apache License 2.0
  (see `LICENSE-APACHE`). Each such file starts with SPDX lines naming its source.
- The OpenThai2.0-LATTE-WordSeg-Lite code, `iapp_nlp/tokenizer/latte.py`:
  Apache License 2.0 (see `LICENSE-APACHE` and `NOTICE`).
- Its model files in `iapp_nlp/data/latte/` (the network, the dictionary and
  the character table): [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
  (see `LICENSES/CC-BY-SA-4.0.txt`). Commercial use allowed. If you modify these
  files and share them, share them under the same license; this does not reach
  code that only uses them. The dictionary's entries from ICU also carry the
  Unicode license (see `LICENSES/Unicode-DFS-2016.txt`). The model was trained
  only on data whose licenses allow commercial use; `NOTICE` lists the sources
  and their attributions.
- The word, stopword and province lists: CC0 1.0.
