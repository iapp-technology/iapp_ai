# SPDX-License-Identifier: Apache-2.0
"""OpenThai2.0-LATTE-WordSeg-Lite runtime: Thai word segmentation on the CPU with ONNX Runtime and NumPy only.

Pipeline (identical to the LATTE research code it was distilled and benchmarked with):
each line of a text loses its whitespace; every character gets an id (frequent characters) or a
Unicode-class bucket, and 13 dictionary bits (which dictionary words of each length bucket start,
end or continue there); the network gives one word-start logit per character; a word starts where
the logit is >= 0 unless Thai spelling rules it out; words are mapped back onto the original text,
runs of Latin letters or digits are never split, and every whitespace character is its own token.
A line longer than MAX_WINDOW characters is read in overlapping windows, so memory stays bounded.
"""
from __future__ import annotations

import gzip
import json
import warnings
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import onnxruntime as ort

ASSETS = Path(__file__).parent.parent / "data" / "latte"
N_CLASSES = 13                       # ids 0-12: padding + Unicode-class buckets for unknown characters
N_LEX = 13                           # 6 length buckets x (starts, ends) + inside a word
LEN_BUCKET = np.array([0, 0, 0, 1, 2, 3, 3, 4, 4, 4] + [5] * 200, np.int64)
# Thai spelling: no word starts before a combining mark or a following vowel, none after a leading vowel
NO_START = np.array([0x0E30, 0x0E31, 0x0E32, 0x0E33, *range(0x0E34, 0x0E3B), 0x0E45, *range(0x0E47, 0x0E4F)],
                    np.uint32)
LEADING = np.array(range(0x0E40, 0x0E45), np.uint32)
HASH_MUL = np.uint64(0x9E3779B97F4A7C15)
MAX_ROWS = 512
DEFAULT_BATCH_CHARS = 4096           # 2-4K characters per batch keep the LSTM in cache on one thread
# The network needs about 11 KB per character of the longest line in a batch. A longer line is read in
# windows of MAX_WINDOW characters that overlap by 2 x WINDOW_CONTEXT; each keeps the decisions of its middle,
# where it sees at least WINDOW_CONTEXT characters on both sides (lines up to MAX_WINDOW: read whole, as before).
MAX_WINDOW = 10_000
WINDOW_CONTEXT = 500
MAX_NBEST_CHARS = 10_000             # tokenize_nbest: longest text, whitespace not counted
MAX_NBEST = 100                      # tokenize_nbest: most readings


def _codes(text: str) -> np.ndarray:
    return np.frombuffer(text.encode("utf-32-le", "surrogatepass"), np.uint32)


def _check_text(text: object) -> None:
    if not isinstance(text, str):
        raise TypeError(f"text must be a str, not {type(text).__name__}")


def _windows(n: int) -> list[tuple[int, int, int, int]]:
    """(start, end, keep_from, keep_to) of the windows the network reads for a line of ``n`` characters: the
    whole line up to MAX_WINDOW characters, else overlapping windows whose kept middles tile the line."""
    if n <= MAX_WINDOW:
        return [(0, n, 0, n)]
    out, keep = [], 0
    while keep < n:
        start = max(0, keep - WINDOW_CONTEXT)
        end = min(n, start + MAX_WINDOW)
        keep_to = n if end == n else end - WINDOW_CONTEXT
        out.append((start, end, keep, keep_to))
        keep = keep_to
    return out


def _hash_rows(codes: np.ndarray) -> np.ndarray:
    """64-bit polynomial hash of each row of a (n, L) code-point matrix."""
    codes = codes.astype(np.uint64)
    h = codes[:, 0].copy()
    for j in range(1, codes.shape[1]):
        h = h * HASH_MUL + codes[:, j]
    return h


class Lexicon:
    """Dictionary words of 2..max_len characters, as sorted 64-bit hashes per word length.

    ``bits`` finds every dictionary word in every row of a batch (all overlapping matches, like the
    Aho-Corasick pass of the research code) with one vectorised rolling-hash pass per word length.
    """

    def __init__(self, words: Iterable[str], max_len: int = 16) -> None:
        groups: dict[int, list[str]] = {}
        for w in words:
            if 2 <= len(w) <= max_len and not any(c.isspace() for c in w):
                groups.setdefault(len(w), []).append(w)
        self.hashes = {n: np.unique(_hash_rows(_codes("".join(ws)).reshape(len(ws), n)))
                       for n, ws in groups.items()}
        self.lengths = sorted(self.hashes)
        self.size = sum(len(ws) for ws in groups.values())

    def bits(self, codes: np.ndarray, lengths: np.ndarray) -> np.ndarray:
        """(R, W) code points of a padded batch -> (R, W) int64 dictionary bits."""
        rows, width = codes.shape
        bits = np.zeros((rows, width), np.int64)
        cover = np.zeros((rows, width + 1), np.int64)
        c = codes.astype(np.uint64)
        h, n = c, 1                                   # h[:, i] = hash of the n characters from i
        ends = np.arange(1, width + 1)[None, :]
        for target in self.lengths:
            while n < target and h.shape[1] > 0:
                h = h[:, :-1] * HASH_MUL + c[:, n:]
                n += 1
            if n < target or h.shape[1] == 0:
                break
            table = self.hashes[n]
            hit = table[np.minimum(np.searchsorted(table, h), len(table) - 1)] == h
            hit &= (ends[:, :h.shape[1]] + (n - 1)) <= lengths[:, None]   # window inside the row
            if not hit.any():
                continue
            m, b = hit.shape[1], int(LEN_BUCKET[n])
            hit64 = hit.astype(np.int64)
            bits[:, :m] |= hit64 << b                 # a word of this length starts here
            bits[:, n - 1:] |= hit64 << (6 + b)       # ... ends here
            if n > 2:                                 # ... or continues here
                cover[:, 1:m + 1] += hit64
                cover[:, n - 1:width] -= hit64
        bits |= (np.cumsum(cover[:, :width], axis=1) > 0).astype(np.int64) << 12
        return bits


_Node = Optional[Tuple[int, "_Node"]]          # n-best: a word end and the reading before it


def _unroll(node: _Node) -> tuple[int, ...]:
    """The word ends of one n-best reading, first to last."""
    ends = []
    while node is not None:
        ends.append(node[0])
        node = node[1]
    return tuple(reversed(ends))


def _user_words(user_words: Iterable[str] | None, max_len: int) -> list[str]:
    """User dictionary words, stripped; a word the dictionary cannot hold is left out with a warning."""
    if user_words is None:
        return []
    if isinstance(user_words, str):
        raise TypeError("user_words takes a list of words, not one string")
    words = []
    for w in user_words:
        if not isinstance(w, str):
            raise TypeError(f"user_words must be strings, not {type(w).__name__}")
        if w.strip():
            words.append(w.strip())
    unused = [w for w in words if not 2 <= len(w) <= max_len or any(c.isspace() for c in w)]
    if unused:
        shown = ", ".join(repr(w) for w in unused[:5]) + (", ..." if len(unused) > 5 else "")
        warnings.warn(f"{len(unused)} of the user words not used (a dictionary word has 2 to {max_len} characters "
                      f"and no whitespace): {shown}", UserWarning, stacklevel=3)
    skip = set(unused)
    return [w for w in words if w not in skip]


def _same_run(a: str, b: str) -> bool:
    """Two adjacent characters of one Latin-letter run or one digit run (never split)."""
    return a.isascii() and b.isascii() and ((a.isalpha() and b.isalpha()) or (a.isdigit() and b.isdigit()))


def _batches(lengths: Sequence[int], batch_chars: int) -> list[list[int]]:
    """Group line indices by length under a padded-character budget (<= 0: one line per batch)."""
    order = sorted(range(len(lengths)), key=lengths.__getitem__)
    if batch_chars <= 0:
        return [[i] for i in order]
    batches: list[list[int]] = []
    cur: list[int] = []
    cur_max = 0
    for i in order:
        new_max = max(cur_max, lengths[i] + 3)
        if cur and (new_max * (len(cur) + 1) > batch_chars or len(cur) >= MAX_ROWS):
            batches.append(cur)
            cur, new_max = [], lengths[i] + 3
        cur.append(i)
        cur_max = new_max
    if cur:
        batches.append(cur)
    return batches


class Segmenter:
    """Thai word segmenter.

    >>> seg = Segmenter()                 # unit "short", one CPU thread
    >>> seg.tokenize("ฉันกินข้าวที่บ้าน")
    >>> Segmenter(unit="minimal").tokenize("แม่น้ำเจ้าพระยาไหลผ่านกรุงเทพ")

    Units (``seg.units``, coarse to fine) are named after the units of the Japanese corpus BCCWJ, its long
    and short unit words and the smallest units under them: ``long`` keeps compounds whole (การศึกษา,
    เจ้าหน้าที่), ``short`` (the default) splits them into words (การ|ศึกษา), and ``minimal`` splits words
    into the smallest meaningful units (โรง|เรียน). A unit's boundaries include every coarser unit's,
    except for a unit listed in ``seg.unnested_units``, which follows its own convention (``minimal``
    keeps "1." and "(ก)" whole, where ``short`` splits them).

    ``user_words`` join the dictionary the model reads: hints, not cuts it must make. A dictionary word has 2 to
    16 characters and no whitespace; other words are not used (with a warning).

    ``model_path`` and ``lexicon_path`` replace the shipped network (another ONNX graph of the same model,
    e.g. before quantisation) or dictionary (a gzip word list): for development and testing only.
    """

    def __init__(self, *, unit: str | None = None, threads: int = 1, batch_chars: int = DEFAULT_BATCH_CHARS,
                 user_words: Iterable[str] | None = (), model_path: str | Path | None = None,
                 lexicon_path: str | Path | None = None) -> None:
        manifest = json.loads((ASSETS / "manifest.json").read_text(encoding="utf-8"))
        info = manifest["model"]
        path = Path(model_path) if model_path else ASSETS / info["file"]
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = threads
        opts.inter_op_num_threads = 1
        opts.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        self.session = ort.InferenceSession(str(path), opts, providers=["CPUExecutionProvider"])
        self._uses_bits = any(i.name == "bits" for i in self.session.get_inputs())
        meta = self.session.get_modelmeta().custom_metadata_map
        levels = list(json.loads(meta.get("config", "{}")).get("levels", []))   # the network's outputs, coarse to fine
        names = info.get("units") or levels                    # their public names, in the same order (manifest.json)
        if len(names) != len(levels):
            raise ValueError("manifest.json: `units` must name every output of the model")
        self.units: list[str] = list(names)                    # coarse to fine
        self.unit = None                                       # this segmenter's default unit
        self.unnested_units: list[str] = [u for u in info.get("unnested_units", []) if u in self.units]
        if self.units:
            default = info.get("default_unit")
            self.unit = unit or (default if default in self.units else self.units[-1])
            self._unit_index(self.unit)                        # validate
        elif unit is not None:
            raise ValueError("this model has one unit only")
        vocab = json.loads(meta["vocab"])
        table = np.load(ASSETS / manifest["charclass"])["classes"].astype(np.int16)
        table[np.fromiter(map(ord, vocab), np.int64, len(vocab))] = np.arange(N_CLASSES, N_CLASSES + len(vocab))
        self._ids = table
        lex_file = Path(lexicon_path) if lexicon_path else ASSETS / manifest["lexicon"]
        with gzip.open(lex_file, "rt", encoding="utf-8") as f:
            words = f.read().split("\n")
        max_len = manifest.get("max_word_len", 16)
        self.lexicon = Lexicon([*words, *_user_words(user_words, max_len)], max_len)
        self.batch_chars = batch_chars

    def _unit_index(self, unit: str) -> int:
        if unit not in self.units:
            raise ValueError(f"unknown unit {unit!r}; available: {', '.join(self.units) or 'none (one unit)'}")
        return self.units.index(unit)

    # ------------------------------------------------------------------ lines without whitespace
    def segment_lines(self, lines: Sequence[str], unit: str | None = None) -> list[list[tuple[int, int]]]:
        """Word spans of whitespace-free lines."""
        if unit is not None and not self.units:
            raise ValueError("this model has one unit only")
        k = self._unit_index(unit or str(self.unit)) if self.units else None
        # one row per line, or per window of a line longer than MAX_WINDOW: (line, start, end, keep_from, keep_to)
        rows = [(i, *w) for i, t in enumerate(lines) for w in _windows(len(t))]
        lengths = [end - start for _, start, end, _, _ in rows]
        word_starts = [np.zeros(len(t), bool) for t in lines]
        for group in _batches(lengths, self.batch_chars):
            width = max(lengths[r] for r in group)
            if width == 0:
                continue
            codes = np.zeros((len(group), width), np.uint32)
            for g, r in enumerate(group):
                i, start, end, _, _ = rows[r]
                codes[g, :lengths[r]] = _codes(lines[i][start:end])
            lens = np.array([lengths[r] for r in group], np.int64)
            valid = np.arange(width)[None, :] < lens[:, None]
            ids = np.where(valid, self._ids[codes], 0).astype(np.int64)
            feed = {"ids": ids, "lengths": lens.astype(np.int32)}
            if self._uses_bits:
                feed["bits"] = self.lexicon.bits(codes, lens)
            logits = self.session.run(["logits"], feed)[0]
            if logits.ndim == 3:     # every unit's logits, coarse to fine: a unit's word starts include
                assert k is not None                                               # all coarser units'
                logits = (logits[..., k] if self.units[k] in self.unnested_units   # (nested) unless unnested
                          else logits[..., :k + 1].max(-1))
            allowed = ~np.isin(codes, NO_START)
            allowed[:, 1:] &= ~np.isin(codes[:, :-1], LEADING)
            starts = (logits >= 0.0) & allowed
            starts[:, 0] = True
            for g, r in enumerate(group):
                i, start, _, keep_from, keep_to = rows[r]
                word_starts[i][keep_from:keep_to] = starts[g, keep_from - start:keep_to - start]
        out = []
        for i, t in enumerate(lines):
            pos = np.flatnonzero(word_starts[i]).tolist() + [len(t)]
            out.append(list(zip(pos[:-1], pos[1:])))
        return out

    # ------------------------------------------------------------------ texts
    def tokenize_batch(self, texts: Sequence[str], keep_whitespace: bool = True,
                       unit: str | None = None) -> list[list[str]]:
        """Tokens of each text. Every whitespace character is a token of its own (dropped when
        ``keep_whitespace`` is False); runs of Latin letters or digits are never split. ``unit``
        overrides the segmenter's unit for this call."""
        if isinstance(texts, str):
            raise TypeError("tokenize_batch takes a list of texts; for one text use tokenize")
        texts = list(texts)                  # a generator is read once
        for text in texts:
            _check_text(text)
        jobs, maps, owner = [], [], []
        for d, text in enumerate(texts):
            start = 0
            for line in text.split("\n"):
                idx = [start + j for j, c in enumerate(line) if not c.isspace()]
                if idx:
                    jobs.append("".join(text[j] for j in idx))
                    maps.append(idx)
                    owner.append(d)
                start += len(line) + 1
        cuts: list[set[int]] = [set() for _ in texts]
        for d, idx, spans in zip(owner, maps, self.segment_lines(jobs, unit)):
            cuts[d].update(idx[s] for s, _ in spans[1:])
        out = []
        for d, text in enumerate(texts):
            space = [j for j, c in enumerate(text) if c.isspace()]
            cut = {j for j in cuts[d] if not _same_run(text[j - 1], text[j])} | set(space) | {j + 1 for j in space}
            bounds = [0] + sorted(j for j in cut if 0 < j < len(text)) + [len(text)]
            toks = [text[a:b] for a, b in zip(bounds[:-1], bounds[1:]) if b > a]
            out.append(toks if keep_whitespace else [t for t in toks if not t.isspace()])
        return out

    def tokenize(self, text: str, keep_whitespace: bool = True, unit: str | None = None) -> list[str]:
        """Tokens of one text (see :meth:`tokenize_batch`)."""
        return self.tokenize_batch([text], keep_whitespace, unit)[0]

    __call__ = tokenize

    # ------------------------------------------------------------------ several readings
    def tokenize_nbest(self, text: str, n: int = 10, unit: str | None = None,
                       keep_whitespace: bool = True) -> list[tuple[list[str], float]]:
        """The ``n`` most probable segmentations of a short text, best first, each with its probability under
        the model: the readings of an ambiguous phrase, such as ตา|กลม and ตาก|ลม.

        Every piece is a dictionary word or a word that the model cuts in one of its units. Whitespace always
        separates and runs of Latin letters or digits stay whole, as in :meth:`tokenize`, whose result comes
        first. The probability of a segmentation is the product of the model's start and no-start
        probabilities over the characters (a measure of plausibility, not calibrated). At most MAX_NBEST
        readings of a text of at most MAX_NBEST_CHARS characters, whitespace not counted."""
        _check_text(text)
        if not 1 <= n <= MAX_NBEST:
            raise ValueError(f"n must be between 1 and {MAX_NBEST}")
        k = self._unit_index(unit or str(self.unit)) if self.units else None
        keep = [j for j, c in enumerate(text) if not c.isspace()]
        if not keep:
            return [([c for c in text] if keep_whitespace else [], 1.0)]
        if len(keep) > MAX_NBEST_CHARS:
            raise ValueError(f"tokenize_nbest reads at most {MAX_NBEST_CHARS:,} characters (whitespace not counted), "
                             f"this text has {len(keep):,}; use tokenize for long texts")
        line = "".join(text[j] for j in keep)
        size = len(line)
        codes = _codes(line)[None, :]
        lens = np.array([size], np.int64)
        feed = {"ids": self._ids[codes].astype(np.int64), "lengths": lens.astype(np.int32)}
        if self._uses_bits:
            feed["bits"] = self.lexicon.bits(codes, lens)
        logits = self.session.run(["logits"], feed)[0][0]
        if logits.ndim == 2:
            assert k is not None
            logits = logits[:, k] if self.units[k] in self.unnested_units else logits[:, :k + 1].max(-1)
        gap = np.zeros(size, bool)                      # whitespace between two characters: always a cut
        gap[1:] = np.diff(np.array(keep)) > 1
        free = ~np.isin(codes[0], NO_START)             # where the model decides; elsewhere no word starts
        free[1:] &= ~np.isin(codes[0, :-1], LEADING)
        free[1:] &= ~np.array([_same_run(line[p - 1], line[p]) for p in range(1, size)], bool)
        log_start = np.where(free, -np.logaddexp(0.0, -logits), -np.inf)
        log_inside = np.where(free, -np.logaddexp(0.0, logits), 0.0)
        log_start[gap], log_inside[gap] = 0.0, 0.0
        inside = np.concatenate([[0.0], np.cumsum(log_inside)])
        gaps = np.concatenate([[0], np.cumsum(gap)])    # no piece may contain whitespace

        pieces = self._lattice(line)                    # dictionary words, then the model's words
        where = np.cumsum([0] + [not c.isspace() for c in text])          # text index -> line index
        best = None
        units: list[str | None] = [*self.units] or [None]
        for v in units:
            pos = 0
            bounds = [0]
            for tok in self.tokenize(text, True, v):
                if not tok.isspace():
                    pieces.add((int(where[pos]), int(where[pos + len(tok)])))
                    bounds.append(int(where[pos + len(tok)]))
                pos += len(tok)
            if v == (unit or self.unit):
                best = tuple(bounds)
        ending: dict[int, list[int]] = {}
        for a, b in pieces:
            ending.setdefault(b, []).append(a)
        # a reading is a linked list of its word ends, (end, previous), shared between readings: memory grows
        # with size x n, not size^2 x n as with one tuple per reading
        paths: dict[int, list[tuple[float, _Node]]] = {0: [(0.0, (0, None))]}
        for b in range(1, size + 1):
            found: list[tuple[float, _Node]] = []
            for a in ending.get(b, []):
                if gaps[b] > gaps[a + 1]:
                    continue
                score = (0.0 if a == 0 else log_start[a]) + inside[b] - inside[a + 1]
                if np.isfinite(score):
                    found += [(s + score, (b, node)) for s, node in paths.get(a, [])]
            if found:
                paths[b] = sorted(found, key=lambda x: -x[0])[:n]
        ranked = [(s, _unroll(node)) for s, node in paths.get(size, [])]
        if best is not None:                            # the tokenize result first, also on exact ties
            ranked = sorted(ranked, key=lambda x: (x[1] != best, -x[0]))
        out = []
        space = [j for j, c in enumerate(text) if c.isspace()]
        for score, path in ranked[:n]:
            cut = {keep[p] for p in path[1:-1]} | set(space) | {j + 1 for j in space}
            marks = [0] + sorted(j for j in cut if 0 < j < len(text)) + [len(text)]
            toks = [text[x:y] for x, y in zip(marks[:-1], marks[1:]) if y > x]
            out.append((toks if keep_whitespace else [t for t in toks if not t.isspace()], float(np.exp(score))))
        return out

    def _lattice(self, line: str) -> set[tuple[int, int]]:
        """(start, end) of every dictionary word in a whitespace-free line (the hashes of :class:`Lexicon`)."""
        c = _codes(line).astype(np.uint64)
        spans: set[tuple[int, int]] = set()
        for n in self.lexicon.lengths:
            m = len(line) - n + 1
            if m <= 0:
                break
            h = c[:m].copy()
            for j in range(1, n):
                h = h * HASH_MUL + c[j:j + m]
            table = self.lexicon.hashes[n]
            hit = table[np.minimum(np.searchsorted(table, h), len(table) - 1)] == h
            spans.update((int(a), int(a) + n) for a in np.flatnonzero(hit))
        return spans
