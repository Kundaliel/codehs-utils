

import sys
import time
from dataclasses import dataclass, field
from typing import IO, List, Optional, Sequence, Union

from .text import _tokenize_ansi
from .colors import ColorLike, ColorText, GradientText, StyledText, ColorSpec, _STYLE_CODES

_RESET = "\033[0m"

Printable = Union[str, ColorText, GradientText, StyledText]


@dataclass
class PrintOptions:


    speed: float = 40.0
    color: Optional[ColorSpec] = None
    background: Optional[ColorSpec] = None
    styles: Optional[Sequence[str]] = None
    end: str = "\n"
    newline_delay: float = 0.5
    flush: bool = True
    stream: IO[str] = field(default_factory=lambda: sys.stdout)

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

    if isinstance(text, (ColorText, GradientText, StyledText)):
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

    if options is None:
        options = PrintOptions()

    stream = options.stream
    delay = 1.0 / options.speed

    rendered = _render(text, options)
    tokens = _tokenize_ansi(rendered)
    had_any_codes = any(kind == "ansi" for kind, _ in tokens)

    pending = []
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