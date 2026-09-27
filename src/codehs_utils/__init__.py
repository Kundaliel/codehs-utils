"""codehs_utils: a small terminal toolkit (colors, gradients, banners,
keyboard/mouse input, drawing) originally written as one flat script for
CodeHS's Python environment, now split into a regular package.

Everything importable from the original flat module is re-exported here,
so ``import codehs_utils`` (or ``from codehs_utils import *``) behaves the
same as before.
"""

from ._buffer import frame, write
from .geometry import Rect
from .terminal import (
    MouseEvent,
    KeyEvent,
    restore_terminal,
    get_key,
    get_keys,
    get_key_nonblocking,
    get_mouse_event,
    get_mouse_event_nonblocking,
    get_event,
    events,
    get_cursor_position,
    gcp,
    get_terminal_size,
    clear_screen,
    set_cursor_col,
    set_cursor_row,
    set_cursor_pos,
    move_cursor,
    save_cursor_position,
    restore_cursor_position,
    hide_cursor,
    show_cursor,
    enter_alt_screen,
    leave_alt_screen,
    clear_line,
    enable_mouse_tracking,
    disable_mouse_tracking,
    print_at,
    app,
)
from .text import wrap_text, align_text
from .colors import ColorLike, StyledText, ColorText, GradientText, ColorSpec, GradientColors
from .printing import PrintOptions, slow_print
from .bigtext import LargeText
from .drawing import (
    Banner,
    BannerRow,
    banner,
    fill_rect,
    get_pixel_size,
    set_pixel,
    clear_pixel,
    clear_pixels,
    Button,
)

__all__ = [
    "frame", "write",
    "Rect",
    "MouseEvent", "KeyEvent", "restore_terminal",
    "get_key", "get_keys", "get_key_nonblocking",
    "get_mouse_event", "get_mouse_event_nonblocking",
    "get_event", "events",
    "get_cursor_position", "gcp", "get_terminal_size",
    "clear_screen", "set_cursor_col", "set_cursor_row", "set_cursor_pos",
    "move_cursor", "save_cursor_position", "restore_cursor_position",
    "hide_cursor", "show_cursor", "enter_alt_screen", "leave_alt_screen",
    "clear_line", "enable_mouse_tracking", "disable_mouse_tracking",
    "print_at", "app",
    "wrap_text", "align_text",
    "ColorLike", "StyledText", "ColorText", "GradientText",
    "ColorSpec", "GradientColors",
    "PrintOptions", "slow_print",
    "LargeText",
    "Banner", "BannerRow", "banner",
    "fill_rect", "get_pixel_size", "set_pixel", "clear_pixel", "clear_pixels",
    "Button",
]

__version__ = "1.2.3.1"