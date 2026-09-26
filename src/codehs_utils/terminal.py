"""Low-level terminal control: cursor movement, screen clearing, the
alternate screen, keyboard/mouse input, terminal size, and `print_at`/`app`.

Raw terminal mode and signal decoding are handled here; Windows-specific
console API calls live in `._platform` and are used internally.
"""

import os
import sys
import re
import time
import shutil
import select
import atexit
import itertools
import contextlib
from collections import deque
from typing import Callable, Iterator, List, Optional, Tuple, Union

from ._platform import (
    _IS_WINDOWS,
    _win_get_cursor_position,
    _win_get_terminal_size,
    _win_read_bytes,
    _win_enable_vt_output,
    _win_enable_vt_input,
    _win_restore_input_mode,
)
from ._buffer import _write, _flush_pending_frame, frame
from ._pixelbuf import _pixel_buf
from .text import _visible_len
from .geometry import Rect

if not _IS_WINDOWS:
    import termios
    import tty


_cleanup_registered = False
_mouse_on = False
_cursor_hidden = False
_alt_screen_on = False
_cbreak_old = None
_cbreak_failed = False


def _register_cleanup():
    global _cleanup_registered
    if not _cleanup_registered:
        _cleanup_registered = True
        atexit.register(restore_terminal)


def _ensure_cbreak_mode():
    global _cbreak_old, _cbreak_failed
    if _IS_WINDOWS or _cbreak_old is not None or _cbreak_failed:
        return
    try:
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        tty.setcbreak(fd, termios.TCSANOW)
    except (termios.error, OSError, ValueError):
        _cbreak_failed = True
        return
    _cbreak_old = old
    _register_cleanup()


def _restore_cbreak_mode():
    global _cbreak_old
    if _cbreak_old is not None:
        try:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, _cbreak_old)
        except Exception:
            pass
        _cbreak_old = None


@contextlib.contextmanager
def _scoped_cbreak():
    owned = not _IS_WINDOWS and _cbreak_old is None and not _cbreak_failed
    _ensure_cbreak_mode()
    try:
        yield
    finally:
        if owned:
            _restore_cbreak_mode()


def restore_terminal():
    global _mouse_on, _cursor_hidden, _alt_screen_on
    try:
        if _mouse_on:
            _mouse_on = False
            _write("\033[?1000l\033[?1003l\033[?1006l")
            _drain_input()
        if _cursor_hidden:
            _cursor_hidden = False
            _write("\033[?25h")
        if _alt_screen_on:
            _alt_screen_on = False
            _write("\033[?1049l")
        _restore_cbreak_mode()
        if _IS_WINDOWS:
            _win_restore_input_mode()
    except Exception:
        pass


def _drain_input(settle: float = 0.03):
    try:
        if sys.stdin.isatty():
            while _pump(settle):
                pass
    except Exception:
        pass
    _mouse_queue.clear()


_MOUSE_RE = re.compile(rb"\x1b\[<(\d+);(\d+);(\d+)([Mm])")
_CSI_RE = re.compile(rb"\x1b\[[0-?]*[ -/]*[@-~]")
_SS3_RE = re.compile(rb"\x1bO[@-~]")
_ESC_PARTIAL_RE = re.compile(rb"\x1b(?:\[[0-?]*[ -/]*|O)?")
_CPR_RE = re.compile(rb"\x1b\[(\d+);(\d+)R")
_ESC_TIMEOUT = 0.05

_CSI_KEYS = {"A": "UP", "B": "DOWN", "C": "RIGHT", "D": "LEFT", "H": "HOME", "F": "END",
             "P": "F1", "Q": "F2", "R": "F3", "S": "F4"}
_SS3_KEYS = dict(_CSI_KEYS)
_TILDE_KEYS = {"1": "HOME", "2": "INSERT", "3": "DELETE", "4": "END", "5": "PAGEUP",
               "6": "PAGEDOWN", "7": "HOME", "8": "END", "11": "F1", "12": "F2", "13": "F3",
               "14": "F4", "15": "F5", "17": "F6", "18": "F7", "19": "F8", "20": "F9",
               "21": "F10", "23": "F11", "24": "F12"}
_MOUSE_BUTTON_NAMES = {0: "left", 1: "middle", 2: "right", 3: None}

_pending = b""
_incomplete_since = None
_seq = itertools.count()
_key_queue: deque = deque(maxlen=512)
_mouse_queue: deque = deque(maxlen=512)


class MouseEvent:
    __slots__ = ("type", "button", "x", "y", "shift", "alt", "ctrl")
    kind = "mouse"

    def __init__(self, type_: str, button: Optional[str], x: int, y: int,
                 shift: bool = False, alt: bool = False, ctrl: bool = False):
        self.type = type_
        self.button = button
        self.x = x
        self.y = y
        self.shift = shift
        self.alt = alt
        self.ctrl = ctrl

    def inside(self, rect) -> bool:
        return rect.contains(self.x, self.y)

    def __repr__(self):
        mods = "".join(f", {m}=True" for m in ("shift", "alt", "ctrl") if getattr(self, m))
        return f"MouseEvent(type={self.type!r}, button={self.button!r}, x={self.x}, y={self.y}{mods})"


class KeyEvent:
    __slots__ = ("key",)
    kind = "key"
    type = "key"

    def __init__(self, key: str):
        self.key = key

    def __eq__(self, other):
        if isinstance(other, KeyEvent):
            return self.key == other.key
        if isinstance(other, str):
            return self.key == other
        return NotImplemented

    def __hash__(self):
        return hash(self.key)

    def __str__(self):
        return self.key

    def __repr__(self):
        return f"KeyEvent({self.key!r})"


def _parse_mouse_match(m) -> MouseEvent:
    code, x, y, final = int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)
    mods = dict(shift=bool(code & 4), alt=bool(code & 8), ctrl=bool(code & 16))
    if code & 64:
        return MouseEvent(("wheel_up", "wheel_down", "wheel_left", "wheel_right")[code & 3],
                          None, x, y, **mods)
    if code & 128:
        button = ("back", "forward", "button10", "button11")[code & 3]
    else:
        button = _MOUSE_BUTTON_NAMES.get(code & 3)
    if final == b"m":
        return MouseEvent("release", button, x, y, **mods)
    if code & 32:
        return MouseEvent("move", button, x, y, **mods)
    return MouseEvent("press", button, x, y, **mods)


def _decode_csi_key(seq: bytes) -> Optional[str]:
    final = chr(seq[-1])
    params = seq[2:-1].decode("ascii", "ignore").split(";")
    first = params[0]
    if final == "~":
        name = _TILDE_KEYS.get(first)
    elif final == "Z":
        return "SHIFT+TAB"
    elif final in "PQRS":
        name = _CSI_KEYS.get(final) if first in ("", "1") else None
    else:
        name = _CSI_KEYS.get(final)
    if name is None:
        return None
    if len(params) > 1 and params[1].isdigit():
        bits = int(params[1]) - 1
        name = (("SHIFT+" if bits & 1 else "") + ("ALT+" if bits & 2 else "")
                + ("CTRL+" if bits & 4 else "") + name)
    return name


def _parse_one(buf: bytes, flush: bool):
    b0 = buf[0]
    if b0 == 0x1B:
        m = _MOUSE_RE.match(buf)
        if m:
            return "mouse", _parse_mouse_match(m), m.end()
        m = _CSI_RE.match(buf)
        if m:
            name = _decode_csi_key(m.group())
            return ("key", name, m.end()) if name else ("skip", None, m.end())
        m = _SS3_RE.match(buf)
        if m:
            name = _SS3_KEYS.get(chr(m.group()[2]))
            return ("key", name, m.end()) if name else ("skip", None, m.end())
        if not flush and _ESC_PARTIAL_RE.fullmatch(buf):
            return None
        return "key", "ESC", 1
    if b0 < 0x80:
        if b0 in (0x0D, 0x0A):
            return "key", "ENTER", 1
        if b0 in (0x7F, 0x08):
            return "key", "BACKSPACE", 1
        if b0 == 0x09:
            return "key", "TAB", 1
        if 1 <= b0 <= 26:
            return "key", "CTRL+" + chr(b0 + 64), 1
        if b0 < 0x20:
            return "skip", None, 1
        return "key", chr(b0), 1
    if 0xC0 <= b0 <= 0xF7:
        need = 2 if b0 < 0xE0 else 3 if b0 < 0xF0 else 4
        if len(buf) < need:
            return ("skip", None, len(buf)) if flush else None
        try:
            return "key", buf[:need].decode("utf-8"), need
        except UnicodeDecodeError:
            return "skip", None, 1
    return "skip", None, 1


def _parse_pending(flush: bool = False):
    global _pending, _incomplete_since
    while _pending:
        item = _parse_one(_pending, flush)
        if item is None:
            if _incomplete_since is None:
                _incomplete_since = time.monotonic()
            return
        kind, value, used = item
        _pending = _pending[used:]
        if kind == "key":
            _key_queue.append((next(_seq), value))
        elif kind == "mouse":
            _mouse_queue.append((next(_seq), value))
    _incomplete_since = None


def _read_raw(timeout: Optional[float]) -> bytes:
    if _IS_WINDOWS:
        return _win_read_bytes(timeout)
    _ensure_cbreak_mode()
    fd = sys.stdin.fileno()
    if not select.select([fd], [], [], timeout)[0]:
        return b""
    data = os.read(fd, 1024)
    if not data:
        raise EOFError("Standard input was closed.")
    return data


def _pump(timeout: Optional[float]) -> bool:
    global _pending, _incomplete_since
    deadline = None if timeout is None else time.monotonic() + max(0.0, timeout)
    while True:
        now = time.monotonic()
        wait = None if deadline is None else max(0.0, deadline - now)
        if _incomplete_since is not None:
            left = _incomplete_since + _ESC_TIMEOUT - now
            if left <= 0:
                _incomplete_since = None
                _parse_pending(flush=True)
                return True
            wait = left if wait is None else min(wait, left)
        data = _read_raw(wait)
        if data:
            _pending += data
            _incomplete_since = None
            _parse_pending()
            return True
        if deadline is not None and time.monotonic() >= deadline:
            return False


def _wait_for(pop: Callable, timeout: Optional[float]):
    end = None if timeout is None else time.monotonic() + timeout
    while True:
        item = pop()
        if item is not None:
            return item
        remaining = None if end is None else max(0.0, end - time.monotonic())
        _pump(remaining)
        item = pop()
        if item is not None:
            return item
        if end is not None and time.monotonic() >= end:
            return None


def _pop_key() -> Optional[str]:
    return _key_queue.popleft()[1] if _key_queue else None


def _pop_mouse() -> Optional[MouseEvent]:
    return _mouse_queue.popleft()[1] if _mouse_queue else None


def _pop_event():
    if _key_queue and (not _mouse_queue or _key_queue[0][0] < _mouse_queue[0][0]):
        return KeyEvent(_key_queue.popleft()[1])
    return _pop_mouse()


def get_key(timeout: Optional[float] = None) -> str:
    with _scoped_cbreak():
        key = _wait_for(_pop_key, timeout)
    return "" if key is None else key


def get_keys() -> List[str]:
    while _pump(0):
        pass
    keys = [k for _, k in _key_queue]
    _key_queue.clear()
    return keys


def get_key_nonblocking() -> List[str]:
    return get_keys()


def get_mouse_event(timeout: Optional[float] = None) -> Optional[MouseEvent]:
    return _wait_for(_pop_mouse, timeout)


def get_mouse_event_nonblocking() -> Optional[MouseEvent]:
    return get_mouse_event(timeout=0)


def get_event(timeout: Optional[float] = None) -> Optional[Union[KeyEvent, MouseEvent]]:
    return _wait_for(_pop_event, timeout)


def events(timeout: Optional[float] = None) -> Iterator[Optional[Union[KeyEvent, MouseEvent]]]:
    while True:
        yield get_event(timeout)


def _query_cursor_position() -> Tuple[int, int]:
    global _pending
    if _IS_WINDOWS:
        return _win_get_cursor_position()
    _flush_pending_frame()
    fd = sys.stdin.fileno()
    sys.stdout.write("\033[6n")
    sys.stdout.flush()
    deadline = time.monotonic() + 2.0
    buf = b""
    while True:
        left = deadline - time.monotonic()
        if left <= 0 or not select.select([fd], [], [], left)[0]:
            raise TimeoutError("The terminal never answered the cursor-position query.")
        data = os.read(fd, 64)
        if not data:
            raise EOFError("Standard input was closed.")
        buf += data
        m = _CPR_RE.search(buf)
        if m:
            rest = buf[:m.start()] + buf[m.end():]
            if rest:
                _pending += rest
                _parse_pending()
            return int(m.group(1)), int(m.group(2))


gcp = _query_cursor_position


def get_cursor_position() -> Tuple[int, int]:
    if _IS_WINDOWS:
        return _win_get_cursor_position()
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd, termios.TCSANOW)
        return _query_cursor_position()
    finally:
        termios.tcsetattr(fd, termios.TCSANOW, old)


def get_terminal_size() -> Tuple[int, int]:
    if _IS_WINDOWS:
        return _win_get_terminal_size()
    try:
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
    except (OSError, ValueError, termios.error):
        size = shutil.get_terminal_size(fallback=(80, 24))
        return size.columns, size.lines
    try:
        tty.setcbreak(fd, termios.TCSANOW)
        _write("\033[s\033[999;999H")
        height, width = _query_cursor_position()
        _write("\033[u")
        return width, height
    finally:
        termios.tcsetattr(fd, termios.TCSANOW, old)


def clear_screen(scrollback: bool = True):
    _pixel_buf.clear()
    _write("\033[2J\033[H" + ("\033[3J" if scrollback else ""))


def set_cursor_col(col: int):
    _write(f"\033[{col}G")


def set_cursor_row(row: int):
    _write(f"\033[{row}d")


def set_cursor_pos(row: int, col: int):
    _write(f"\033[{row};{col}H")


def move_cursor(dx: int = 0, dy: int = 0):
    out = ""
    if dy < 0:
        out += f"\033[{-dy}A"
    elif dy > 0:
        out += f"\033[{dy}B"
    if dx > 0:
        out += f"\033[{dx}C"
    elif dx < 0:
        out += f"\033[{-dx}D"
    if out:
        _write(out)


def save_cursor_position():
    _write("\0337")


def restore_cursor_position():
    _write("\0338")


def hide_cursor():
    global _cursor_hidden
    _cursor_hidden = True
    _register_cleanup()
    _write("\033[?25l")


def show_cursor():
    global _cursor_hidden
    _cursor_hidden = False
    _write("\033[?25h")


def enter_alt_screen():
    global _alt_screen_on
    _alt_screen_on = True
    _pixel_buf.clear()
    _register_cleanup()
    _write("\033[?1049h")


def leave_alt_screen():
    global _alt_screen_on
    _alt_screen_on = False
    _pixel_buf.clear()
    _write("\033[?1049l")


def clear_line(mode: str = "full"):
    codes = {"full": "2", "to_end": "0", "to_start": "1"}
    if mode not in codes:
        raise ValueError(f"Unknown clear_line mode: '{mode}'. Use 'full', 'to_end', or 'to_start'.")
    _write(f"\033[{codes[mode]}K")


def enable_mouse_tracking():
    global _mouse_on
    if _IS_WINDOWS:
        try:
            _win_enable_vt_output()
            _win_enable_vt_input()
        except Exception:
            pass
    _mouse_on = True
    _register_cleanup()
    _write("\033[?1000h\033[?1003h\033[?1006h")


def disable_mouse_tracking():
    global _mouse_on
    _mouse_on = False
    _write("\033[?1000l\033[?1003l\033[?1006l")
    _drain_input()
    if _IS_WINDOWS:
        _win_restore_input_mode()


def print_at(row: int, col: int, text, clear_to_end: bool = False) -> Rect:
    lines = str(text).split("\n")
    widest = 0
    with frame():
        for i, line in enumerate(lines):
            _write(f"\033[{row + i};{col}H{line}" + ("\033[K" if clear_to_end else ""))
            widest = max(widest, _visible_len(line))
    return Rect(row, col, widest, len(lines))


@contextlib.contextmanager
def app(mouse: bool = False, cursor: bool = False, clear: bool = True,
        alt_screen: bool = True, catch_interrupt: bool = True):
    try:
        if alt_screen:
            enter_alt_screen()
        if clear:
            clear_screen(scrollback=False)
        if not cursor:
            hide_cursor()
        if mouse:
            enable_mouse_tracking()
        yield
    except KeyboardInterrupt:
        if not catch_interrupt:
            raise
    finally:
        restore_terminal()
        _key_queue.clear()
        _mouse_queue.clear()
        if not alt_screen:
            _write("\033[999;1H\r\n")
