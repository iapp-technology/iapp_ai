# iapp-nlp

Free Thai word, subword, syllable and sentence tokenizer and text normalizer from [iApp Technology](https://iapp.co.th).
No API key, runs offline, and the Thai dictionary and models are included.

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

## Your own words

Names and new words that are not in the dictionary come out in pieces. Add them
with `extra_words`, or replace the whole dictionary with `custom_dict`.

```python
from iapp_nlp import Tokenizer, word_tokenize

word_tokenize("ชาไข่มุกบราวน์ชูการ์อร่อย")
# ['ชา', 'ไข่', 'มุ', 'กบ', 'ราวน์', 'ชู', 'การ์', 'อร่อย']
word_tokenize("ชาไข่มุกบราวน์ชูการ์อร่อย", extra_words=["บราวน์ชูการ์"])
# ['ชา', 'ไข่มุก', 'บราวน์ชูการ์', 'อร่อย']

tokenizer = Tokenizer(extra_words=["บราวน์ชูการ์"])
tokenizer.word_tokenize("ชาไข่มุกบราวน์ชูการ์อร่อย")
# ['ชา', 'ไข่มุก', 'บราวน์ชูการ์', 'อร่อย']
```

- `iapp_nlp.corpus.thai_words()` returns the bundled words, so
  `custom_dict=thai_words() - {"..."}` removes words.
- Each distinct set of words is loaded once and stays in memory until the
  process ends, since nlpO3 cannot unload a dictionary. Create one `Tokenizer`
  and reuse it rather than building new word sets per request.
- `sent_tokenize` always uses the bundled dictionary, since its model was trained on it.

## Subwords (Thai Character Clusters)

`subword_tokenize` splits text into Thai Character Clusters (TCC), the smallest
pieces that can be cut without breaking a vowel or tone mark off its consonant.

```python
from iapp_nlp import subword_tokenize

subword_tokenize("ขนมชั้น")
# ['ข', 'น', 'ม', 'ชั้น']
subword_tokenize("ประเทศไทย")
# ['ป', 'ระ', 'เท', 'ศ', 'ไท', 'ย']
```

Non-Thai characters come out one at a time, and `keep_whitespace=False` works
as in `word_tokenize`. The rules are the improved TCC rules from PyThaiNLP
(`tcc_p`), used under the Apache License 2.0 (see `LICENSE-APACHE`).

## Syllables

`syllable_tokenize` splits text into syllables with the Han-solo CRF model,
which also handles social media spelling such as repeated letters.

```python
from iapp_nlp import syllable_tokenize

syllable_tokenize("นายกรัฐมนตรี")
# ['นา', 'ยก', 'รัฐ', 'มน', 'ตรี']
syllable_tokenize("ม่ายยยย อร่อยมากกกก", keep_whitespace=False)
# ['ม่ายยยย', 'อร่อย', 'มากกกก']
```

- Tabs and new lines come out as pieces of their own.
- Digits written right next to Thai can split wrongly: `iPhone15ราคา` gives `iPhone1` `5รา` `คา`.

The model and feature code come from [Han-solo](https://github.com/PyThaiNLP/Han-solo)
and PyThaiNLP, used under the Apache License 2.0 (see `LICENSE-APACHE`).

## Sentences

`sent_tokenize` splits text into sentences. Thai has no full stop, so a CRF
model decides which spaces end a sentence.

```python
from iapp_nlp import sent_tokenize

sent_tokenize("หิวข้าวมากๆ แต่ไม่รู้จะกินอะไรดี")
# ['หิวข้าวมากๆ ', 'แต่ไม่รู้จะกินอะไรดี']
sent_tokenize("สวัสดีครับ! วันนี้ว่างไหม? ไปเที่ยวกัน", keep_whitespace=False)
# ['สวัสดีครับ!', 'วันนี้ว่างไหม?', 'ไปเที่ยวกัน']
```

- A new line always ends a sentence; blank lines stay on the sentence before them.
- `!`, `.` and `?` end a sentence, so abbreviations such as `ดร.` and `กทม.` do too.
- Joining the sentences gives back the input text.

The model is PyThaiNLP's `crfcut` (trained on TED subtitles), used under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); the feature code comes
from PyThaiNLP under the Apache License 2.0 (see `LICENSE-APACHE`).

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

`reign_year_to_ad` and `now_reign_year` convert reign years. On Windows, the
Thai time zone comes from the `tzdata` package, which pip installs there. The
code follows PyThaiNLP, used under the Apache License 2.0 (see `LICENSE-APACHE`).

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

The earlier rule-based tokenizer is still available as `iapp_nlp.tokenizer.legacy`.

## Notes

- Needs Python 3.9 or later. On Windows, pip also installs `tzdata` for the Thai time zone.
- nlpO3 has no prebuilt wheel for Linux on ARM (aarch64), so there pip builds it
  from source and needs a [Rust toolchain](https://rustup.rs).
- The dictionary `iapp_nlp/data/words_th.txt` is `words_th.txt` from
  [PyThaiNLP](https://github.com/PyThaiNLP/pythainlp), released under
  [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
- The stopword list `iapp_nlp/data/stopwords_th.txt` and the province list
  `iapp_nlp/data/thailand_provinces_th.csv` are from PyThaiNLP, released under
  CC0 1.0. The stopwords come from a thesis by เพ็ญศิริ ลี้ตระกูล (Thammasat
  University, 2008). The loaders and `tag_provinces` follow PyThaiNLP's code,
  used under the Apache License 2.0 (see `LICENSE-APACHE`).
