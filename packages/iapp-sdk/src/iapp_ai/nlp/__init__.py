"""Offline Thai NLP, no API key: word tokenizers (``iapp_ai.nlp.tokenizer``) and text utilities
(``iapp_ai.nlp.util``).

The word tokenizers need numpy and ONNX Runtime, which ``pip install "iapp-ai[nlp]"`` installs;
everything else works with ``pip install iapp-ai``.
"""

from .tokenizer import Token, Tokenizer, tokenize, word_tokenize, word_tokenize_nbest
from .util import normalize

__all__ = [
    "Token",
    "Tokenizer",
    "normalize",
    "tokenize",
    "word_tokenize",
    "word_tokenize_nbest",
]
