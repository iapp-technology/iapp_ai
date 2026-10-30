"""Command-line entry point: ``iapp-tokenize "ข้อความ"``."""

import sys

from .tokenizer import word_tokenize


def main() -> None:
    # strip so the new line that ends stdin input does not print as a token
    text = (" ".join(sys.argv[1:]) or sys.stdin.read()).strip()
    print(" | ".join(word_tokenize(text, keep_whitespace=False)))


if __name__ == "__main__":
    main()