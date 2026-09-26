"""Output write buffering: batches writes made inside a `frame()` block into
a single flush to stdout, so multi-line draws don't tear or flicker.

A private implementation detail of :mod:`codehs_utils`, used by
:mod:`codehs_utils.terminal` and :mod:`codehs_utils.geometry`.
"""

import sys
import contextlib
from typing import List

_frame_depth = 0
_frame_buf: List[str] = []


def _flush_pending_frame():
    if _frame_buf:
        data = "".join(_frame_buf)
        _frame_buf.clear()
        sys.stdout.write(data)
        sys.stdout.flush()


def _write(s: str, flush: bool = True):
    if _frame_depth > 0:
        _frame_buf.append(s)
    else:
        sys.stdout.write(s)
        if flush:
            sys.stdout.flush()


@contextlib.contextmanager
def frame(sync: bool = False):
    global _frame_depth
    _frame_depth += 1
    try:
        yield
    finally:
        _frame_depth -= 1
        if _frame_depth == 0 and _frame_buf:
            data = "".join(_frame_buf)
            _frame_buf.clear()
            if sync:
                data = "\033[?2026h" + data + "\033[?2026l"
            sys.stdout.write(data)
            sys.stdout.flush()


def write(*parts, sep: str = "", flush: bool = True):
    _write(sep.join(str(p) for p in parts), flush)
