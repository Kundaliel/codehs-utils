# codehs-utils

[![PyPI version](https://badge.fury.io/py/codehs-utils.svg)](https://badge.fury.io/py/codehs-utils)
[![Python versions](https://img.shields.io/pypi/pyversions/codehs-utils.svg)](https://pypi.org/project/codehs-utils/)

A Python library for terminal colors, gradients, banners, drawing, and keyboard/mouse input, originally built for CodeHS's Python environment.

## Features

- RGB and named colors for foreground and background, plus mixing/lighten/darken
- Gradient text with built-in presets (rainbow, fire, ocean, sunset, and more)
- Typewriter-style slow printing that understands gradients/styles, not just plain text
- Big multi-row "banner" text rendered from a 3x5 or 5x7 pixel font, in blocky or half-block-pixel style
- Composable text banners and boxes, alignable and laid out side by side
- Rectangles with fill and border drawing
- A half-block pixel canvas for square-pixel graphics
- Keyboard and mouse input, including click-and-drag mouse events
- Cursor and screen control (alternate screen, hide/show cursor, clear, resize-aware sizing)
- Clickable buttons with hover/press states

## Installation

```bash
pip install codehs-utils
```

## Quick Start

```python
import codehs_utils as c

# Colorful banner
print(c.banner("Hello, World!", color="white", background="blue"))

# Interactive app with mouse support
with c.app(mouse=True):
    c.banner("Click anywhere, press ESC to quit").draw(1, 1)
    for event in c.events(timeout=5):
        if event is None or (event.kind == "key" and event.key == "ESC"):
            break
```

## Documentation

### Color Functions

```python
from codehs_utils import ColorLike, ColorText, GradientText

# Using named colors, hex, or RGB tuples
red = ColorLike("red")
also_red = ColorLike("#ff0000")
also_red_too = ColorLike((255, 0, 0))

print(ColorText("Red text", foreground=red))

# Mixing and adjusting colors
lighter = red.lighten(0.3)
darker = red.darken(0.3)
contrast = red.contrast()  # black or white, whichever reads better

# Background colors
print(ColorText("Green background", background="green"))
```

### Gradient Text

```python
from codehs_utils import GradientText

# Built-in preset, as a shortcut method...
print(GradientText.rainbow("This text has rainbow colors!"))

# ...or via from_preset(), which every shortcut method calls internally
print(GradientText.from_preset("Same thing", preset="rainbow"))

# Custom stops
print(GradientText("Custom gradient", colors=["red", "orange", "yellow"]))

# Background gradient
print(GradientText("Rainbow background!", background_colors="rainbow"))
```

Mixing two colors together (used internally by `.lighten()`/`.darken()`, also usable directly):

```python
from codehs_utils import ColorLike

blend = ColorLike("red").mix("blue", t=0.5)  # 50/50 blend
print(blend.to_hex())
```

### Style Methods

`ColorText` and `GradientText` share a set of chainable style methods (from their common `_StyleMixin`), so you can build up a piece of styled text step by step instead of passing everything to the constructor at once:

```python
from codehs_utils import ColorText

msg = ColorText("warning!").bold().underline()
msg.set_background("red")
print(msg)
```

Available chainable methods:
- `.bold()`, `.italic()`, `.underline()`, `.strikethrough()`, `.dim()`, `.blink()`, `.reverse()` — turn on a single style
- `.add_style(name)` / `.remove_style(name)` — turn a named style on/off
- `.set_styles(*names)` — replace the whole style list at once
- `.set_text(text)` — change the wrapped text
- `.set_background(color)` — set or clear the background color
- `.set_reset(bool)` — whether an ANSI reset code is appended after the text (default `True`)

Every method returns `self`, so calls can be chained.

`StyledText` concatenates several `ColorText`/`GradientText`/plain-string pieces into one object, and can be wrapped or aligned as a whole:

```python
from codehs_utils import ColorText, GradientText, StyledText

line = StyledText([ColorText("Error: ", "red"), GradientText.fire("something broke")])
print(line)
print(line.align(40, "center"))
print(line.wrap(20))
```

### Slow Printing

`slow_print` reveals text one visible character at a time, typewriter-style. It takes a plain string, or any of `ColorText`/`GradientText`/`StyledText` directly — a gradient keeps the right color at each position as it's typed out, instead of only supporting one flat color:

```python
from codehs_utils import slow_print, PrintOptions, GradientText, ColorText

# Plain text, colored via PrintOptions
slow_print("Loading...", PrintOptions(speed=20, color="cyan"))

# A gradient reveals its own colors character by character
slow_print(GradientText("Rainbow!", colors="rainbow"))

# Any styled/colored object works the same way
slow_print(ColorText("Warning!", foreground="red", styles=["bold"]), PrintOptions(speed=15, end=""))
```

`PrintOptions` fields:
- `speed` — visible characters per second (default `40`)
- `color` / `background` / `styles` — only used for plain strings; ignored on `ColorText`/`GradientText`/`StyledText`, which already carry their own coloring
- `end` — printed after the text finishes (default `"\n"`)
- `newline_delay` — extra pause after each `\n` in the text (default `0.5`)
- `flush` — flush the stream after every character (default `True`)
- `stream` — where to write to (default `sys.stdout`)

### Big Text

`LargeText` renders multi-row "banner" text from a small pixel font, in one of two styles:

```python
from codehs_utils import LargeText

# "block" (default): each font pixel becomes 2 terminal characters wide
print(LargeText("HI"))

# "pixel": packs 2 font rows per terminal row using half-block characters,
# so it comes out roughly half as tall for the same size
print(LargeText("HI", format="pixel"))

# Two font sizes: "5x7" (default, more detail) or "3x5" (compact)
print(LargeText("OK", font="3x5"))
```

Colors, gradients, and styles work the same way as `ColorText`/`GradientText` — `color`/`colors` paint the glyph strokes, `background`/`background_colors` fill the space around them:

```python
print(LargeText("WARNING", color="red", styles=["bold"]))
print(LargeText("RAINBOW", colors="rainbow", format="pixel"))
print(LargeText("HYPE", color="white", background="purple"))
```

`.wrap(width)` and `.align(width, align=)` work like `StyledText`'s, except wrapping only ever breaks between whole big characters — a single character is never split mid-glyph, so a line can still come out wider than `width` if one character alone doesn't fit:

```python
big = LargeText("HELLO WORLD", font="3x5", color="cyan")
print(big.wrap(40))
print(big.align(60, "center"))
```

Both fonts cover the full printable ASCII range (32–126: digits, `A`–`Z`, and punctuation). Letters are case-insensitive — lowercase renders using the uppercase glyph, since these fonts are too small to draw a separate lowercase form. Anything outside that range (like accented letters or emoji) just renders as a blank cell instead of raising. `LargeText.supported_chars(font="5x7")` lists every character a font can render.

### Cursor & Screen Control

```python
from codehs_utils import (
    clear_screen, clear_line, set_cursor_pos, set_cursor_row, set_cursor_col,
    move_cursor, save_cursor_position, restore_cursor_position,
    hide_cursor, show_cursor, get_cursor_position, get_terminal_size,
    enter_alt_screen, leave_alt_screen, restore_terminal,
)

# Clear the screen, or just the current line
clear_screen()
clear_line(mode="to_end")  # "full", "to_end", or "to_start"

# Move the cursor
set_cursor_pos(10, 5)   # absolute: row 10, column 5
set_cursor_row(10)
set_cursor_col(5)
move_cursor(dx=2, dy=-1)  # relative

# Save/restore cursor position
save_cursor_position()
restore_cursor_position()

# Hide/show the cursor
hide_cursor()
show_cursor()

# Read back state
row, col = get_cursor_position()
width, height = get_terminal_size()

# The alternate screen buffer (used internally by app())
enter_alt_screen()
leave_alt_screen()

# Manually undo everything (hide_cursor, alt screen, mouse tracking, raw
# mode) in one call — normally you'd just use app() instead
restore_terminal()
```

Lower-level output helpers, used internally but available directly:

```python
from codehs_utils import write, frame

write("some text")  # like print(), but no trailing newline and no `sep`

# Batch several writes into one flush, avoiding flicker/tearing
with frame():
    write("line one\n")
    write("line two\n")
```

### Text Formatting

```python
from codehs_utils import align_text, wrap_text

# Text alignment
text = "Hello World"
print(align_text(text, 20, "center"))   # Center align in 20 characters
print(align_text(text, 20, "right"))    # Right align
print(align_text(text, 20, "left"))     # Left align

# Word wrapping (ANSI-aware, so styled text still wraps correctly)
print(wrap_text("A long line of text that needs wrapping", width=15))
```

### Banners & Boxes

```python
from codehs_utils import banner, Banner, BannerRow

# A styled box of text
b = banner("Important Message", color="black", background="lightyellow")
print(b)

# Draw it at a specific position in an app()
b.draw(row=1, col=1)

# Lay banners out side by side
row = BannerRow([banner("One"), banner("Two"), banner("Three")])
print(row)

# Adjust spacing and vertical alignment between banners
row.set_gap(3).set_valign("middle")

# Align a whole banner (or row) within a wider field
print(b.align(width=40, align="right"))
```

### Rectangles & Pixels

```python
from codehs_utils import Rect, fill_rect, set_pixel, get_pixel_size

# Fill a rectangle
rect = fill_rect(row=1, col=1, width=10, height=3, color="blue")

# Draw a border around a Rect
rect.draw_border(color="cyan", style="double")

# Half-block pixel canvas
width, height = get_pixel_size()
set_pixel(x=5, y=5, color="red")
```

### Keyboard & Mouse Input

```python
from codehs_utils import get_key, get_keys, get_mouse_event, events, app, KeyEvent, MouseEvent

with app(mouse=True):
    for event in events(timeout=None):
        if isinstance(event, KeyEvent):
            print("Key pressed:", event.key)
        elif isinstance(event, MouseEvent):
            print("Mouse:", event.type, event.button, event.x, event.y)

# Blocking single-key read (outside an app(), still uses raw/cbreak mode)
key = get_key(timeout=5)

# Drain every key pressed so far without blocking
keys = get_keys()

# Just the next mouse event
mouse_event = get_mouse_event(timeout=1)
```

Mouse tracking can also be toggled manually, if you're not using `app()`:

```python
from codehs_utils import enable_mouse_tracking, disable_mouse_tracking

enable_mouse_tracking()
disable_mouse_tracking()
```

## Advanced Usage

### Custom Colors and Gradients

```python
from codehs_utils import ColorLike, GradientText

# Create ColorLike objects directly
purple = ColorLike((128, 64, 192))
print(purple.to_hex())

# List and preview all built-in gradient presets
print(GradientText.list_presets())
GradientText.preview_presets()
```

### Clickable Buttons

```python
from codehs_utils import Button, app, events

with app(mouse=True):
    button = Button("Click me", row=2, col=2, on_click=lambda: print("Clicked!"))
    button.draw()
    for event in events(timeout=10):
        if event is None:
            break
        # handle() updates hover/pressed state, redraws if it changed, fires
        # on_click when appropriate, and returns True exactly on that click
        button.handle(event)
```

### The `app()` Context Manager

```python
from codehs_utils import app

with app(mouse=True, cursor=False, clear=True, alt_screen=True):
    ...  # Terminal state is restored automatically on exit, even on Ctrl+C
```

## Reference

### Text Styles
Passed as `styles=[...]` to `ColorText`/`GradientText`, or via `.bold()`, `.italic()`, etc:
- `bold`
- `dim`
- `italic`
- `underline`
- `blink`
- `reverse`
- `strikethrough`

### Border Styles
Passed as `style=` to `Rect.draw_border()`:
- `single` — `┌─┐ └─┘`
- `double` — `╔═╗ ╚═╝`
- `rounded` — `╭─╮ ╰─╯`
- `heavy` — `┏━┓ ┗━┛`
- `ascii` — `+-+ +-+`

### Gradient Presets
Built into `GradientText`, usable by name (e.g. `GradientText.rainbow(...)`):
- `rainbow`, `fire`, `ocean`, `sunset`, `pastel`, `grayscale`, `neon`, `forest`, `mint`, `gold`

## API Reference

Every public name is re-exported from the top level (`import codehs_utils as c`), so the module path below is just for grouping — you don't need to import from it directly.

### Colors — `colors`

| Name | Description |
|---|---|
| `ColorLike(color)` | Parses a name, `"#hex"`, or `(r, g, b)` tuple into a normalized color |
| `ColorLike.rgb` | The parsed `(r, g, b)` tuple, or `None` |
| `ColorLike.to_hex()` | Returns `"#rrggbb"` |
| `ColorLike.luminance()` | Perceived brightness, 0.0–1.0 |
| `ColorLike.contrast()` | Black or white, whichever reads better on this color |
| `ColorLike.mix(other, t=0.5)` | Blends toward another color by ratio `t` |
| `ColorLike.lighten(amount=0.2)` / `.darken(amount=0.2)` | Mixes toward white / black |
| `ColorLike.print_samples()` | Prints every named color as a labeled banner |
| `ColorText(text, foreground=, background=, styles=, reset=)` | A single piece of solid-colored/styled text |
| `GradientText(text, colors=, color=, background=, background_colors=, styles=, reset=)` | Text with a foreground and/or background gradient |
| `GradientText.from_preset(text, preset="rainbow", **kwargs)` | Build from a named preset |
| `GradientText.rainbow(...)`, `.fire(...)`, `.ocean(...)`, `.sunset(...)`, `.pastel(...)`, `.grayscale(...)`, `.neon(...)`, `.forest(...)`, `.mint(...)`, `.gold(...)` | Shortcut constructors, one per built-in preset |
| `GradientText.list_presets()` | List of built-in preset names |
| `GradientText.preview_presets(sample_text=, print_output=True)` | Prints (and returns) a sample of every preset |
| `StyledText(parts=None)` | Concatenates strings/`ColorText`/`GradientText` into one object |
| `ColorSpec`, `GradientColors` | Type aliases used in the signatures above (not runtime objects) |

**Shared style methods** (on `ColorText` and `GradientText`, via `_StyleMixin`):

| Name | Description |
|---|---|
| `.bold()` `.dim()` `.italic()` `.underline()` `.blink()` `.reverse()` `.strikethrough()` | Turn on one style |
| `.add_style(name)` / `.remove_style(name)` | Turn a named style on/off |
| `.set_styles(*names)` | Replace the whole style list |
| `.set_text(text)` | Change the wrapped text |
| `.set_background(color)` | Set or clear the background color |
| `.set_reset(bool)` | Whether a trailing ANSI reset code is appended |
| `.set_color(color)` (`ColorText` only) | Set or clear the foreground color |
| `.set_colors(colors)` / `.set_background_gradient(colors)` (`GradientText` only) | Set the foreground / background gradient stops |

**`StyledText` methods:**

| Name | Description |
|---|---|
| `.wrap(width, collapse_space=True)` | ANSI-aware word wrap of the combined text |
| `.align(width, align="left", fillchar=" ")` | Align the combined text within `width` |

### Text — `text`

| Name | Description |
|---|---|
| `wrap_text(text, width, collapse_space=True, break_long_words=True, preserve_newlines=True)` | ANSI-aware word wrapping |
| `align_text(text, width, align="left", fillchar=" ")` | `"left"`, `"right"`, `"center"`, or `"justify"` alignment |

### Printing — `printing`

| Name | Description |
|---|---|
| `slow_print(text, options=None)` | Print `text` one visible character at a time; accepts a plain string or a `ColorText`/`GradientText`/`StyledText` |
| `PrintOptions(speed=40.0, color=None, background=None, styles=None, end="\n", newline_delay=0.5, flush=True, stream=sys.stdout)` | Settings for `slow_print`; `color`/`background`/`styles` only apply to plain strings |

### Big Text — `bigtext`

| Name | Description |
|---|---|
| `LargeText(text, font="5x7", format="block", color=, colors=, background=, background_colors=, styles=, spacing=1, cell_width=2)` | Multi-row banner text rendered from a pixel font. `font` is `"3x5"` or `"5x7"`; `format` is `"block"` (chunky) or `"pixel"` (half-block, ~half as tall) |
| `LargeText.width` / `.height` | Rendered size in terminal columns / rows |
| `LargeText.wrap(width)` | Wraps at whole-character boundaries only |
| `LargeText.align(width, align="left", fillchar=" ")` | Aligns each rendered row within `width` |
| `LargeText.draw(row, col)` | Draw at a position (wraps `print_at`) |
| `LargeText.supported_chars(font="5x7")` | Every character the font can render |



### Geometry — `geometry`

| Name | Description |
|---|---|
| `Rect(row, col, width, height)` | A rectangle; also returned by most drawing functions |
| `Rect.top` `.left` `.bottom` `.right` | Edge coordinates |
| `Rect.contains(x, y)` | Whether a point falls inside the rect |
| `Rect.fill(color=None, char=" ")` | Fill the rect (wraps `fill_rect`) |
| `Rect.draw_border(color=None, style="single", background=None)` | Draw a border around the rect |

### Drawing — `drawing`

| Name | Description |
|---|---|
| `Banner(lines)` | A block of text padded to a uniform width |
| `Banner.height` | Number of lines |
| `Banner.draw(row, col)` | Draw at a position, returns the `Rect` drawn |
| `Banner.align(width, align="left", fillchar=" ")` | Align the banner within a wider field |
| `BannerRow(banners, gap=1, valign="top")` | Lay several banners out side by side |
| `BannerRow.width` `.height` | Combined dimensions |
| `BannerRow.set_gap(gap)` / `.set_valign(valign)` | Adjust spacing / vertical alignment |
| `BannerRow.draw(row, col)` / `.align(width, align=, fillchar=)` | Same as on `Banner` |
| `banner(text, width=None, color=, colors=, background=, background_colors=, styles=, padding=1, align="center")` | Build a styled `Banner` in one call |
| `fill_rect(row, col, width, height, color=None, char=" ", foreground=None)` | Fill a rectangle directly, returns a `Rect` |
| `get_pixel_size()` | Terminal size in half-block pixels (`(width, height * 2)`) |
| `set_pixel(x, y, color)` / `clear_pixel(x, y)` / `clear_pixels()` | Half-block pixel canvas |
| `Button(text, row, col, width=, background=, color=, hover_background=, hover_color=, pressed_background=, pressed_color=, padding=1, styles=, trigger="release", on_click=)` | A clickable button |
| `Button.draw()` | (Re)draw the button in its current state |
| `Button.handle(event)` | Update state from a `MouseEvent`, redraw if needed, fire `on_click`; returns `True` on a completed click |

### Terminal — `terminal`

| Name | Description |
|---|---|
| `app(mouse=False, cursor=False, clear=True, alt_screen=True, catch_interrupt=True)` | Context manager: sets up and tears down an interactive session |
| `MouseEvent` | `.type`, `.button`, `.x`, `.y`, `.shift`, `.alt`, `.ctrl`; `.inside(rect)` |
| `KeyEvent` | `.key`; compares equal to a plain string |
| `get_key(timeout=None)` | Block for a single keypress |
| `get_keys()` / `get_key_nonblocking()` | Drain all buffered keys without blocking |
| `get_mouse_event(timeout=None)` / `get_mouse_event_nonblocking()` | Get the next mouse event |
| `get_event(timeout=None)` | Get the next key **or** mouse event |
| `events(timeout=None)` | Infinite iterator over `get_event()` |
| `get_cursor_position()` / `gcp` | Query the cursor's current position (`gcp` is an alias) |
| `get_terminal_size()` | `(width, height)` in characters |
| `clear_screen(scrollback=True)` / `clear_line(mode="full")` | Clear the screen / current line |
| `set_cursor_pos(row, col)` / `set_cursor_row(row)` / `set_cursor_col(col)` | Absolute cursor positioning |
| `move_cursor(dx=0, dy=0)` | Relative cursor movement |
| `save_cursor_position()` / `restore_cursor_position()` | Push/pop cursor position |
| `hide_cursor()` / `show_cursor()` | Toggle cursor visibility |
| `enter_alt_screen()` / `leave_alt_screen()` | Toggle the alternate screen buffer |
| `enable_mouse_tracking()` / `disable_mouse_tracking()` | Toggle mouse event reporting |
| `print_at(row, col, text, clear_to_end=False)` | Print (possibly multi-line) text at a position, returns a `Rect` |
| `restore_terminal()` | Undo cursor/mouse/alt-screen/raw-mode state in one call |

### Output buffering — `_buffer` (re-exported)

| Name | Description |
|---|---|
| `write(*parts, sep="", flush=True)` | Like `print()`, but no newline and writes go through the frame buffer |
| `frame(sync=False)` | Context manager: batch writes into a single flush |

## Requirements

- Python 3.8+
- No third-party dependencies

## Examples

### Create a Colorful Banner

```python
from codehs_utils import banner, clear_screen, GradientText

clear_screen()
print(banner("WELCOME", color="black", background="lightgreen"))
print()
print(GradientText.rainbow("- Terminal Toolkit Demo -"))
print(GradientText.rainbow("=" * 50))
```

### Simple Paint Program

```python
from codehs_utils import app, events, set_pixel

with app(mouse=True):
    for event in events(timeout=None):
        if event is None or (event.kind == "key" and event.key == "ESC"):
            break
        if event.kind == "mouse" and event.button == "left":
            set_pixel(event.x, event.y, "red")
```

### Bordered Dialog Box

```python
from codehs_utils import Rect, print_at

box = Rect(row=3, col=5, width=30, height=6)
box.fill(color="black")
box.draw_border(color="white", style="rounded")
print_at(box.row + 2, box.col + 2, "Press any key to continue...")
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.