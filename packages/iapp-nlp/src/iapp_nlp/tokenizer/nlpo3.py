"""Thai word segmentation with nlpo3 (newmm in Rust) and the bundled dictionary."""

import hashlib
import os
import tempfile
import threading
from importlib.resources import as_file, files
from typing import Dict, FrozenSet, List

import nlpo3

DICT_NAME = "iapp_nlp_words_th"
_DICT_FILE = "words_th.txt"
_load_lock = threading.Lock()
_dict_loaded = False
_custom_dicts: Dict[str, str] = {}  # sha256 of the word set -> nlpo3 dictionary name


def load_dict() -> None:
    """Load the bundled dictionary into nlpo3 once, even when called from many threads."""
    global _dict_loaded
    with _load_lock:
        if _dict_loaded:
            return
        # nlpo3 reads the whole file into memory, so the file may go once loaded
        with as_file(files("iapp_nlp") / "data" / _DICT_FILE) as path:
            message, ok = nlpo3.load_dict(str(path), DICT_NAME)
        if not ok:  # nlpo3 reports a failure in its return value, it does not raise
            raise RuntimeError(f"Failed to load the iapp_nlp dictionary: {message}")
        _dict_loaded = True


def load_words(words: FrozenSet[str]) -> str:
    """Load ``words`` into nlpo3 once per distinct set and return the dictionary name.

    nlpo3 cannot unload a dictionary, so every distinct set stays in memory until the process ends.
    """
    content = "\n".join(sorted(words))
    key = hashlib.sha256(content.encode("utf-8")).hexdigest()
    with _load_lock:
        if key in _custom_dicts:
            return _custom_dicts[key]
        name = f"iapp_nlp_custom_{key}"
        # nlpo3 only loads from a file, and reads it all into memory, so the file may go once loaded
        fd, path = tempfile.mkstemp(suffix=".txt")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as file:
                file.write(content)
            message, ok = nlpo3.load_dict(path, name)
        finally:
            os.remove(path)
        if not ok:
            raise RuntimeError(f"Failed to load the custom dictionary: {message}")
        _custom_dicts[key] = name
        return name


def segment(text: str, dict_name: str = DICT_NAME) -> List[str]:
    """Split ``text`` into words; joining the result gives back ``text`` exactly."""
    if dict_name == DICT_NAME:
        load_dict()
    return nlpo3.segment(text, dict_name)
