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
