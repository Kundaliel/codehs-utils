

from typing import NamedTuple

from ._buffer import frame


class Rect(NamedTuple):
    row: int
    col: int
    width: int
    height: int

    @property
    def top(self) -> int:
        return self.row

    @property
    def left(self) -> int:
        return self.col

    @property
    def bottom(self) -> int:
        return self.row + self.height

    @property
    def right(self) -> int:
        return self.col + self.width

    def contains(self, x: int, y: int) -> bool:
        return self.col <= x < self.col + self.width and self.row <= y < self.row + self.height

    def fill(self, color=None, char: str = " "):
        from .drawing import fill_rect
        fill_rect(self.row, self.col, self.width, self.height, color, char)
        return self

    def draw_border(self, color=None, style: str = "single", background=None):
        from .colors import ColorText
        from .terminal import print_at
        from .drawing import _BORDER_STYLES

        if style not in _BORDER_STYLES:
            raise ValueError(
                f"Unknown border style: '{style}'. Available styles: "
                f"{', '.join(sorted(_BORDER_STYLES))}"
            )
        if self.width < 2 or self.height < 2:
            raise ValueError("A border needs a Rect at least 2 wide and 2 tall.")
        tl, tr, bl, br, h, v = _BORDER_STYLES[style]
        w = self.width

        def paint(text):
            return str(ColorText(text, color, background))

        with frame():
            print_at(self.row, self.col, paint(tl + h * (w - 2) + tr))
            print_at(self.bottom - 1, self.col, paint(bl + h * (w - 2) + br))
            if self.height > 2:
                side = "\n".join([paint(v)] * (self.height - 2))
                print_at(self.row + 1, self.col, side)
                print_at(self.row + 1, self.right - 1, side)
        return self
