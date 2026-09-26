"""ANSI-aware text measurement, wrapping, and alignment.

These helpers treat ANSI SGR escape codes as zero-width, and measure
wide (e.g. CJK) characters as width 2, so wrapping/alignment stays correct
on styled or gradient text. Has no dependency on any other module in this
package, since almost every other module depends on it.
"""

import re
import unicodedata
from typing import List

_ANSI_ESCAPE_RE = re.compile(r'\033\[[0-9;]*m')


def _tokenize_ansi(s: str):
    items = []
    pos = 0
    for m in _ANSI_ESCAPE_RE.finditer(s):
        for ch in s[pos:m.start()]:
            items.append(('char', ch))
        items.append(('ansi', m.group()))
        pos = m.end()
    for ch in s[pos:]:
        items.append(('char', ch))
    return items


def _char_width(ch: str) -> int:
    o = ord(ch)
    if o < 32 or 0x7F <= o < 0xA0:
        return 0
    if o < 0x300:
        return 1
    if unicodedata.category(ch) in ("Mn", "Me", "Cf"):
        return 0
    return 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1


def _visible_len(s: str) -> int:
    plain = _ANSI_ESCAPE_RE.sub('', s)
    if plain.isascii() and plain.isprintable():
        return len(plain)
    return sum(_char_width(ch) for ch in plain)


def _is_reset(code: str) -> bool:
    return code[2:-1].split(";")[0] in ("", "0", "00")


def _apply_sgr(active: List[str], code: str):
    if _is_reset(code):
        active.clear()
        if len(code[2:-1].split(";")) > 1:
            active.append(code)
    else:
        active.append(code)


class _LineBuilder:
    def __init__(self):
        self.lines: List[str] = []
        self.cur: List[str] = []
        self.cur_w = 0
        self.has_text = False
        self.active: List[str] = []

    def ansi(self, code: str):
        self.cur.append(code)
        _apply_sgr(self.active, code)

    def char(self, ch: str, width: int):
        self.cur.append(ch)
        self.cur_w += width
        self.has_text = True

    def items(self, word):
        for kind, val in word:
            if kind == 'ansi':
                self.ansi(val)
            else:
                self.char(val, _char_width(val))

    def newline(self, final: bool = False):
        line = "".join(self.cur) if self.has_text else ""
        if self.has_text and self.active and not final:
            line += "\033[0m"
        self.lines.append(line)
        self.cur = [] if final else list(self.active)
        self.cur_w = 0
        self.has_text = False


def wrap_text(text, width, collapse_space=True, break_long_words=True, preserve_newlines=True):
    s = str(text)
    width = max(1, int(width))
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    if not preserve_newlines:
        s = s.replace("\n", " ")
    if not collapse_space:
        s = s.replace("\t", "    ")
    items = _tokenize_ansi(s)
    lb = _LineBuilder()

    if not collapse_space:
        for kind, val in items:
            if kind == 'ansi':
                lb.ansi(val)
            elif val == "\n":
                lb.newline()
            else:
                cw = _char_width(val)
                if cw and lb.cur_w > 0 and lb.cur_w + cw > width:
                    lb.newline()
                lb.char(val, cw)
        lb.newline(final=True)
        return "\n".join(lb.lines)

    words = []
    cur = []
    for kind, val in items:
        if kind == 'char' and val == "\n":
            if cur:
                words.append(cur)
                cur = []
            words.append(None)
        elif kind == 'char' and val.isspace():
            if cur:
                words.append(cur)
                cur = []
        else:
            cur.append((kind, val))
    if cur:
        words.append(cur)

    def place(word, wlen):
        if wlen > width and break_long_words:
            for kind, val in word:
                if kind == 'ansi':
                    lb.ansi(val)
                else:
                    cw = _char_width(val)
                    if cw and lb.cur_w > 0 and lb.cur_w + cw > width:
                        lb.newline()
                    lb.char(val, cw)
        else:
            lb.items(word)

    for word in words:
        if word is None:
            lb.newline()
            continue
        wlen = sum(_char_width(v) for k, v in word if k == 'char')
        if wlen == 0:
            lb.items(word)
        elif lb.cur_w == 0:
            place(word, wlen)
        elif lb.cur_w + 1 + wlen <= width:
            lb.char(" ", 1)
            lb.items(word)
        else:
            lb.newline()
            place(word, wlen)
    lb.newline(final=True)
    return "\n".join(lb.lines)


def align_text(text, width: int, align: str = "left", fillchar: str = " ") -> str:
    if align not in ("left", "right", "center", "justify"):
        raise ValueError(
            f"Unknown align mode: '{align}'. Use 'left', 'right', 'center', or 'justify'."
        )
    if len(fillchar) != 1:
        raise ValueError("fillchar must be a single character.")
    out = []
    for line in str(text).split("\n"):
        pad = max(0, width - _visible_len(line))
        if align == "left":
            out.append(line + fillchar * pad)
        elif align == "right":
            out.append(fillchar * pad + line)
        elif align == "center":
            left = pad // 2
            out.append(fillchar * left + line + fillchar * (pad - left))
        else:
            words = [w for w in line.split(" ") if w]
            gaps = len(words) - 1
            space = width - sum(_visible_len(w) for w in words)
            if gaps <= 0 or space < gaps:
                out.append(line + fillchar * pad)
                continue
            base, extra = divmod(space, gaps)
            pieces = []
            for i, word in enumerate(words):
                pieces.append(word)
                if i < gaps:
                    pieces.append(fillchar * (base + (1 if i < extra else 0)))
            out.append("".join(pieces))
    return "\n".join(out)
