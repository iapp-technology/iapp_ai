"""Command-line entry point: ``iapp-tokenize "ข้อความ"`` or ``iapp-tokenize --unit long "ข้อความ"``."""

import argparse
import sys
from typing import List, Optional

from .tokenizer import Tokenizer
from .tokenizer.core import NLP_EXTRA_MODULES, UNITS


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
    # UTF-8 whatever the console's locale: on Windows a redirected stream used the ANSI code page and failed
    # on Thai; utf-8-sig drops a byte-order mark at the start of the input
    for stream, encoding in ((sys.stdin, "utf-8-sig"), (sys.stdout, "utf-8")):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding=encoding)
    # load the model before reading standard input, so that a missing nlp extra is said at once
    try:
        tokenizer = Tokenizer(args.unit)
    except ImportError as e:
        if e.name not in NLP_EXTRA_MODULES:
            raise
        sys.exit(f"iapp-tokenize: {e}")
    # strip so the new line that ends stdin input does not print as a token
    try:
        text = (" ".join(args.text).lstrip("\ufeff") or sys.stdin.read()).strip()
    except UnicodeDecodeError:
        sys.exit("the input is not UTF-8: save the file as UTF-8 and run again")
    print(" | ".join(tokenizer.word_tokenize(text, keep_whitespace=False)))


if __name__ == "__main__":
    main()
