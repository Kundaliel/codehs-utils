

from typing import Dict, List, Optional, Sequence, Tuple, Union

from .colors import (
    ColorLike, ColorText, GradientText, ColorSpec, GradientColors,
    _STYLE_CODES, _validate_styles,
)
from .text import align_text

_LOWER_HALF = "\u2584"

RGB = Tuple[int, int, int]


FONT_3X5: Dict[str, str] = {
    " ": "...\n...\n...\n...\n...",
    "0": "###\n#.#\n#.#\n#.#\n###",
    "1": ".#.\n##.\n.#.\n.#.\n###",
    "2": "###\n..#\n###\n#..\n###",
    "3": "###\n..#\n###\n..#\n###",
    "4": "#.#\n#.#\n###\n..#\n..#",
    "5": "###\n#..\n###\n..#\n###",
    "6": "###\n#..\n###\n#.#\n###",
    "7": "###\n..#\n..#\n..#\n..#",
    "8": "###\n#.#\n###\n#.#\n###",
    "9": "###\n#.#\n###\n..#\n###",
    "A": ".#.\n#.#\n###\n#.#\n#.#",
    "B": "##.\n#.#\n##.\n#.#\n##.",
    "C": ".##\n#..\n#..\n#..\n.##",
    "D": "##.\n#.#\n#.#\n#.#\n##.",
    "E": "###\n#..\n##.\n#..\n###",
    "F": "###\n#..\n##.\n#..\n#..",
    "G": ".##\n#..\n#.#\n#.#\n.##",
    "H": "#.#\n#.#\n###\n#.#\n#.#",
    "I": "###\n.#.\n.#.\n.#.\n###",
    "J": "..#\n..#\n..#\n#.#\n.#.",
    "K": "#.#\n#.#\n##.\n#.#\n#.#",
    "L": "#..\n#..\n#..\n#..\n###",
    "M": "#.#\n###\n#.#\n#.#\n#.#",
    "N": "#.#\n##.\n#.#\n.##\n#.#",
    "O": ".#.\n#.#\n#.#\n#.#\n.#.",
    "P": "##.\n#.#\n##.\n#..\n#..",
    "Q": ".#.\n#.#\n#.#\n##.\n.##",
    "R": "##.\n#.#\n##.\n#.#\n#.#",
    "S": ".##\n#..\n.#.\n..#\n##.",
    "T": "###\n.#.\n.#.\n.#.\n.#.",
    "U": "#.#\n#.#\n#.#\n#.#\n.#.",
    "V": "#.#\n#.#\n#.#\n.#.\n.#.",
    "W": "#.#\n#.#\n#.#\n###\n#.#",
    "X": "#.#\n#.#\n.#.\n#.#\n#.#",
    "Y": "#.#\n#.#\n.#.\n.#.\n.#.",
    "Z": "###\n..#\n.#.\n#..\n###",
    ".": "...\n...\n...\n...\n.#.",
    ",": "...\n...\n...\n.#.\n#..",
    ":": "...\n.#.\n...\n.#.\n...",
    ";": "...\n.#.\n...\n.#.\n#..",
    "!": ".#.\n.#.\n.#.\n...\n.#.",
    "?": "##.\n..#\n.#.\n...\n.#.",
    "-": "...\n...\n###\n...\n...",
    "+": "...\n.#.\n###\n.#.\n...",
    "=": "...\n###\n...\n###\n...",
    '"': "
    "#": "#.#\n###\n#.#\n###\n#.#",
    "$": ".#.\n##.\n.#.\n.##\n.#.",
    "%": "#.#\n..#\n.#.\n#..\n#.#",
    "&": ".#.\n#.#\n.#.\n#.#\n.##",
    "'": ".#.\n.#.\n...\n...\n...",
    "(": ".#.\n#..\n#..\n#..\n.#.",
    ")": ".#.\n..#\n..#\n..#\n.#.",
    "*": "...\n#.#\n.#.\n#.#\n...",
    "/": "..#\n..#\n.#.\n#..\n#..",
    "<": "..#\n.#.\n#..\n.#.\n..#",
    ">": "#..\n.#.\n..#\n.#.\n#..",
    "@": ".#.\n#.#\n#.#\n#..\n.##",
    "[": "##.\n#..\n#..\n#..\n##.",
    "\\": "
    "]": ".##\n..#\n..#\n..#\n.##",
    "^": ".#.\n#.#\n...\n...\n...",
    "_": "...\n...\n...\n...\n###",
    "`": "#..\n.#.\n...\n...\n...",
    "{": ".##\n.#.\n#..\n.#.\n.##",
    "|": ".#.\n.#.\n.#.\n.#.\n.#.",
    "}": "##.\n.#.\n..#\n.#.\n##.",
    "~": "...\n.##\n##.\n...\n...",
}

FONT_5X7: Dict[str, str] = {
    " ": ".....\n.....\n.....\n.....\n.....\n.....\n.....",
    "0": ".###.\n#...#\n#..##\n#.#.#\n##..#\n#...#\n.###.",
    "1": "..#..\n.##..\n..#..\n..#..\n..#..\n..#..\n.###.",
    "2": ".###.\n#...#\n....#\n...#.\n..#..\n.#...\n#####",
    "3": ".###.\n#...#\n....#\n..##.\n....#\n#...#\n.###.",
    "4": "...#.\n..##.\n.#.#.\n#..#.\n#####\n...#.\n...#.",
    "5": "#####\n#....\n####.\n....#\n....#\n#...#\n.###.",
    "6": "..##.\n.#...\n#....\n####.\n#...#\n#...#\n.###.",
    "7": "#####\n....#\n...#.\n..#..\n.#...\n.#...\n.#...",
    "8": ".###.\n#...#\n#...#\n.###.\n#...#\n#...#\n.###.",
    "9": ".###.\n#...#\n#...#\n.####\n....#\n...#.\n.##..",
    "A": "..#..\n.#.#.\n#...#\n#...#\n#####\n#...#\n#...#",
    "B": "####.\n#...#\n#...#\n####.\n#...#\n#...#\n####.",
    "C": ".####\n#....\n#....\n#....\n#....\n#....\n.####",
    "D": "####.\n#...#\n#...#\n#...#\n#...#\n#...#\n####.",
    "E": "#####\n#....\n#....\n####.\n#....\n#....\n#####",
    "F": "#####\n#....\n#....\n####.\n#....\n#....\n#....",
    "G": ".####\n#....\n#....\n#.###\n#...#\n#...#\n.####",
    "H": "#...#\n#...#\n#...#\n#####\n#...#\n#...#\n#...#",
    "I": "#####\n..#..\n..#..\n..#..\n..#..\n..#..\n#####",
    "J": "..###\n...#.\n...#.\n...#.\n...#.\n#..#.\n.##..",
    "K": "#...#\n#..#.\n#.#..\n##...\n#.#..\n#..#.\n#...#",
    "L": "#....\n#....\n#....\n#....\n#....\n#....\n#####",
    "M": "#...#\n##.##\n#.#.#\n#...#\n#...#\n#...#\n#...#",
    "N": "#...#\n##..#\n#.#.#\n#..##\n#...#\n#...#\n#...#",
    "O": ".###.\n#...#\n#...#\n#...#\n#...#\n#...#\n.###.",
    "P": "####.\n#...#\n#...#\n####.\n#....\n#....\n#....",
    "Q": ".###.\n#...#\n#...#\n#...#\n#.#.#\n#..#.\n.##.#",
    "R": "####.\n#...#\n#...#\n####.\n#.#..\n#..#.\n#...#",
    "S": ".####\n#....\n#....\n.###.\n....#\n....#\n####.",
    "T": "#####\n..#..\n..#..\n..#..\n..#..\n..#..\n..#..",
    "U": "#...#\n#...#\n#...#\n#...#\n#...#\n#...#\n.###.",
    "V": "#...#\n#...#\n#...#\n#...#\n#...#\n.#.#.\n..#..",
    "W": "#...#\n#...#\n#...#\n#.#.#\n#.#.#\n##.##\n#...#",
    "X": "#...#\n.#.#.\n..#..\n..#..\n..#..\n.#.#.\n#...#",
    "Y": "#...#\n.#.#.\n..#..\n..#..\n..#..\n..#..\n..#..",
    "Z": "#####\n....#\n...#.\n..#..\n.#...\n#....\n#####",
    ".": ".....\n.....\n.....\n.....\n.....\n.##..\n.##..",
    ",": ".....\n.....\n.....\n.....\n.....\n..#..\n.#...",
    ":": ".....\n.##..\n.##..\n.....\n.##..\n.##..\n.....",
    ";": ".....\n.##..\n.##..\n.....\n.##..\n.#...\n#....",
    "!": "..#..\n..#..\n..#..\n..#..\n..#..\n.....\n..#..",
    "?": ".###.\n#...#\n....#\n..##.\n..#..\n.....\n..#..",
    "-": ".....\n.....\n.....\n#####\n.....\n.....\n.....",
    "+": ".....\n..#..\n..#..\n#####\n..#..\n..#..\n.....",
    "=": ".....\n.....\n#####\n.....\n#####\n.....\n.....",
    '"': "
    "#": ".#.#.\n.#.#.\n#####\n.#.#.\n#####\n.#.#.\n.#.#.",
    "$": "..#..\n.####\n#.#..\n.###.\n..#.#\n####.\n..#..",
    "%": "##..#\n##.#.\n...#.\n..#..\n.#...\n.#.##\n#..##",
    "&": ".##..\n#..#.\n#.#..\n.#...\n#.#.#\n#..#.\n.##.#",
    "'": ".#...\n.#...\n.....\n.....\n.....\n.....\n.....",
    "(": "...#.\n..#..\n.#...\n.#...\n.#...\n..#..\n...#.",
    ")": ".#...\n..#..\n...#.\n...#.\n...#.\n..#..\n.#...",
    "*": ".....\n#.#.#\n.###.\n#####\n.###.\n#.#.#\n.....",
    "/": "....#\n...#.\n..#..\n..#..\n..#..\n.#...\n#....",
    "<": "...#.\n..#..\n.#...\n#....\n.#...\n..#..\n...#.",
    ">": ".#...\n..#..\n...#.\n....#\n...#.\n..#..\n.#...",
    "@": ".###.\n#...#\n#.###\n#.#.#\n#.###\n#....\n.####",
    "[": ".###.\n.#...\n.#...\n.#...\n.#...\n.#...\n.###.",
    "\\": "
    "]": ".###.\n...#.\n...#.\n...#.\n...#.\n...#.\n.###.",
    "^": "..#..\n.#.#.\n#...#\n.....\n.....\n.....\n.....",
    "_": ".....\n.....\n.....\n.....\n.....\n.....\n#####",
    "`": ".#...\n..#..\n.....\n.....\n.....\n.....\n.....",
    "{": "..##.\n..#..\n..#..\n.#...\n..#..\n..#..\n..##.",
    "|": "..#..\n..#..\n..#..\n..#..\n..#..\n..#..\n..#..",
    "}": ".##..\n..#..\n..#..\n...#.\n..#..\n..#..\n.##..",
    "~": ".....\n.....\n.#...\n#.#.#\n...#.\n.....\n.....",
}

FONT_5X7_LOWER: Dict[str, str] = {
    "a": ".....\n.....\n.###.\n....#\n.####\n#...#\n.####",
    "b": "#....\n#....\n####.\n#...#\n#...#\n#...#\n####.",
    "c": ".....\n.....\n.###.\n#....\n#....\n#...#\n.###.",
    "d": "....#\n....#\n.####\n#...#\n#...#\n#...#\n.####",
    "e": ".....\n.....\n.###.\n#...#\n#####\n#....\n.###.",
    "f": "..##.\n.#..#\n.#...\n###..\n.#...\n.#...\n.#...",
    "g": ".....\n.....\n.####\n#...#\n#...#\n.####\n....#\n.###.",
    "h": "#....\n#....\n####.\n#...#\n#...#\n#...#\n#...#",
    "i": "..#..\n.....\n.##..\n..#..\n..#..\n..#..\n.###.",
    "j": "...#.\n.....\n..##.\n...#.\n...#.\n...#.\n#..#.\n.##..",
    "k": "#....\n#....\n#..#.\n#.#..\n##...\n#.#..\n#..#.",
    "l": ".##..\n..#..\n..#..\n..#..\n..#..\n..#..\n.###.",
    "m": ".....\n.....\n##.#.\n#.#.#\n#.#.#\n#...#\n#...#",
    "n": ".....\n.....\n####.\n#...#\n#...#\n#...#\n#...#",
    "o": ".....\n.....\n.###.\n#...#\n#...#\n#...#\n.###.",
    "p": ".....\n.....\n####.\n#...#\n#...#\n####.\n#....\n#....",
    "q": ".....\n.....\n.####\n#...#\n#...#\n.####\n....#\n....#",
    "r": ".....\n.....\n#.##.\n##..#\n#....\n#....\n#....",
    "s": ".....\n.....\n.####\n#....\n.###.\n....#\n####.",
    "t": ".#...\n.#...\n###..\n.#...\n.#...\n.#..#\n..##.",
    "u": ".....\n.....\n#...#\n#...#\n#...#\n#..##\n.##.#",
    "v": ".....\n.....\n#...#\n#...#\n#...#\n.#.#.\n..#..",
    "w": ".....\n.....\n#...#\n#...#\n#.#.#\n#.#.#\n.#.#.",
    "x": ".....\n.....\n#...#\n.#.#.\n..#..\n.#.#.\n#...#",
    "y": ".....\n.....\n#...#\n#...#\n#...#\n.####\n....#\n.###.",
    "z": ".....\n.....\n#####\n...#.\n..#..\n.#...\n#####",
}

FONT_5X7.update(FONT_5X7_LOWER)

_FONTS: Dict[str, Tuple[int, int, Dict[str, str]]] = {
    "3x5": (3, 5, FONT_3X5),
    "5x7": (5, 8, FONT_5X7),
}


def _get_font(name: str) -> Tuple[int, int, Dict[str, str]]:
    key = str(name).strip().lower()
    if key not in _FONTS:
        raise ValueError(f"Unknown font: '{name}'. Available fonts: {', '.join(sorted(_FONTS))}")
    return _FONTS[key]


def _validate_font(width: int, height: int, glyphs: Dict[str, str]) -> None:
    for ch, spec in glyphs.items():
        rows = spec.split("\n")
        if not 1 <= len(rows) <= height or any(len(row) != width or set(row) - {"#", "."} for row in rows):
            raise AssertionError(f"Malformed {width}x{height} glyph for {ch!r}: {spec!r}")


for _w, _h, _glyphs in _FONTS.values():
    _validate_font(_w, _h, _glyphs)
del _w, _h, _glyphs


def _glyph_rows(font_dict: Dict[str, str], height: int, ch: str) -> List[str]:
    spec = font_dict.get(ch)
    if spec is None:
        spec = font_dict.get(ch.upper())
    if spec is None:
        spec = font_dict[" "]
    rows = spec.split("\n")
    if len(rows) < height:
        rows += ["." * len(rows[0])] * (height - len(rows))
    return rows


def _resolve_gradient(spec: Optional[GradientColors]) -> List[ColorLike]:
    if not spec:
        return []
    return GradientText()._resolve_colors(spec)


def _lerp_color(colors: List[ColorLike], t: float) -> RGB:
    n = len(colors)
    if n == 1:
        return colors[0].rgb
    pos = t * (n - 1)
    seg = min(int(pos), n - 2)
    local_t = pos - seg
    r1, g1, b1 = colors[seg].rgb
    r2, g2, b2 = colors[seg + 1].rgb
    return (
        round(r1 + (r2 - r1) * local_t),
        round(g1 + (g2 - g1) * local_t),
        round(b1 + (b2 - b1) * local_t),
    )


class LargeText:


    FORMATS = ("block", "pixel")

    def __init__(
        self,
        text: str = "",
        font: str = "5x7",
        format: str = "block",
        color: Union[ColorLike, str, tuple, None] = None,
        colors: Optional[GradientColors] = None,
        background: Union[ColorLike, str, tuple, None] = None,
        background_colors: Optional[GradientColors] = None,
        styles: Optional[Sequence[str]] = None,
        spacing: int = 1,
        cell_width: int = 2,
    ):
        self.text = "" if text is None else str(text)

        self.font_name = str(font).strip().lower()
        self._glyph_w, self._glyph_h, self._font_dict = _get_font(self.font_name)

        if format not in self.FORMATS:
            raise ValueError(f"Unknown format: '{format}'. Use one of: {', '.join(self.FORMATS)}")
        self.format = format

        self.color = ColorLike(color) if color is not None else None
        self.colors: List[ColorLike] = _resolve_gradient(colors)
        self.background = ColorLike(background) if background is not None else None
        self.background_colors: List[ColorLike] = _resolve_gradient(background_colors)
        self.styles: List[str] = _validate_styles(styles) if styles else []

        self.spacing = max(0, int(spacing))
        self.cell_width = max(1, int(cell_width))

    @classmethod
    def supported_chars(cls, font: str = "5x7") -> str:

        _, _, glyphs = _get_font(font)
        return "".join(sorted(ch for ch in glyphs if ch != " "))


    def set_text(self, text: str = ""):
        self.text = "" if text is None else str(text)
        return self

    def set_color(self, col: Union[ColorLike, str, tuple, None] = None):

        self.color = ColorLike(col) if col is not None else None
        return self

    def set_colors(self, colors: Optional[GradientColors] = None):

        self.colors = _resolve_gradient(colors)
        return self

    def set_background(self, col: Union[ColorLike, str, tuple, None] = None):

        self.background = ColorLike(col) if col is not None else None
        return self

    def set_background_colors(self, colors: Optional[GradientColors] = None):

        self.background_colors = _resolve_gradient(colors)
        return self

    def set_background_gradient(self, colors: Optional[GradientColors] = None):

        return self.set_background_colors(colors)

    def set_styles(self, *styles: str):
        if len(styles) == 1 and isinstance(styles[0], (list, tuple)):
            styles = tuple(styles[0])
        self.styles = _validate_styles(styles)
        return self

    def add_style(self, style: str):
        key = _validate_styles([style])[0]
        if key not in self.styles:
            self.styles.append(key)
        return self

    def remove_style(self, style: str):
        key = str(style).strip().lower()
        if key in self.styles:
            self.styles.remove(key)
        return self

    def bold(self):
        return self.add_style("bold")

    def italic(self):
        return self.add_style("italic")

    def underline(self):
        return self.add_style("underline")

    def strikethrough(self):
        return self.add_style("strikethrough")

    def dim(self):
        return self.add_style("dim")

    def blink(self):
        return self.add_style("blink")

    def reverse(self):
        return self.add_style("reverse")


    def _fg_at(self, col: int, total: int) -> Optional[RGB]:
        if self.colors:
            t = col / (total - 1) if total > 1 else 0.0
            return _lerp_color(self.colors, t)
        return self.color.rgb if self.color is not None else None

    def _bg_at(self, col: int, total: int) -> Optional[RGB]:
        if self.background_colors:
            t = col / (total - 1) if total > 1 else 0.0
            return _lerp_color(self.background_colors, t)
        return self.background.rgb if self.background is not None else None


    def _grid(self) -> List[List[bool]]:

        rows: List[List[bool]] = [[] for _ in range(self._glyph_h)]
        for i, ch in enumerate(self.text):
            if i > 0 and self.spacing:
                for r in rows:
                    r.extend([False] * self.spacing)
            glyph_rows = _glyph_rows(self._font_dict, self._glyph_h, ch)
            for r, glyph_row in zip(rows, glyph_rows):
                r.extend(c == "#" for c in glyph_row)
        return rows


    def _solid(self, width: int, fg: Optional[RGB]) -> str:

        if fg is None:
            styles = list(self.styles) + ["reverse"]
            return str(ColorText(" " * width, styles=styles))
        return str(ColorText(" " * width, background=fg, styles=self.styles))

    def _render_block(self, grid: List[List[bool]], total: int) -> str:
        lines = []
        for row in grid:
            parts = []
            for c in range(total):
                if row[c]:
                    fg = self._fg_at(c, total)
                    parts.append(self._solid(self.cell_width, fg))
                else:
                    bg = self._bg_at(c, total)
                    if bg is not None:
                        parts.append(str(ColorText(" " * self.cell_width, background=bg)))
                    else:
                        parts.append(" " * self.cell_width)
            lines.append("".join(parts))
        return "\n".join(lines)

    def _render_pixel(self, grid: List[List[bool]], total: int) -> str:
        height = len(grid)
        lines = []
        r = 0
        while r < height:
            top = grid[r]
            bottom_real = r + 1 < height
            bottom = grid[r + 1] if bottom_real else [False] * total
            parts = []
            for c in range(total):
                top_on, bottom_on = top[c], bottom[c]
                fg = self._fg_at(c, total)
                bg = self._bg_at(c, total)
                if top_on and bottom_on:
                    parts.append(self._solid(1, fg))
                elif top_on:
                    b = bg if bottom_real else None
                    styles = list(self.styles)
                    if "reverse" not in styles:
                        styles.append("reverse")
                    parts.append(str(ColorText(_LOWER_HALF, foreground=fg, background=b, styles=styles)))
                elif bottom_on:
                    parts.append(str(ColorText(_LOWER_HALF, foreground=fg, background=bg, styles=self.styles)))
                elif bg is not None:
                    parts.append(str(ColorText(" ", background=bg)))
                else:
                    parts.append(" ")
            lines.append("".join(parts))
            r += 2
        return "\n".join(lines)

    def render(self) -> str:
        if not self.text:
            return ""
        grid = self._grid()
        total = len(grid[0])
        if total == 0:
            return ""
        if self.format == "pixel":
            return self._render_pixel(grid, total)
        return self._render_block(grid, total)

    def __str__(self) -> str:
        return self.render()

    def __repr__(self) -> str:
        return f"LargeText(text={self.text!r}, font={self.font_name!r}, format={self.format!r})"


    @property
    def width(self) -> int:
        if not self.text:
            return 0
        cols = len(self.text) * self._glyph_w + (len(self.text) - 1) * self.spacing
        return cols * (self.cell_width if self.format == "block" else 1)

    @property
    def height(self) -> int:
        if self.format == "pixel":
            return (self._glyph_h + 1) // 2
        return self._glyph_h


    def _clone(self, text: str) -> "LargeText":
        return LargeText(
            text=text,
            font=self.font_name,
            format=self.format,
            color=self.color,
            colors=self.colors or None,
            background=self.background,
            background_colors=self.background_colors or None,
            styles=self.styles or None,
            spacing=self.spacing,
            cell_width=self.cell_width,
        )

    def wrap(self, width: int) -> str:

        width = max(1, int(width))
        char_w = self._glyph_w * (self.cell_width if self.format == "block" else 1)
        spacing_w = self.spacing * (self.cell_width if self.format == "block" else 1)

        lines: List[str] = []
        current = ""
        current_w = 0
        for ch in self.text:
            add = char_w if not current else char_w + spacing_w
            if current and current_w + add > width:
                lines.append(current)
                current, current_w = ch, char_w
            else:
                current += ch
                current_w += add
        if current:
            lines.append(current)

        return "\n".join(self._clone(line).render() for line in lines)

    def align(self, width: int, align: str = "left", fillchar: Optional[str] = None) -> str:

        rendered = self.render()
        lines = [align_text(line, width, align=align, fillchar=fillchar) for line in rendered.split("\n")]
        return "\n".join(lines)

    def draw(self, row: int, col: int):
        from .terminal import print_at
        return print_at(row, col, self.render())