"""Big, multi-row "banner" text rendered from a small pixel font (3x5 or
5x7), with the same color/gradient/style support as `ColorText` and
`GradientText`.

Two render formats:
  - "block" (default): each font pixel becomes `cell_width` (default 2)
    terminal characters wide, one terminal row per font row. Simple,
    chunky, and works everywhere.
  - "pixel": packs two font rows into a single terminal row using
    half-block characters -- the same trick the half-block pixel canvas
    (`set_pixel`) uses -- so the result comes out roughly half as tall
    for the same size, with squarer-looking pixels.

Font glyphs are stored as one flat "#"/"." string per character (rows
joined with "\\n") rather than nested lists, to keep this file small.
"""

from typing import Dict, List, Optional, Sequence, Tuple, Union

from .colors import (
    ColorLike, ColorText, GradientText, ColorSpec, GradientColors,
    _STYLE_CODES, _validate_styles,
)
from .text import align_text

_UPPER_HALF = "\u2580"  # ▀
_LOWER_HALF = "\u2584"  # ▄

RGB = Tuple[int, int, int]

# --------------------------------------------------------------------- #
# Font data: one "#"/"." string per glyph (rows joined by "\n"), covering
# the full printable ASCII range (32-126: space, digits, punctuation, and
# A-Z -- lowercase is folded to the same glyph as its uppercase letter,
# since these fonts are too small to draw distinct lowercase forms).
# Characters outside 32-126 fall back to a blank (space-width) glyph
# rather than raising, so stray unicode never crashes a render.
# --------------------------------------------------------------------- #

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
    '"': "#.#\n#.#\n...\n...\n...",
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
    "\\": "#..\n#..\n.#.\n..#\n..#",
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
    '"': "#.#..\n#.#..\n.....\n.....\n.....\n.....\n.....",
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
    "\\": "#....\n.#...\n..#..\n..#..\n..#..\n...#.\n....#",
    "]": ".###.\n...#.\n...#.\n...#.\n...#.\n...#.\n.###.",
    "^": "..#..\n.#.#.\n#...#\n.....\n.....\n.....\n.....",
    "_": ".....\n.....\n.....\n.....\n.....\n.....\n#####",
    "`": ".#...\n..#..\n.....\n.....\n.....\n.....\n.....",
    "{": "..##.\n..#..\n..#..\n.#...\n..#..\n..#..\n..##.",
    "|": "..#..\n..#..\n..#..\n..#..\n..#..\n..#..\n..#..",
    "}": ".##..\n..#..\n..#..\n...#.\n..#..\n..#..\n.##..",
    "~": ".....\n.....\n.#...\n#.#.#\n...#.\n.....\n.....",
}

_FONTS: Dict[str, Tuple[int, int, Dict[str, str]]] = {
    "3x5": (3, 5, FONT_3X5),
    "5x7": (5, 7, FONT_5X7),
}


def _get_font(name: str) -> Tuple[int, int, Dict[str, str]]:
    key = str(name).strip().lower()
    if key not in _FONTS:
        raise ValueError(f"Unknown font: '{name}'. Available fonts: {', '.join(sorted(_FONTS))}")
    return _FONTS[key]


def _validate_font(width: int, height: int, glyphs: Dict[str, str]) -> None:
    for ch, spec in glyphs.items():
        rows = spec.split("\n")
        if len(rows) != height or any(len(row) != width for row in rows):
            raise AssertionError(f"Malformed {width}x{height} glyph for {ch!r}: {spec!r}")


for _w, _h, _glyphs in _FONTS.values():
    _validate_font(_w, _h, _glyphs)
del _w, _h, _glyphs


def _glyph_rows(font_dict: Dict[str, str], height: int, ch: str) -> List[str]:
    spec = font_dict.get(ch.upper())
    if spec is None:
        spec = font_dict[" "]
    return spec.split("\n")


def _resolve_gradient(spec: Optional[GradientColors]) -> List[ColorLike]:
    if not spec:
        return []
    # Reuses GradientText's own preset table/parsing (rainbow, fire, ...)
    # instead of duplicating it here.
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
    """Big, multi-row text rendered from a pixel font.

        >>> print(LargeText("HI"))
        >>> print(LargeText("HI", font="3x5", format="pixel", colors="rainbow"))
        >>> print(LargeText("WARN", color="red", styles=["bold"]).align(40, "center"))

    `color`/`colors` paint the "on" pixels (the glyph strokes); `background`/
    `background_colors` fill the "off" pixels within the text's bounding
    box, like a highlighted banner. Any of the four may be a single color
    or a gradient (a preset name like `"rainbow"`, or a list of colors).

    Covers the full printable ASCII range (32-126). Letters are
    case-insensitive -- lowercase renders using the uppercase glyph, since
    these fonts are too small to draw a distinct lowercase form. Any other
    character renders as a blank cell instead of raising -- use
    `LargeText.supported_chars()` to see the full set.
    """

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
        """Every character (besides space) this font can render. Letters
        are case-insensitive, so only the uppercase form is listed."""
        _, _, glyphs = _get_font(font)
        return "".join(sorted(ch for ch in glyphs if ch != " "))

    # -- color sampling, by column position across the whole string ----

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

    # -- glyph assembly --------------------------------------------------

    def _grid(self) -> List[List[bool]]:
        """The on/off pixel grid for the whole string: one bool list per
        font row, `self._glyph_h` rows total."""
        rows: List[List[bool]] = [[] for _ in range(self._glyph_h)]
        for i, ch in enumerate(self.text):
            if i > 0 and self.spacing:
                for r in rows:
                    r.extend([False] * self.spacing)
            glyph_rows = _glyph_rows(self._font_dict, self._glyph_h, ch)
            for r, glyph_row in zip(rows, glyph_rows):
                r.extend(c == "#" for c in glyph_row)
        return rows

    # -- rendering ---------------------------------------------------------

    def _solid(self, width: int, fg: Optional[RGB]) -> str:
        """A solid cell: spaces with the color as their *background*, rather
        than a full-block glyph, so cells fill their whole row height with no
        seams (block glyphs often leave gaps between rows in terminal fonts).
        With no color set, reverse video paints it in the default text color."""
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
                    parts.append(str(ColorText(_UPPER_HALF, foreground=fg, background=b, styles=self.styles)))
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

    # -- size --------------------------------------------------------------

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

    # -- wrap / align --------------------------------------------------------

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
        """Wraps at whole-character boundaries only: one big character is
        never split mid-glyph, so a line can still come out wider than
        `width` if a single character alone doesn't fit.
        """
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
        """Aligns each rendered row within `width`, ANSI-aware."""
        rendered = self.render()
        lines = [align_text(line, width, align=align, fillchar=fillchar) for line in rendered.split("\n")]
        return "\n".join(lines)

    def draw(self, row: int, col: int):
        from .terminal import print_at  # lazy: avoids a load-time cycle with .terminal
        return print_at(row, col, self.render())