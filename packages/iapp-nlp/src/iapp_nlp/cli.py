"""Command-line entry point: ``iapp-tokenize "ข้อความ"`` or ``iapp-tokenize --unit long "ข้อความ"``."""

import argparse
import sys
from typing import List, Optional

from .tokenizer import word_tokenize
from .tokenizer.core import UNITS


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(prog="iapp-tokenize", description="Split Thai text into words.")
    parser.add_argument("text", nargs="*", help="the text to split (default: read standard input)")
    parser.add_argument(
        "--unit",
        choices=UNITS,
        default="short",
        help="long keeps compounds whole, short gives words (the default), "
        "minimal splits words into their smallest meaningful parts",
    )
    args = parser.parse_args(argv)
    # strip so the new line that ends stdin input does not print as a token
    text = (" ".join(args.text) or sys.stdin.read()).strip()
    print(" | ".join(word_tokenize(text, keep_whitespace=False, unit=args.unit)))


if __name__ == "__main__":
    main()
