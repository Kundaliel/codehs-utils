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
