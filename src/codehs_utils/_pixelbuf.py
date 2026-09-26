"""Shared half-block pixel-canvas state.

Kept in its own module (rather than in `.terminal` or `.drawing`) because
both of those modules touch it: `.terminal` clears it on `clear_screen`,
`enter_alt_screen`, and `leave_alt_screen`, while `.drawing` reads and
writes it for `set_pixel`/`clear_pixel`/`clear_pixels`. Keeping it here
avoids either module needing to import the other just for this dict.
"""

_pixel_buf: dict = {}
