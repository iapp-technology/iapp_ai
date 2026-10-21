"""Command-line entry point: ``iapp-tokenize "ข้อความ"``."""

import sys

from .tokenizer import word_tokenize


def main() -> None:
    text = " ".join(sys.argv[1:]) or sys.stdin.read()
    print(" | ".join(word_tokenize(text)))


if __name__ == "__main__":
    main()