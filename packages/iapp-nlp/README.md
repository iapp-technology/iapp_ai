# iapp-nlp has moved into iapp-ai

The `iapp-nlp` package gets no more releases. Its code is now `iapp_ai.nlp`,
part of [iapp-ai](../iapp-sdk) 2.0.0 and later:

```bash
pip install "iapp-ai[nlp]"
```

```python
from iapp_ai.nlp import word_tokenize   # was: from iapp_nlp import word_tokenize
```

The functions, their options and the `iapp-tokenize` command are the same; see
the [`iapp_ai.nlp` guide](../iapp-sdk/docs/nlp.md). `iapp-nlp` 0.1.0 stays on
PyPI and keeps working, but gets no updates.
