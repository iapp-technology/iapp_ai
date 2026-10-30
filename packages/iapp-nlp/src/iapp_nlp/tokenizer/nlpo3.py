"""Thai word segmentation with nlpo3 (newmm in Rust) and the bundled dictionary."""

import threading
from importlib.resources import as_file, files
from typing import List

import nlpo3

_DICT_NAME = "iapp_nlp_words_th"
_DICT_FILE = "words_th.txt"
_load_lock = threading.Lock()
_dict_loaded = False


def load_dict() -> None:
    """Load the bundled dictionary into nlpo3 once, even when called from many threads."""
    global _dict_loaded
    with _load_lock:
        if _dict_loaded:
            return
        # nlpo3 reads the whole file into memory, so the file may go once loaded
        with as_file(files("iapp_nlp") / "data" / _DICT_FILE) as path:
            message, ok = nlpo3.load_dict(str(path), _DICT_NAME)
        if not ok:  # nlpo3 reports a failure in its return value, it does not raise
            raise RuntimeError(f"Failed to load the iapp_nlp dictionary: {message}")
        _dict_loaded = True


def segment(text: str) -> List[str]:
    """Split ``text`` into words; joining the result gives back ``text`` exactly."""
    load_dict()
    return nlpo3.segment(text, _DICT_NAME)
