# codehs-utils

[![PyPI version](https://badge.fury.io/py/codehs-utils.svg)](https://badge.fury.io/py/codehs-utils)
[![Python versions](https://img.shields.io/pypi/pyversions/codehs-utils.svg)](https://pypi.org/project/codehs-utils/)

A Python library for terminal colors, gradients, banners, drawing, and keyboard/mouse input, originally built for CodeHS's Python environment.

## Features

- RGB, hex, and named colors for foreground and background, with mixing, lightening, and darkening
- Gradient text with built-in presets such as rainbow, fire, ocean, and sunset
- Typewriter-style slow printing with support for gradients and styles
- Large multi-row banner text rendered from a 3x5 or 5x7 pixel font, in block or half-block pixel style
- Composable text banners and boxes with alignment and side-by-side layout
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

# Run a seperate program without clearing the previously drawn banner
with c.app(mouse=True):
    c.banner("Click anywhere to place a character, waiting 5 seconds or pressing escape will exit").draw(1, 1)
    for event in c.events(timeout=5):
        if isinstance(event, c.MouseEvent) and event.type == 'press':
            x, y = event.x, event.y
            c.print_at(y, x, "|")
            
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

Two colors can be blended with `.mix()`, which `.lighten()` and `.darken()` also use internally:

```python
from codehs_utils import ColorLike

blend = ColorLike("red").mix("blue", t=0.5)  # 50/50 blend
print(blend.to_hex())
```

### Style Methods

`ColorText` and `GradientText` share a set of chainable style methods (from their common `_StyleMixin`). These allow styled text to be built incrementally instead of passing every option to the constructor:

```python
from codehs_utils import ColorText

msg = ColorText("warning!").bold().underline()
msg.set_background("red")
print(msg)
```

Available chainable methods:
- `.bold()`, `.italic()`, `.underline()`, `.strikethrough()`, `.dim()`, `.blink()`, `.reverse()`: Turn on a single style
- `.add_style(name)` / `.remove_style(name)`: Turn a named style on or off
- `.set_styles(*names)`: Replace the whole style list at once
- `.set_text(text)`: Change the wrapped text
- `.set_background(color)`: Set or clear the background color
- `.set_reset(bool)`: Set whether an ANSI reset code is appended after the text (default `True`)

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

`slow_print` reveals text one visible character at a time, like a typewriter. It accepts a plain string or any `ColorText`, `GradientText`, or `StyledText` object. Gradients keep the correct color at each position as the text is printed, rather than being limited to a single flat color:

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
- `speed`: Visible characters per second (default `40`)
- `color` / `background` / `styles`: Applied only to plain strings. Ignored for `ColorText`, `GradientText`, and `StyledText`, which already carry their own coloring
- `end`: Text printed after the output finishes (default `"\n"`)
- `newline_delay`: Extra pause after each `\n` in the text (default `0.5`)
- `flush`: Whether to flush the stream after every character (default `True`)
- `stream`: Output stream to write to (default `sys.stdout`)

### Big Text

`LargeText` renders multi-row "banner" text from a small pixel font, in one of two styles:

```python
from codehs_utils import LargeText, write

# "block" (default): each font pixel becomes 2 terminal characters wide
print(LargeText("HI"))

write('\n')

# "pixel": packs 2 font rows per terminal row using half-block characters,
# so it comes out roughly half as tall for the same size
print(LargeText("HI", format="pixel"))

write('\n')

# Two font sizes: "5x7" (default, more detail) or "3x5" (compact)
print(LargeText("OK", font="3x5"))
```

Colors, gradients, and styles work the same way as in `ColorText` and `GradientText`. The `color` and `colors` parameters set the glyph strokes, and `background` and `background_colors` fill the space around them:

```python
print(LargeText("WARNING", color="red", styles=["bold"]))
print(LargeText("RAINBOW", colors="rainbow", format="pixel"))
print(LargeText("HYPE", color="white", background="purple"))
```

`.wrap(width)` and `.align(width, align=)` work like their `StyledText` counterparts, except that wrapping only breaks between whole characters. A single character is never split, so a line can be wider than `width` if one character alone does not fit:

```python
big = LargeText("HELLO WORLD", font="3x5", color="cyan")
print(big.wrap(40))
print(big.align(60, "center"))
```

Both fonts cover the full printable ASCII range (32–126: digits, `A`–`Z`, and punctuation). Letters are case-insensitive: lowercase letters render using the uppercase glyphs, because the fonts are too small to draw a separate lowercase form. Characters outside that range, such as accented letters or emoji, render as a blank cell instead of raising an error. `LargeText.supported_chars(font="5x7")` lists every character a font can render.

### Cursor & Screen Control

```python
from codehs_utils import (
    clear_screen, clear_line, set_cursor_pos, set_cursor_row, set_cursor_col,
    move_cursor, save_cursor_position, restore_cursor_position,
    hide_cursor, show_cursor, get_cursor_position, get_terminal_size,
    enter_alt_screen, leave_alt_screen, restore_terminal,
)

import time


def pause(seconds=1.5):
    time.sleep(seconds)


def title(text):
    """Show a step title at the top of the screen."""
    clear_screen()
    set_cursor_pos(1, 1)
    print(f"=== {text} ===")


# ---------------------------------------------------------------
# Clear the screen, or just the current line
# ---------------------------------------------------------------
title("clear_screen()")
print("This text is about to disappear...")
pause()
clear_screen()
set_cursor_pos(1, 1)
print("Screen cleared!")
pause()

title("clear_line()")
set_cursor_pos(3, 1)
print("Line A: this line stays untouched")
print("Line B: the cursor will sit in the middle of this line")
print("Line C: this line stays untouched")
pause()

set_cursor_pos(4, 20)
print("<-- cursor here", end="", flush=True)
pause()

set_cursor_pos(4, 20)
clear_line(mode="to_end")
print("[to_end wiped everything to the right]", end="", flush=True)
pause()

set_cursor_pos(4, 20)
clear_line(mode="to_start")
set_cursor_pos(4, 1)
print("[to_start wiped everything to the left]", end="", flush=True)
pause()

clear_line(mode="full")
set_cursor_pos(4, 1)
print("[full wiped the whole line, then I typed this]", end="", flush=True)
pause(2)

# ---------------------------------------------------------------
# Move the cursor
# ---------------------------------------------------------------
title("set_cursor_pos(row, col)")
set_cursor_pos(10, 5)
print("X  <- printed at row 10, column 5", end="", flush=True)
pause()

set_cursor_pos(3, 30)
print("Y  <- printed at row 3, column 30", end="", flush=True)
pause()

title("set_cursor_row() / set_cursor_col()")
set_cursor_pos(5, 1)
print("Starting on row 5", end="", flush=True)
pause()
set_cursor_row(8)
print("Jumped to row 8 (column kept)", end="", flush=True)
pause()
set_cursor_col(40)
print("Jumped to column 40", end="", flush=True)
pause(2)

title("move_cursor(dx, dy)  (relative)")
set_cursor_pos(10, 20)
print("O", end="", flush=True)  # start marker
pause(1)
# Trace a small path with relative moves
steps = [(2, 0), (2, 0), (0, 1), (0, 1), (-2, 0), (-2, 0), (0, -1)]
for dx, dy in steps:
    move_cursor(dx=dx, dy=dy)
    print("*", end="", flush=True)
    pause(0.4)
pause(1.5)

# ---------------------------------------------------------------
# Save / restore cursor position
# ---------------------------------------------------------------
title("save_cursor_position() / restore_cursor_position()")
set_cursor_pos(5, 10)
print("Saving position here -> ", end="", flush=True)
save_cursor_position()
pause()

set_cursor_pos(12, 10)
print("Wandered off to row 12...", end="", flush=True)
pause()

restore_cursor_position()
print("[back at the saved spot!]", end="", flush=True)
pause(2)

# ---------------------------------------------------------------
# Hide / show the cursor
# ---------------------------------------------------------------
title("hide_cursor() / show_cursor()")
set_cursor_pos(4, 1)
print("Cursor is visible now (look for the blinking block).")
pause(2)

hide_cursor()
set_cursor_pos(6, 1)
print("Cursor is now HIDDEN.")
pause(2)

show_cursor()
set_cursor_pos(8, 1)
print("Cursor is visible again.")
pause(2)

# ---------------------------------------------------------------
# Read back state
# ---------------------------------------------------------------
title("get_cursor_position() / get_terminal_size()")
set_cursor_pos(7, 15)
row, col = get_cursor_position()
width, height = get_terminal_size()

set_cursor_pos(3, 1)
print(f"I moved the cursor to (7, 15) and it reports: row={row}, col={col}")
print(f"Terminal size: width={width}, height={height}")
pause(3)

# ---------------------------------------------------------------
# The alternate screen buffer
# ---------------------------------------------------------------
title("Before entering the alternate screen")
set_cursor_pos(3, 1)
print("This is the NORMAL screen. Watch it get swapped out...")
pause(2)

enter_alt_screen()
clear_screen()
set_cursor_pos(1, 1)
print("=== ALTERNATE SCREEN ===")
print("This is a totally separate buffer.")
print("Your normal screen content is hidden, not erased.")
pause(3)

leave_alt_screen()
set_cursor_pos(5, 1)
print("Back on the normal screen. The earlier text is still here!")
pause(3)

# ---------------------------------------------------------------
# Restore the terminal
# ---------------------------------------------------------------
title("restore_terminal()")
set_cursor_pos(3, 1)
print("Hiding the cursor and entering the alt screen...")
hide_cursor()
enter_alt_screen()
pause(1.5)

set_cursor_pos(1, 1)
print("Now in alt screen with the cursor hidden.")
print("Calling restore_terminal() in 2 seconds...")
pause(2)

restore_terminal()
print("Everything restored: cursor visible, normal screen back.")
pause(2)

print("Demo complete!")
```

Lower-level output helpers, used internally but available directly:

```python
from codehs_utils import write, frame

write("some text")  # like print(), but no trailing newline and no `sep`
write(", same line\n")

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
from codehs_utils import Rect, fill_rect, set_pixel, get_pixel_size, clear_screen

# Clear the screen before printing
clear_screen()

# Fill a rectangle
rect = fill_rect(row=1, col=1, width=10, height=3, color="blue")

# Draw a border around a Rect
rect.draw_border(color="cyan", style="double")

# Half-block pixel canvas
width, height = get_pixel_size()
set_pixel(x=10, y=10, color="red")

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

If you are not using `app()`, mouse tracking can be toggled manually:

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
    button = Button("Click me", row=2, col=2, on_click=lambda: print("\nClicked!"))
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
Passed as `styles=[...]` to `ColorText` or `GradientText`, or set through the style methods such as `.bold()` and `.italic()`:
- `bold`
- `dim`
- `italic`
- `underline`
- `blink`
- `reverse`
- `strikethrough`

### Border Styles
Passed as `style=` to `Rect.draw_border()`:
- `single`: `┌─┐ └─┘`
- `double`: `╔═╗ ╚═╝`
- `rounded`: `╭─╮ ╰─╯`
- `heavy`: `┏━┓ ┗━┛`
- `ascii`: `+-+ +-+`

### Gradient Presets
Built into `GradientText` and available by name, for example `GradientText.rainbow(...)`:
- `rainbow`, `fire`, `ocean`, `sunset`, `pastel`, `grayscale`, `neon`, `forest`, `mint`, `gold`

## API Reference

Every public name is re-exported from the top level (`import codehs_utils as c`). The module names in the headings below are for grouping only. Names do not need to be imported from them directly.

### Colors (`colors`)

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
| `.align(width, align="left", fillchar=None)` | Align the combined text within `width` |

### Text (`text`)

| Name | Description |
|---|---|
| `wrap_text(text, width, collapse_space=True, break_long_words=True, preserve_newlines=True)` | ANSI-aware word wrapping |
| `align_text(text, width, align="left", fillchar=None)` | `"left"`, `"right"`, `"center"`, or `"justify"` alignment |

### Printing (`printing`)

| Name | Description |
|---|---|
| `slow_print(text, options=None)` | Print `text` one visible character at a time; accepts a plain string or a `ColorText`/`GradientText`/`StyledText` |
| `PrintOptions(speed=40.0, color=None, background=None, styles=None, end="\n", newline_delay=0.5, flush=True, stream=sys.stdout)` | Settings for `slow_print`; `color`/`background`/`styles` only apply to plain strings |

### Big Text (`bigtext`)

| Name | Description |
|---|---|
| `LargeText(text, font="5x7", format="block", color=, colors=, background=, background_colors=, styles=, spacing=1, cell_width=2)` | Multi-row banner text rendered from a pixel font. `font` is `"3x5"` or `"5x7"`; `format` is `"block"` (chunky) or `"pixel"` (half-block, ~half as tall) |
| `LargeText.width` / `.height` | Rendered size in terminal columns / rows |
| `LargeText.wrap(width)` | Wraps at whole-character boundaries only |
| `LargeText.align(width, align="left", fillchar=None)` | Aligns each rendered row within `width` |
| `LargeText.draw(row, col)` | Draw at a position (wraps `print_at`) |
| `LargeText.supported_chars(font="5x7")` | Every character the font can render |



### Geometry (`geometry`)

| Name | Description |
|---|---|
| `Rect(row, col, width, height)` | A rectangle; also returned by most drawing functions |
| `Rect.top` `.left` `.bottom` `.right` | Edge coordinates |
| `Rect.contains(x, y)` | Whether a point falls inside the rect |
| `Rect.fill(color=None, char=" ")` | Fill the rect (wraps `fill_rect`) |
| `Rect.draw_border(color=None, style="single", background=None)` | Draw a border around the rect |

### Drawing (`drawing`)

| Name | Description |
|---|---|
| `Banner(lines)` | A block of text padded to a uniform width |
| `Banner.height` | Number of lines |
| `Banner.draw(row, col)` | Draw at a position, returns the `Rect` drawn |
| `Banner.align(width, align="left", fillchar=None)` | Align the banner within a wider field |
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

### Terminal (`terminal`)

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

### Output Buffering (`_buffer`, re-exported)

| Name | Description |
|---|---|
| `write(*parts, sep="", flush=True)` | Like `print()`, but no newline and writes go through the frame buffer |
| `frame(sync=False)` | Context manager: batch writes into a single flush |

## Requirements

- Python 3.8+
- No third-party dependencies

## Examples

The snippets below are short examples. For complete, runnable scripts, see the
[`codehs_utils.examples`](#runnable-examples) package described in the next section.

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
from codehs_utils import app, print_at, events, ColorText, get_terminal_size, fill_rect
PALETTE = ['white', 'black', 'gray', 'red', 'mistyrose',
           'green', 'blue', 'orange', 'yellow', 'purple']
width, height = get_terminal_size()

def clear():
    fill_rect(0, 0, width, height, 'white')
    fill_rect(1, width - 1, 2, 1, color)

def change_color(n):
    color = PALETTE[n]
    fill_rect(1, width - 1, 2, 1, color)
    return color
    

held = False

with app(mouse=True):
    color = PALETTE[1]
    clear()
    for event in events():
        if event == "q":
            break

        if event.kind == 'key':
            if len(event.key) == 1 and '0' <= event.key <= '9':
                color = change_color(int(event.key))
            if event.key == 'c':
                clear()

        elif event.kind == 'mouse':
            if event.button == 'left':
                if event.type == 'press':
                    held = True
                elif event.type == 'release':
                    held = False
            if held and not event.type.startswith('wheel'):
                col = (event.x - 1) // 2 * 2 + 1
                fill_rect(event.y, col, 2, 1, color)
```

### Bordered Dialog Box

```python
from codehs_utils import Rect, print_at, ColorLike, ColorText

background = ColorLike('black')
color = background.contrast()
message = ColorText("Press any key to continue...", color, background)

box = Rect(row=3, col=5, width=len(message)+4, height=5)
box.fill(color=background)
box.draw_border(color=color, background=background)
print_at(box.row + 2, box.col + 2, message)
```

### Runnable Examples

The package includes a `codehs_utils.examples` subpackage with one self-contained script per feature area. Each module exposes a `run()` function, so an example can be run directly after importing it, without using the command line. This also makes the examples usable on CodeHS:

```python
from codehs_utils.examples import colors_demo

colors_demo.run()
```

The full source for each example is listed below.

#### `colors_demo`: Named colors, hex, RGB, mixing, lighten/darken/contrast

```python
from codehs_utils.examples import colors_demo

colors_demo.run()
```

Source code for the `colors_demo`:

```python
"""Named colors, hex, RGB, mixing, lighten/darken/contrast.

    from codehs_utils.examples import colors_demo
    colors_demo.run()
"""

import codehs_utils as c
from codehs_utils import ColorLike, ColorText


def run() -> None:
    # Three ways to specify the same color.
    named = ColorLike("tomato")
    hexed = ColorLike("#ff6347")
    rgb = ColorLike((255, 99, 71))
    print(ColorText(f"named == hex == rgb : {named == hexed == rgb}"))

    # Foreground and background.
    print(ColorText("white text on a blue background", foreground="white", background="blue"))

    # Bold/underline/etc. via the shared style methods.
    print(ColorText("bold + underline").bold().underline().set_color("cyan"))

    # Lighten / darken / mix, and picking a readable text color for a swatch.
    base = ColorLike("forestgreen")
    print(ColorText(f"  lighter  ", background=base.lighten(0.4)).set_color(base.lighten(0.4).contrast()))
    print(ColorText(f"  base     ", background=base).set_color(base.contrast()))
    print(ColorText(f"  darker   ", background=base.darken(0.4)).set_color(base.darken(0.4).contrast()))

    blend = ColorLike("red").mix("blue", t=0.5)
    print(ColorText(f"  50/50 red+blue = {blend.to_hex()}  ", background=blend).set_color(blend.contrast()))


if __name__ == "__main__":
    run()
```

#### `gradients_demo`: GradientText presets, custom stops, gradient backgrounds

```python
from codehs_utils.examples import gradients_demo

gradients_demo.run()
```

Source code for the `gradients_demo`:

```python
"""GradientText presets, custom stops, and gradient backgrounds.

    from codehs_utils.examples import gradients_demo
    gradients_demo.run()
"""

from codehs_utils import GradientText


def run() -> None:
    # Every built-in preset has a shortcut classmethod...
    print(GradientText.rainbow("This text has rainbow colors!"))
    print(GradientText.fire("Fire preset"))
    print(GradientText.ocean("Ocean preset"))

    # ...which is just a thin wrapper around from_preset().
    print(GradientText.from_preset("Same thing via from_preset()", preset="sunset"))

    # Custom stops instead of a preset.
    print(GradientText("Custom stops: red -> orange -> yellow", colors=["red", "orange", "yellow"]))

    # The gradient can live on the background instead of the text.
    print(GradientText("Rainbow background!", background_colors="rainbow", color="black"))

    # Styles stack the same way ColorText's do.
    print(GradientText("Bold rainbow", colors="rainbow").bold())

    print("\nEvery available preset:", ", ".join(GradientText.list_presets()))


if __name__ == "__main__":
    run()
```

#### `banners_demo`: banner() boxes, side-by-side layout, and alignment

```python
from codehs_utils.examples import banners_demo

banners_demo.run()
```

Source code for the `banners_demo`:

```python
"""banner() boxes, side-by-side layout, and alignment.

    from codehs_utils.examples import banners_demo
    banners_demo.run()
"""

from codehs_utils import banner


def run() -> None:
    # A simple colored box.
    print(banner("Hello, World!", color="white", background="blue"))

    # Banners can be added together to sit side by side...
    left = banner("LEFT", background="darkred", color="white")
    right = banner("RIGHT", background="darkgreen", color="white")
    row = left + right
    print(row)

    # ...and a BannerRow can be aligned within a wider space.
    print(row.align(60, align="center"))
    print(row.align(60, align="justify"))

    # width/padding/align control the box itself.
    print(banner("centered, padding=2", width=40, padding=2, align="center", background="purple", color="white"))
    print(banner("left aligned", width=40, align="left", background="purple", color="white"))


if __name__ == "__main__":
    run()
```

#### `bigtext_demo`: LargeText big pixel-font banners, block and half-block styles

```python
from codehs_utils.examples import bigtext_demo

bigtext_demo.run()
```

Source code for the `bigtext_demo`:

```python
"""LargeText: big pixel-font banners, block and half-block styles.

    from codehs_utils.examples import bigtext_demo
    bigtext_demo.run()
"""

from codehs_utils import LargeText


def run() -> None:
    # "block" format: chunky, one font-pixel per `cell_width` columns.
    big = LargeText("HI", font="5x7", format="block", colors="rainbow")
    print(big.render())

    # "pixel" format packs two font rows per terminal row (half-block
    # characters), so it comes out roughly half as tall for the same size.
    print()
    small_font = LargeText("OK", font="3x5", format="pixel", color="lime")
    print(small_font.render())

    # A gradient background instead of a gradient foreground.
    print()
    bg = LargeText("GO", font="5x7", color="black", background_colors="fire")
    print(bg.render())

    print("\nCharacters the 5x7 font supports:", LargeText.supported_chars("5x7"))


if __name__ == "__main__":
    run()
```

#### `slow_print_demo`: Typewriter-style output with slow_print()

```python
from codehs_utils.examples import slow_print_demo

slow_print_demo.run()
```

Source code for the `slow_print_demo`:

```python
"""Typewriter-style output with slow_print().

    from codehs_utils.examples import slow_print_demo
    slow_print_demo.run()
"""

from codehs_utils import slow_print, PrintOptions, GradientText


def run() -> None:
    # A plain string, colored via PrintOptions since it's not already
    # a ColorText/GradientText.
    slow_print("Loading", PrintOptions(speed=20, color="cyan", end=""))
    slow_print("...", PrintOptions(speed=4, color="cyan"))

    # A GradientText keeps its per-character coloring while it types out.
    slow_print(GradientText("Rainbow, one letter at a time!", colors="rainbow"), PrintOptions(speed=25))

    # newline_delay adds an extra pause after each line break -- handy for
    # a multi-line "story" effect.
    story = "Once upon a time...\nthere was a terminal.\nThe end."
    slow_print(story, PrintOptions(speed=35, newline_delay=0.6, color="yellow"))


if __name__ == "__main__":
    run()
```

#### `drawing_demo`: fill_rect() and the half-block pixel canvas (set_pixel)

```python
from codehs_utils.examples import drawing_demo

drawing_demo.run()
```

Source code for the `drawing_demo`:

```python
"""fill_rect() and the half-block pixel canvas (set_pixel).

    from codehs_utils.examples import drawing_demo
    drawing_demo.run()
"""

from codehs_utils import clear_screen, print_at, fill_rect, set_pixel, ColorLike


def run() -> None:
    clear_screen()

    # A couple of filled rectangles. fill_rect() returns the Rect it drew,
    # which you can reuse (e.g. Rect.contains(x, y) for hit-testing).
    fill_rect(2, 2, width=20, height=4, color="steelblue")
    box = fill_rect(2, 26, width=20, height=4, color="indianred", char="#")
    print_at(7, 2, f"Second box: {box}")  # Rect(row=2, col=26, width=20, height=4)

    # The half-block pixel canvas: each terminal cell holds two "pixels"
    # (top half + bottom half), so you get roughly square pixels instead
    # of the usual tall/narrow terminal cells. Coordinates are 1-based, and
    # y counts pixels (2 per terminal row): terminal row r covers y = 2r-1
    # and y = 2r. So to start the circle at terminal row 9, start at y = 17.
    top_row, left = 9, 2
    top = 2 * top_row - 1
    red = ColorLike("red")
    for y in range(10):
        for x in range(10):
            # A simple filled circle.
            if (x - 4.5) ** 2 + (y - 4.5) ** 2 <= 20:
                set_pixel(left + x, top + y, red)

    print_at(top_row + 6, 2, "A circle drawn one half-block pixel at a time.")


if __name__ == "__main__":
    run()
```

#### `buttons_demo`: A mouse-driven app with clickable Button widgets

```python
from codehs_utils.examples import buttons_demo

buttons_demo.run()
```

Source code for the `buttons_demo`:

```python
"""A mouse-driven app: clickable Button widgets, ESC to quit.

    from codehs_utils.examples import buttons_demo
    buttons_demo.run()

Click the buttons; the label banner updates to show the last click.
Press ESC (or close the terminal) to exit cleanly -- `app()` always
restores your terminal on the way out, even after an error.
"""

import codehs_utils as c


def run() -> None:
    clicks = {"count": 0}

    def make_handler(label: str):
        def handler():
            clicks["count"] += 1
            status.text = f"You clicked '{label}'! (total clicks: {clicks['count']})"
            redraw_status()
        return handler

    with c.app(mouse=True):
        title = c.banner("Click a button below. ESC to quit.", background="navy", color="white")
        title.draw(1, 2)

        status = c.banner(" " * 40, background="black", color="white")

        def redraw_status():
            status.draw(4, 2)

        redraw_status()

        buttons = [
            c.Button("Red", row=7, col=2, background="crimson", on_click=make_handler("Red")),
            c.Button("Green", row=7, col=14, background="forestgreen", on_click=make_handler("Green")),
            c.Button("Blue", row=7, col=28, background="royalblue", on_click=make_handler("Blue")),
        ]
        for b in buttons:
            b.draw()

        for event in c.events():
            if event is None:
                continue
            if event.kind == "key" and event.key == "ESC":
                break
            for b in buttons:
                b.handle(event)


if __name__ == "__main__":
    run()
```

#### `keyboard_demo`: A keyboard-driven app (move a character with arrow keys)

```python
from codehs_utils.examples import keyboard_demo

keyboard_demo.run()
```

Source code for the `keyboard_demo`:

```python
"""A keyboard-driven app: move a character with arrow keys.

    from codehs_utils.examples import keyboard_demo
    keyboard_demo.run()

Use the arrow keys to move the '@' around. Press ESC to quit.
"""

import codehs_utils as c

_MOVES = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}


def run() -> None:
    width, height = c.get_terminal_size()
    x, y = width // 2, height // 2

    with c.app():
        c.banner("Arrow keys to move, ESC to quit.", background="darkslategray", color="white").draw(1, 1)
        c.print_at(y, x, "@")

        while True:
            key = c.get_key(timeout=None)
            if key == "ESC":
                break
            move = _MOVES.get(key)
            if move is None:
                continue

            c.print_at(y, x, " ")  # erase the old position
            dx, dy = move
            x = max(1, min(width, x + dx))
            y = max(4, min(height, y + dy))  # stay clear of the banner
            c.print_at(y, x, "@")


if __name__ == "__main__":
    run()
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing

Contributions are welcome. To contribute, please submit a pull request.