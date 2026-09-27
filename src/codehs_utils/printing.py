"""Typewriter-style slow printing, built on top of this package's own
color objects instead of raw RGB tuples.

`slow_print` accepts a plain string *or* a `ColorText` / `GradientText` /
`StyledText` instance. Colors, backgrounds, and styles (bold, italic, ...)
are resolved once into an ANSI string, then revealed one visible character
at a time -- each character keeps whatever color it was supposed to have,
so a `GradientText("Hello", colors="rainbow")` still rainbows correctly
as it's typed out, instead of only supporting one flat foreground color.
"""

import sys
import time
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Union

from .text import _tokenize_ansi
from .colors import ColorLike, ColorText, GradientText, StyledText, ColorSpec, _STYLE_CODES

_RESET = "\033[0m"

#: Anything `slow_print` knows how to render.
Printable = Union[str, ColorText, GradientText, StyledText]


@dataclass
class PrintOptions:
    """Settings for `slow_print`.

    `color` / `background` / `styles` are only used when `text` is a plain
    `str` -- they're ignored (and unnecessary) for `ColorText`, `GradientText`,
    or `StyledText`, since those already carry their own coloring.
    """

    speed: float = 40.0                          # visible characters per second
    color: Optional[ColorSpec] = None             # foreground, for plain strings
    background: Optional[ColorSpec] = None        # background, for plain strings
    styles: Optional[Sequence[str]] = None        # e.g. ("bold", "italic")
    end: str = "\n"
    newline_delay: float = 0.5                    # extra pause after each '\n'
    flush: bool = True
    stream = sys.stdout

    def __post_init__(self):
        if self.speed <= 0:
            raise ValueError("PrintOptions.speed must be > 0")
        if self.styles:
            self.styles = list(self.styles)
            for s in self.styles:
                key = str(s).strip().lower()
                if key not in _STYLE_CODES:
                    raise ValueError(
                        f"Unknown style: '{s}'. Available styles: "
                        f"{', '.join(sorted(_STYLE_CODES))}"
                    )


def _render(text: Printable, options: PrintOptions) -> str:
    """Resolve `text` + `options` down to one fully-escaped ANSI string."""
    if isinstance(text, (ColorText, GradientText, StyledText)):
        # Already carries its own color(s)/style(s); render as-is.
        return str(text)

    text = "" if text is None else str(text)
    if options.color is not None or options.background is not None or options.styles:
        return str(ColorText(
            text,
            foreground=options.color,
            background=options.background,
            styles=options.styles,
        ))
    return text


def slow_print(text: Printable, options: Optional[PrintOptions] = None) -> None:
    """Print `text` one visible character at a time, typewriter-style.

    `text` may be:
      - a plain `str` (optionally colored via `PrintOptions.color` /
        `background` / `styles`)
      - a `ColorText` -- printed in its solid foreground/background color
      - a `GradientText` -- each revealed character shows its correct
        point along the gradient, exactly like printing it all at once
      - a `StyledText` -- a mix of the above, concatenated

    Timing is based on *visible* characters only: ANSI escape codes are
    never delayed on their own, so color changes never slow things down.

        >>> slow_print("Loading...", PrintOptions(speed=20, color="cyan"))
        >>> slow_print(GradientText("Rainbow!", colors="rainbow"))
    """
    if options is None:
        options = PrintOptions()

    stream = options.stream
    delay = 1.0 / options.speed

    rendered = _render(text, options)
    tokens = _tokenize_ansi(rendered)
    had_any_codes = any(kind == "ansi" for kind, _ in tokens)

    pending = []  # ANSI codes waiting to be emitted with the next character
    for kind, val in tokens:
        if kind == "ansi":
            pending.append(val)
            continue

        if pending:
            stream.write("".join(pending))
            pending = []
        stream.write(val)
        if options.flush:
            stream.flush()

        time.sleep(delay)
        if val == "\n":
            time.sleep(options.newline_delay)

    if pending:
        stream.write("".join(pending))
    if had_any_codes and not rendered.endswith(_RESET):
        stream.write(_RESET)
    stream.write(options.end)
    if options.flush:
        stream.flush()