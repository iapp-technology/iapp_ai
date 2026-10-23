"""iapp_nlp — free Thai NLP tools (word tokenizer)."""

__version__ = "0.1.0"

from .core import tokenize, word_tokenize
from .tokenizer import Token

__all__ = ["Token", "tokenize", "word_tokenize"]