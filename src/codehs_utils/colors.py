"""RGB colors, ANSI styles, and styled/gradient text.

`ColorLike` parses names/hex/RGB tuples into a normalized RGB color.
`ColorText` and `GradientText` render styled strings (solid or gradient
foreground/background, bold/italic/etc.) as ANSI escape sequences.
`StyledText` concatenates pieces of any of the above.
"""

import json
import gzip
import base64
from typing import Dict, List, Optional, Sequence, Tuple, Union

from .text import _visible_len, _tokenize_ansi, _is_reset, wrap_text, align_text

def _fg_code(rgb) -> str:
    if rgb is None:
        return ""
    r, g, b = rgb
    return f"\033[38;2;{r};{g};{b}m"


def _bg_code(rgb) -> str:
    if rgb is None:
        return ""
    r, g, b = rgb
    return f"\033[48;2;{r};{g};{b}m"


_STYLE_CODES = {
    "bold": "1",
    "dim": "2",
    "italic": "3",
    "underline": "4",
    "blink": "5",
    "reverse": "7",
    "strikethrough": "9",
}


def _validate_styles(styles) -> List[str]:
    result = []
    for s in styles:
        key = str(s).strip().lower()
        if key not in _STYLE_CODES:
            raise ValueError(
                f"Unknown style: '{s}'. Available styles: {', '.join(sorted(_STYLE_CODES))}"
            )
        if key not in result:
            result.append(key)
    return result


class ColorLike:
    COMP_COL = "H4sIAP+HsmoC/31Xy47rNgz9lcGs78KSX3F/pehCsZVYjSN5ZDuBW/TfK5J62Zi5QKKFjihSfBzS/36KSfXyOm3y84+PP3lV/Prg1cUtdf3Xr49PoVf1tcn3qFY6UMOBsnYLowNfmwCgQJEk57afwiqNUoy3AWYc4X82mynMBK9S3T0Cm7jwAhG1fHkr8Tx3VrKuQWgS/cNbAT+/p/tRDmJ6Gj0kMbS9IF3+1SQVDHCbL2UmuaLlpdNSlaCONFnz1gg07p6Kwx/3Nzvtb2NIEXf77FK5pcQ7ezHINWjrnCCrwfgGDe1HYVcrt+XkKg+a3kzCO585M1nhsJJAY8UUX4aSlwDo22Te0galrADRqgMHtOHIoqZHcgxGnVzdW/VcjKa3gGvc3xu7C/1NuAdhH0dvsrILQCbjdg/Q3UyD1Jbc5j0GC4sHrNjJ3SDolwRKGW8uQuA98rPYYxQPRQoBuJQg3Qb0Ke5Sr4KC353fYib1klHvpUZRlwRR3IVE31OWsio3y9h+VPTW2mnFWiqqgFo55Fqj1IIpjFeWYCuIMc4jLEU0iEGqsgskV1XGA5A/ITqtS82GHd6EeHB05V7TdvA/wfIHeN3s12bUEmLPiwaWiGe1BBkGJ3x4pZxnpbMMxBRtA7Y89iylWMdStqlnzIui9iXBioTJHzAz3FNJlKiuirfelJVXq4hIWOtshVQsMTyumFypZSyIqY9ciWG6GSuXNYYBcxjC6KW3flyUiJKJbO5C6eVqrEml5hdER7OsSSkWaMbNh+LhDBkFuIEHMJnKAp9EvyF7+oWArJZgv4i7u5wcl5BXSl/3FKbo6fNto9FyH+T7RPHkrNGsh7hTiIi5lB6U0L4SOAAdh3/A7uiptvZ1STIvY/csLElTrHSygSKOyCReUg+YDMuYcSCGtM5PUN0FcRd0At86FR3HJOLeZ5N01erq/HbzRZuShdJwUvcxdgNyKWvw/ogmZq+Ko2cJ9ozKSXPiYURjXqTAkXpcWNISksEVJFZlLE2PRlIBLSWSSpXDvxE+BvgC/bArI5oxGuJNYjTCM0orQRaqkbXJ8owbGDX0JsUGD+Scxhh2nQa4szwfkb87sko5pUg1OHBAeSZTcx/H7OPeTU+Z98oibMa3+aSATkCYljqFy+csIFlTOjGIG7KM0bEIQ994ykFtz9MUVnCvzruSDp2mIMpRgrJ+dXHvvtQxyITPm50nuhsaA2OggHXpQB5IDDL0DsbK7ETenBjHXkzplp2Z3RPuOUOhg1hdpTOHNtTiQ7vYXekIdaLQZTuAsRGSNWrQeV1yDCa+iWC99laKZxpNfVkTuqy7NctpOuWcfGn6XixKn0bXCzpSi5f425w6C86PbenxPZuqiARcgbuJ1wuUYUymVMEJ5UjKaX+w4kqpAOGC8ZUG1PPU0oR0JSDwMWAwTHkoJAf1Hgo++nsWkzx2J2APTqVcxBORYIA7eQ3BqHlADwFlbe0pyCcGnDjEk2MBgw1+hJjFLHbhHDtnsz/GHP06S9GP83a7ZU0So1ITarfYgRhMXQ1JHWitwzQjYNooNTClGuzhGN/ZvIdsDG+RPqoYrayCfPn6ELtZRLq0yXCoXvJRSQeGnA7wNpeCe/pC8WNgnAWt2UVksyY0Xp+kixiGSSZhcBXOzR2hibBjQ6JYL0IPSSmHXsEat9CXWU4AVeOnokvroWV07Jl13zrGd1FSaxrCwZnQQKgtu2+WFzVldH9YEPq2KVCCH2kGgC6R3alZ8PBA6nanPnFG9YH904jwHWnRVxqieWdpaZaJQ9DquzujrTi0rJKGgtNIsI6Ofib/hdiEUZmh/1fzFKuJBgLptZiXh/KCeFFWFnhjmtmp7dP4g9B7lGJNJEhM1RFynI7TVILI8jSP84c9hfS7FlokIKOJKrXL//4HY/qhiboQAAA="
    NAMED_COLORS = json.loads(gzip.decompress(base64.b64decode(COMP_COL)).decode("utf-8"))

    def __init__(self, color: Union[str, Tuple[int, int, int], "ColorLike", None] = None):
        self.rgb = self._parse(color)

    @staticmethod
    def print_samples():
        # Imported lazily to avoid a circular import: .terminal and .drawing
        # both import from this module at load time, so this module can't
        # import them back at load time too.
        from .terminal import get_terminal_size
        from .drawing import banner
        width = get_terminal_size()[0]
        for name, color in ColorLike.NAMED_COLORS.items():
            c = ColorLike(color)
            print(banner(name, width, color=c.contrast(), background=c))

    def _parse(self, color) -> Optional[Tuple[int, int, int]]:
        if color is None:
            return None
        if isinstance(color, ColorLike):
            return color.rgb

        if isinstance(color, (tuple, list)):
            if len(color) != 3 or not all(0 <= int(c) <= 255 for c in color):
                raise ValueError(f"RGB must be 3 integers between 0 and 255, got: {color}")
            return tuple(int(c) for c in color)

        if isinstance(color, str):
            clean = color.strip().lower()

            if clean.startswith("#"):
                hex_str = clean[1:]
                if len(hex_str) == 3:
                    hex_str = "".join(ch * 2 for ch in hex_str)
                if len(hex_str) == 6:
                    try:
                        return tuple(int(hex_str[i: i + 2], 16) for i in (0, 2, 4))
                    except ValueError:
                        pass
                raise ValueError(f"Invalid hex color format: '{color}'")

            clean = clean.replace(" ", "").replace("_", "").replace("-", "")
            if clean in self.NAMED_COLORS:
                return tuple(self.NAMED_COLORS[clean])

            raise ValueError(f"Unknown color name: '{color}'")

        raise TypeError(f"Unsupported color type: {type(color).__name__}")

    def _require(self) -> Tuple[int, int, int]:
        if self.rgb is None:
            raise ValueError("This ColorLike has no color (it was created from None).")
        return self.rgb

    def to_hex(self) -> str:
        r, g, b = self._require()
        return f"#{r:02x}{g:02x}{b:02x}"

    def luminance(self) -> float:
        r, g, b = self._require()
        return (0.299 * r + 0.587 * g + 0.114 * b) / 255

    def contrast(self) -> "ColorLike":
        return ColorLike((0, 0, 0) if self.luminance() >= 0.5 else (255, 255, 255))

    def mix(self, other, t: float = 0.5) -> "ColorLike":
        a = self._require()
        b = ColorLike(other)._require()
        t = max(0.0, min(1.0, t))
        return ColorLike(tuple(round(x + (y - x) * t) for x, y in zip(a, b)))

    def lighten(self, amount: float = 0.2) -> "ColorLike":
        return self.mix((255, 255, 255), amount)

    def darken(self, amount: float = 0.2) -> "ColorLike":
        return self.mix((0, 0, 0), amount)

    def __eq__(self, other):
        if isinstance(other, ColorLike):
            return self.rgb == other.rgb
        return NotImplemented

    def __hash__(self):
        return hash(self.rgb)

    def __repr__(self):
        return f"ColorLike({self.rgb})"


def _vlen(part) -> int:
    return _visible_len(part) if isinstance(part, str) else len(part)


class StyledText:
    def __init__(self, parts: Optional[List[Union[str, "ColorText", "GradientText"]]] = None):
        self.parts: List[Union[str, "ColorText", "GradientText"]] = list(parts) if parts else []

    def __str__(self) -> str:
        return "".join(str(p) for p in self.parts)

    def __len__(self) -> int:
        return sum(_vlen(p) for p in self.parts)

    def __bool__(self) -> bool:
        return bool(self.parts)

    def wrap(self, width: int, collapse_space: bool = True) -> str:
        return wrap_text(str(self), width, collapse_space=collapse_space)

    def align(self, width: int, align: str = "left", fillchar: str = " ") -> str:
        return align_text(str(self), width, align=align, fillchar=fillchar)

    def __add__(self, other):
        if isinstance(other, StyledText):
            return StyledText(self.parts + other.parts)
        if isinstance(other, (ColorText, GradientText, str)):
            return StyledText(self.parts + [other])
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, str):
            return StyledText([other] + self.parts)
        return NotImplemented

    def __repr__(self):
        return f"StyledText({self.parts!r})"


class _StyleMixin:
    def set_text(self, text: str = ""):
        self.text = "" if text is None else str(text)
        return self

    def set_reset(self, reset: bool = True):
        self.reset = reset
        return self

    def set_background(self, col: Union[ColorLike, str, tuple, None] = None):
        self.background = ColorLike(col) if col is not None else None
        return self

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

    def __add__(self, other):
        if isinstance(other, StyledText):
            return StyledText([self] + other.parts)
        if isinstance(other, (ColorText, GradientText, str)):
            return StyledText([self, other])
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, str):
            return StyledText([other, self])
        return NotImplemented


ColorSpec = Union[ColorLike, str, tuple, list]

GradientColors = Union[str, Sequence[ColorSpec]]


class ColorText(_StyleMixin):
    _validate_styles = staticmethod(_validate_styles)

    def __init__(
        self,
        text: str = "",
        foreground: Union[ColorLike, str, tuple, None] = None,
        background: Union[ColorLike, str, tuple, None] = None,
        styles: Optional[Sequence[str]] = None,
        reset: bool = True,
        *,
        color: Union[ColorLike, str, tuple, None] = None,
    ):
        if foreground is None:
            foreground = color
        self.text = "" if text is None else str(text)
        self.fore = ColorLike(foreground) if foreground is not None else None
        self.background = ColorLike(background) if background is not None else None
        self.styles: List[str] = _validate_styles(styles) if styles else []
        self.reset = reset

    @property
    def color(self) -> Optional[ColorLike]:
        return self.fore

    @color.setter
    def color(self, value):
        self.set_color(value)

    def set_color(self, col: Union[ColorLike, str, tuple, None] = None):
        self.fore = ColorLike(col) if col is not None else None
        return self

    def __str__(self) -> str:
        codes = [f"\033[{_STYLE_CODES[s]}m" for s in self.styles]

        if self.fore and self.fore.rgb:
            codes.append(_fg_code(self.fore.rgb))

        if self.background and self.background.rgb:
            codes.append(_bg_code(self.background.rgb))

        prefix = "".join(codes)
        suffix = "\033[0m" if prefix and self.reset else ""

        return f"{prefix}{self.text}{suffix}"

    def __len__(self) -> int:
        return _visible_len(self.text)


class GradientText(_StyleMixin):

    PRESETS = {
        "rainbow": ["red", "orange", "yellow", "green", "blue", "indigo", "violet"],
        "fire": ["darkred", "red", "orange", "gold", "yellow"],
        "ocean": ["midnightblue", "navy", "blue", "deepskyblue", "cyan"],
        "sunset": ["indigo", "purple", "orangered", "gold"],
        "pastel": ["lightpink", "lightyellow", "lightgreen", "lightskyblue", "plum"],
        "grayscale": ["black", "white"],
        "neon": ["deeppink", "fuchsia", "cyan", "yellow"],
        "forest": ["darkgreen", "forestgreen", "yellowgreen", "greenyellow"],
        "mint": ["teal", "mediumspringgreen", "honeydew"],
        "gold": ["saddlebrown", "goldenrod", "gold", "lightyellow"],
    }

    def __init__(
        self,
        text: str = "",
        colors: Optional[GradientColors] = None,
        color: Union[ColorLike, str, tuple, None] = None,
        background: Union[ColorLike, str, tuple, None] = None,
        background_colors: Optional[GradientColors] = None,
        styles: Optional[Sequence[str]] = None,
        reset: bool = True,
        *,
        foreground: Union[ColorLike, str, tuple, None] = None,
    ):
        if color is None:
            color = foreground
        self.text = "" if text is None else str(text)
        self.color = ColorLike(color) if color is not None else None
        self.background = ColorLike(background) if background is not None else None
        self.bg_colors: List[ColorLike] = (
            self._resolve_colors(background_colors) if background_colors is not None else []
        )
        self.styles: List[str] = _validate_styles(styles) if styles else []
        self.reset = reset
        self.colors: List[ColorLike] = self._resolve_colors(colors) if colors is not None else []

    def _resolve_colors(self, colors: GradientColors) -> List[ColorLike]:
        available = ", ".join(sorted(self.PRESETS))
        if isinstance(colors, ColorLike):
            return [colors]
        if isinstance(colors, str):
            key = colors.strip().lower()
            if key in self.PRESETS:
                colors = self.PRESETS[key]
            else:
                try:
                    return [ColorLike(colors)]
                except ValueError:
                    raise ValueError(
                        f"Unknown preset or color: '{colors}'. Available presets: {available}"
                    ) from None
        elif (isinstance(colors, (tuple, list)) and len(colors) == 3
              and all(isinstance(c, (int, float)) and not isinstance(c, bool) for c in colors)):
            return [ColorLike(tuple(colors))]

        if not colors:
            raise ValueError(
                "GradientText requires at least one color: pass a preset name "
                "(e.g. 'rainbow') or a sequence of colors (e.g. ['red', 'blue'])."
            )

        return [ColorLike(c) for c in colors]

    def set_colors(self, colors: GradientColors):
        self.colors = self._resolve_colors(colors)
        return self

    def set_color(self, col: Union[ColorLike, str, tuple, None] = None):
        self.color = ColorLike(col) if col is not None else None
        return self

    def set_background_gradient(self, colors: GradientColors):
        self.bg_colors = self._resolve_colors(colors)
        return self

    @classmethod
    def from_preset(cls, text: str = "", preset: str = "rainbow", **kwargs):
        return cls(text=text, colors=preset, **kwargs)

    @classmethod
    def list_presets(cls) -> List[str]:
        return sorted(cls.PRESETS)

    @classmethod
    def preview_presets(cls, sample_text: str = "Sample Text", print_output: bool = True):
        results = []
        for name in cls.list_presets():
            rendered = str(cls.from_preset(text=sample_text, preset=name))
            results.append((name, rendered))
            if print_output:
                print(f"{name:12s} {rendered}")
        return results

    def _color_at_from(self, colors: List[ColorLike], t: float) -> Tuple[int, int, int]:
        n = len(colors)
        if n == 1:
            return colors[0].rgb

        pos = t * (n - 1)
        seg = int(pos)
        if seg >= n - 1:
            seg = n - 2
        local_t = pos - seg

        r1, g1, b1 = colors[seg].rgb
        r2, g2, b2 = colors[seg + 1].rgb
        return (
            round(r1 + (r2 - r1) * local_t),
            round(g1 + (g2 - g1) * local_t),
            round(b1 + (b2 - b1) * local_t),
        )

    def _color_at(self, t: float) -> Tuple[int, int, int]:
        return self._color_at_from(self.colors, t)

    def __str__(self) -> str:
        if not self.text:
            return ""

        style_prefix = "".join(f"\033[{_STYLE_CODES[s]}m" for s in self.styles)
        fg_solid = _fg_code(self.color.rgb) if self.color and self.color.rgb else ""
        bg_solid = _bg_code(self.background.rgb) if self.background and self.background.rgb else ""

        grad_fg = bool(self.colors)
        grad_bg = bool(self.bg_colors)
        want_fg = grad_fg or bool(fg_solid)
        want_bg = grad_bg or bool(bg_solid)

        tokens = _tokenize_ansi(self.text)
        length = sum(1 for kind, _ in tokens if kind == 'char')

        any_code = bool(style_prefix or want_fg or want_bg)
        reset_code = "\033[0m" if any_code and self.reset else ""

        parts = []
        idx = 0
        has_fg = has_bg = False
        sent_fg = sent_bg = False
        need_style = True
        for kind, val in tokens:
            if kind == 'ansi':
                if _is_reset(val):
                    has_fg = has_bg = sent_fg = sent_bg = False
                    need_style = True
                elif val.startswith("\033[38"):
                    has_fg = True
                elif val.startswith("\033[48"):
                    has_bg = True
                parts.append(val)
                continue

            ch = val
            if ch == '\n':
                if reset_code:
                    parts.append(reset_code)
                parts.append(ch)
                idx += 1
                has_fg = has_bg = sent_fg = sent_bg = False
                need_style = True
                continue

            t = idx / (length - 1) if length > 1 else 0.0
            prefix = ""
            if need_style:
                prefix += style_prefix
                need_style = False
            if want_fg and not has_fg:
                if grad_fg:
                    prefix += _fg_code(self._color_at(t))
                elif not sent_fg:
                    prefix += fg_solid
                    sent_fg = True
            if want_bg and not has_bg:
                if grad_bg:
                    prefix += _bg_code(self._color_at_from(self.bg_colors, t))
                elif not sent_bg:
                    prefix += bg_solid
                    sent_bg = True
            parts.append(f"{prefix}{ch}")
            idx += 1

        return "".join(parts) + reset_code

    def __repr__(self):
        stops = [c.rgb for c in self.colors]
        return f"GradientText(text={self.text!r}, colors={stops})"

    def __len__(self) -> int:
        return _visible_len(self.text)


def _make_preset_classmethod(preset_name: str):
    @classmethod
    def _preset_method(cls, text: str = "", **kwargs):
        return cls.from_preset(text=text, preset=preset_name, **kwargs)

    return _preset_method


for _preset_name in GradientText.PRESETS:
    setattr(GradientText, _preset_name, _make_preset_classmethod(_preset_name))
del _preset_name
