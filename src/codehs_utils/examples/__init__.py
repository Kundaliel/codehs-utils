"""Runnable examples for :mod:`codehs_utils`.

Every module in this subpackage is a small, self-contained script that
prints something to the terminal using one corner of the library. They're
meant to be read as much as run -- open one up and copy from it.

Each example exposes a ``run()`` function with no required arguments, so
you can pull one in and run it like this:

    from codehs_utils.examples import colors_demo
    colors_demo.run()

That pattern works everywhere, including on CodeHS, where you can't
launch a script with a command line (``python -m ...``).
"""

#: name -> one-line description, in the order they're listed in the README.
#: Kept as plain data (rather than importing every module up front) so
#: ``import codehs_utils.examples`` stays cheap and side-effect-free.
EXAMPLES = {
    "colors_demo": "Named colors, hex, RGB, mixing, lighten/darken/contrast.",
    "gradients_demo": "GradientText presets, custom stops, gradient backgrounds.",
    "banners_demo": "banner() boxes, side-by-side layout, and alignment.",
    "bigtext_demo": "LargeText: big pixel-font banners, block and half-block styles.",
    "slow_print_demo": "Typewriter-style output with slow_print().",
    "drawing_demo": "fill_rect() and the half-block pixel canvas (set_pixel).",
    "buttons_demo": "A mouse-driven app: clickable Button widgets, ESC to quit.",
    "keyboard_demo": "A keyboard-driven app: move a character with arrow keys.",
}

__all__ = ["EXAMPLES"]
