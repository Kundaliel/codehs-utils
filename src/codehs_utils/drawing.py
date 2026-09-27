"""Higher-level drawing built on top of `.terminal` and `.colors`: text
banners/boxes, filled rectangles, a half-block pixel canvas, and clickable
buttons.
"""

from typing import Callable, List, Optional, Sequence, Tuple, Union

from .text import _visible_len, _char_width, align_text
from .colors import ColorLike, ColorText, GradientText, StyledText, ColorSpec, GradientColors
from .geometry import Rect
from .terminal import print_at, get_terminal_size
from ._pixelbuf import _pixel_buf

def _calculate_box_width(lines, padding=4):
    if isinstance(lines, list):
        return max(map(_visible_len, lines)) + padding
    if isinstance(lines, (StyledText, ColorText, GradientText)):
        return max(_visible_len(line) for line in str(lines).split("\n")) + padding
    if isinstance(lines, str):
        return max(_visible_len(line) for line in lines.split("\n")) + padding
    return 48


_RESET = "\033[0m"


class Banner:
    def __init__(self, lines: Union[str, Sequence[str]]):
        if isinstance(lines, str):
            lines = lines.split("\n")
        lines = [str(line) for line in lines]
        self.width = max((_visible_len(line) for line in lines), default=0)
        self.lines = [line + " " * (self.width - _visible_len(line)) for line in lines]

    @property
    def height(self) -> int:
        return len(self.lines)

    def draw(self, row: int, col: int) -> Rect:
        return print_at(row, col, self)

    def align(self, width: int, align: str = "left", fillchar: Optional[str] = None) -> str:
        return BannerRow([self]).align(width, align, fillchar)

    def __str__(self) -> str:
        return "\n".join(self.lines)

    def __repr__(self):
        return f"Banner(width={self.width}, height={self.height})"

    def __add__(self, other):
        if isinstance(other, BannerRow):
            return BannerRow([self] + other.banners, other.gap, other.valign)
        if isinstance(other, Banner):
            return BannerRow([self, other])
        if isinstance(other, str):
            return str(self) + other
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, int) and other == 0:
            return self
        if isinstance(other, str):
            return other + str(self)
        return NotImplemented


class BannerRow:
    _VALIGNS = ("top", "middle", "bottom")

    def __init__(self, banners: Sequence[Banner], gap: int = 1, valign: str = "top"):
        self.banners: List[Banner] = list(banners)
        self.set_gap(gap)
        self.set_valign(valign)

    def set_gap(self, gap: int):
        self.gap = max(0, gap)
        return self

    def set_valign(self, valign: str):
        if valign not in self._VALIGNS:
            raise ValueError(
                f"Unknown valign mode: '{valign}'. Use 'top', 'middle', or 'bottom'."
            )
        self.valign = valign
        return self

    @property
    def width(self) -> int:
        return sum(b.width for b in self.banners) + self.gap * max(0, len(self.banners) - 1)

    @property
    def height(self) -> int:
        return max((b.height for b in self.banners), default=0)

    def draw(self, row: int, col: int) -> Rect:
        return print_at(row, col, self)

    def _column(self, b: Banner, height: int) -> List[str]:
        extra = height - b.height
        above = {"top": 0, "bottom": extra, "middle": extra // 2}[self.valign]
        blank = " " * b.width
        lines = [blank] * above + b.lines + [blank] * (extra - above)
        return [ln + _RESET if "\033" in ln else ln for ln in lines]

    def _render(self, gaps: List[int], fillchar: Optional[str] = " ") -> str:
        height = self.height
        cols = [self._column(b, height) for b in self.banners]
        rows = []
        for r in range(height):
            pieces = []
            for i, col in enumerate(cols):
                pieces.append(col[r])
                if i < len(gaps):
                    pieces.append(fillchar * gaps[i])
            rows.append("".join(pieces))
        return "\n".join(rows)

    def align(self, width: int, align: str = "left", fillchar: Optional[str] = None) -> str:
        if not self.banners:
            return ""
        if fillchar is None:
            fillchar = " "  # banners are solid blocks: pad with real spaces
        gaps = [self.gap] * (len(self.banners) - 1)
        pad = max(0, width - self.width)
        left = right = 0

        if align == "left":
            right = pad
        elif align == "right":
            left = pad
        elif align == "center":
            left = pad // 2
            right = pad - left
        elif align == "justify":
            if gaps:
                base, extra = divmod(pad, len(gaps))
                gaps = [g + base + (1 if i < extra else 0) for i, g in enumerate(gaps)]
            else:
                right = pad
        else:
            raise ValueError(
                f"Unknown align mode: '{align}'. Use 'left', 'right', 'center', or 'justify'."
            )

        body = self._render(gaps, fillchar)
        return "\n".join(fillchar * left + line + fillchar * right for line in body.split("\n"))

    def __str__(self) -> str:
        return self._render([self.gap] * max(0, len(self.banners) - 1))

    def __repr__(self):
        return f"BannerRow({len(self.banners)} banners, width={self.width}, height={self.height})"

    def __add__(self, other):
        if isinstance(other, Banner):
            return BannerRow(self.banners + [other], self.gap, self.valign)
        if isinstance(other, BannerRow):
            return BannerRow(self.banners + other.banners, self.gap, self.valign)
        if isinstance(other, str):
            return str(self) + other
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, int) and other == 0:
            return self
        if isinstance(other, str):
            return other + str(self)
        return NotImplemented


def banner(
    text: str,
    width: Union[int, None] = None,
    color: Union[ColorLike, str, tuple, None] = None,
    colors: Optional[GradientColors] = None,
    background: Union[ColorLike, str, tuple, None] = None,
    background_colors: Optional[GradientColors] = None,
    styles: Optional[Sequence[str]] = None,
    padding: int = 1,
    align: str = "center",
) -> Banner:
    if isinstance(text, (list, tuple)):
        text = "\n".join(str(t) for t in text)
    else:
        text = str(text)
    if width is None:
        width = _calculate_box_width(text)
    padding = max(0, padding)
    # Banners need real spaces (not cursor moves) so the background color fills the box.
    line = align_text(text, width, align=align, fillchar=" ")
    blank = " " * width

    def _style(s: str) -> str:
        gt = GradientText(s)
        if colors is not None:
            gt.set_colors(colors)
        elif color is not None:
            gt.set_color(color)
        if background is not None:
            gt.set_background(background)
        if background_colors is not None:
            gt.set_background_gradient(background_colors)
        if styles:
            gt.set_styles(*styles)
        return str(gt)

    rows = [_style(blank)] * padding + [_style(line)] + [_style(blank)] * padding
    return Banner("\n".join(rows))


_BORDER_STYLES = {
    "single": "\u250c\u2510\u2514\u2518\u2500\u2502",
    "double": "\u2554\u2557\u255a\u255d\u2550\u2551",
    "rounded": "\u256d\u256e\u2570\u256f\u2500\u2502",
    "heavy": "\u250f\u2513\u2517\u251b\u2501\u2503",
    "ascii": "++++-|",
}


def fill_rect(row: int, col: int, width: int, height: int, color=None,
              char: str = " ", foreground=None) -> Rect:
    char = str(char)
    if len(char) != 1 or _char_width(char) != 1:
        raise ValueError("char must be a single character, one column wide.")
    width = max(0, int(width))
    height = max(0, int(height))
    if width and height:
        line = str(ColorText(char * width, foreground, color))
        print_at(row, col, "\n".join([line] * height))
    return Rect(row, col, width, height)


def get_pixel_size() -> Tuple[int, int]:
    width, height = get_terminal_size()
    return width, height * 2


def _draw_pixel_cell(x: int, row: int):
    top = _pixel_buf.get((x, 2 * row - 1))
    bottom = _pixel_buf.get((x, 2 * row))
    if top and bottom:
        glyph = ColorText("\u2584", bottom, top)
    elif top:
        glyph = ColorText("\u2580", top)
    elif bottom:
        glyph = ColorText("\u2584", bottom)
    else:
        glyph = " "
    print_at(row, x, glyph)


def set_pixel(x: int, y: int, color):
    x, y = int(x), int(y)
    rgb = ColorLike(color).rgb
    if x < 1 or y < 1:
        return
    if rgb is None:
        _pixel_buf.pop((x, y), None)
    else:
        _pixel_buf[(x, y)] = rgb
    _draw_pixel_cell(x, (y + 1) // 2)


def clear_pixel(x: int, y: int):
    set_pixel(x, y, None)


def clear_pixels():
    _pixel_buf.clear()


class Button:
    def __init__(
        self,
        text: str,
        row: int,
        col: int,
        width: Optional[int] = None,
        background: Union[ColorLike, str, tuple] = "skyblue",
        color: Union[ColorLike, str, tuple, None] = None,
        *,
        hover_background=None,
        hover_color=None,
        pressed_background=None,
        pressed_color=None,
        padding: int = 1,
        styles: Optional[Sequence[str]] = None,
        trigger: str = "release",
        on_click: Optional[Callable[[], None]] = None,
    ):
        if trigger not in ("release", "press"):
            raise ValueError("trigger must be 'release' or 'press'.")
        bg = ColorLike(background)
        fg = ColorLike(color) if color is not None else bg.contrast()
        hbg = ColorLike(hover_background) if hover_background is not None else bg.darken(0.25)
        hfg = ColorLike(hover_color) if hover_color is not None else hbg.contrast()
        pbg = ColorLike(pressed_background) if pressed_background is not None else bg.darken(0.55)
        pfg = ColorLike(pressed_color) if pressed_color is not None else pbg.contrast()
        self._colors = {"idle": (fg, bg), "hover": (hfg, hbg), "pressed": (pfg, pbg)}
        self.text = str(text)
        self.row = row
        self.col = col
        self.padding = padding
        self.styles = styles
        self.trigger = trigger
        self.on_click = on_click
        self._width = width
        self._armed = False
        self.state = "idle"
        first = self._banner("idle")
        self.rect = Rect(row, col, first.width, first.height)

    def _banner(self, state: str) -> Banner:
        fg, bg = self._colors[state]
        return banner(self.text, width=self._width, color=fg, background=bg,
                      styles=self.styles, padding=self.padding)

    def draw(self) -> Rect:
        self.rect = self._banner(self.state).draw(self.row, self.col)
        return self.rect

    def handle(self, event) -> bool:
        if getattr(event, "kind", None) != "mouse" or event.type.startswith("wheel"):
            return False
        inside = self.rect.contains(event.x, event.y)
        clicked = False
        if event.type == "press" and event.button == "left" and inside:
            self._armed = True
            clicked = self.trigger == "press"
        elif event.type == "release" and self._armed:
            clicked = inside and self.trigger == "release"
            self._armed = False
        new_state = "pressed" if (self._armed and inside) else ("hover" if inside else "idle")
        if new_state != self.state:
            self.state = new_state
            self.draw()
        if clicked and self.on_click is not None:
            self.on_click()
        return clicked