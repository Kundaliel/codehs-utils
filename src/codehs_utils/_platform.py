"""Windows console API bindings, used internally to provide VT-mode output,
raw key reads, cursor position, and terminal size on Windows.

Everything here is a private implementation detail of :mod:`codehs_utils`;
the public API lives in :mod:`codehs_utils.terminal`.
"""

import os
import time
import shutil
import ctypes
import ctypes.wintypes
from typing import Optional, Tuple

_IS_WINDOWS = os.name == "nt"

if _IS_WINDOWS:
    import msvcrt


class _WinCOORD(ctypes.Structure):
    _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]


class _WinSMALL_RECT(ctypes.Structure):
    _fields_ = [("Left", ctypes.c_short), ("Top", ctypes.c_short),
                ("Right", ctypes.c_short), ("Bottom", ctypes.c_short)]


class _WinCONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
    _fields_ = [("dwSize", _WinCOORD),
                ("dwCursorPosition", _WinCOORD),
                ("wAttributes", ctypes.c_ushort),
                ("srWindow", _WinSMALL_RECT),
                ("dwMaximumWindowSize", _WinCOORD)]


_STD_INPUT, _STD_OUTPUT = -10, -11
_WIN_VT_OUTPUT = 0x0004
_WIN_VT_INPUT = 0x0200
_WIN_QUICK_EDIT = 0x0040
_WIN_EXT_FLAGS = 0x0080
_win_saved_input_mode = None

if _IS_WINDOWS:
    _k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _k32.GetStdHandle.restype = ctypes.wintypes.HANDLE
    _k32.GetStdHandle.argtypes = [ctypes.wintypes.DWORD]
    _k32.GetConsoleMode.restype = ctypes.wintypes.BOOL
    _k32.GetConsoleMode.argtypes = [ctypes.wintypes.HANDLE, ctypes.POINTER(ctypes.wintypes.DWORD)]
    _k32.SetConsoleMode.restype = ctypes.wintypes.BOOL
    _k32.SetConsoleMode.argtypes = [ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD]
    _k32.GetConsoleScreenBufferInfo.restype = ctypes.wintypes.BOOL
    _k32.GetConsoleScreenBufferInfo.argtypes = [ctypes.wintypes.HANDLE,
                                                ctypes.POINTER(_WinCONSOLE_SCREEN_BUFFER_INFO)]


def _win_get_mode(handle) -> Optional[int]:
    mode = ctypes.wintypes.DWORD()
    if _k32.GetConsoleMode(handle, ctypes.byref(mode)):
        return mode.value
    return None


def _win_enable_vt_output():
    handle = _k32.GetStdHandle(_STD_OUTPUT)
    mode = _win_get_mode(handle)
    if mode is not None and not mode & _WIN_VT_OUTPUT:
        _k32.SetConsoleMode(handle, mode | _WIN_VT_OUTPUT)


def _win_enable_vt_input():
    global _win_saved_input_mode
    handle = _k32.GetStdHandle(_STD_INPUT)
    mode = _win_get_mode(handle)
    if mode is None:
        return
    if _win_saved_input_mode is None:
        _win_saved_input_mode = mode
    _k32.SetConsoleMode(handle, (mode | _WIN_VT_INPUT | _WIN_EXT_FLAGS) & ~_WIN_QUICK_EDIT)


def _win_restore_input_mode():
    global _win_saved_input_mode
    if _win_saved_input_mode is not None:
        try:
            _k32.SetConsoleMode(_k32.GetStdHandle(_STD_INPUT), _win_saved_input_mode)
        except Exception:
            pass
        _win_saved_input_mode = None


def _win_console_info():
    handle = _k32.GetStdHandle(_STD_OUTPUT)
    info = _WinCONSOLE_SCREEN_BUFFER_INFO()
    if not _k32.GetConsoleScreenBufferInfo(handle, ctypes.byref(info)):
        return None
    return info


def _win_get_cursor_position() -> Tuple[int, int]:
    info = _win_console_info()
    if info is None:
        raise OSError("Cannot read the cursor position: stdout is not a console.")
    row = info.dwCursorPosition.Y - info.srWindow.Top + 1
    col = info.dwCursorPosition.X - info.srWindow.Left + 1
    return row, col


def _win_get_terminal_size() -> Tuple[int, int]:
    info = _win_console_info()
    if info is not None:
        width = info.srWindow.Right - info.srWindow.Left + 1
        height = info.srWindow.Bottom - info.srWindow.Top + 1
        if width > 0 and height > 0:
            return width, height
    size = shutil.get_terminal_size(fallback=(80, 24))
    return size.columns, size.lines


_WIN_EXT_MAP = {
    "H": b"\x1b[A", "P": b"\x1b[B", "M": b"\x1b[C", "K": b"\x1b[D",
    "G": b"\x1b[H", "O": b"\x1b[F", "R": b"\x1b[2~", "S": b"\x1b[3~",
    "I": b"\x1b[5~", "Q": b"\x1b[6~",
    ";": b"\x1bOP", "<": b"\x1bOQ", "=": b"\x1bOR", ">": b"\x1bOS",
    "?": b"\x1b[15~", "@": b"\x1b[17~", "A": b"\x1b[18~", "B": b"\x1b[19~",
    "C": b"\x1b[20~", "D": b"\x1b[21~", "\x85": b"\x1b[23~", "\x86": b"\x1b[24~",
}


def _win_read_bytes(timeout=None):
    start = time.monotonic()
    while not msvcrt.kbhit():
        if timeout is not None and (time.monotonic() - start) >= timeout:
            return b""
        time.sleep(0.005)
    out = b""
    while msvcrt.kbhit() and len(out) < 1024:
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):
            out += _WIN_EXT_MAP.get(msvcrt.getwch(), b"")
            continue
        if "\ud800" <= ch <= "\udbff":
            try:
                ch = (ch + msvcrt.getwch()).encode("utf-16", "surrogatepass").decode("utf-16")
            except Exception:
                continue
        out += ch.encode("utf-8", errors="ignore")
    return out


if _IS_WINDOWS:
    try:
        _win_enable_vt_output()
    except Exception:
        pass
