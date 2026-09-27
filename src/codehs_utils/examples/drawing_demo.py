"""fill_rect() and the half-block pixel canvas (set_pixel).

    from codehs_utils.examples import drawing_demo
    drawing_demo.run()
"""

from codehs_utils import clear_screen, set_cursor_pos, fill_rect, set_pixel, ColorLike


def run() -> None:
    clear_screen()

    # A couple of filled rectangles. fill_rect() returns the Rect it drew,
    # which you can reuse (e.g. Rect.contains(x, y) for hit-testing).
    fill_rect(2, 2, width=20, height=4, color="steelblue")
    box = fill_rect(2, 26, width=20, height=4, color="indianred", char="#")
    print(f"\nSecond box: {box}")  # Rect(row=2, col=26, width=20, height=4)

    # The half-block pixel canvas: each terminal cell holds two "pixels"
    # (top half + bottom half), so you get roughly square pixels instead
    # of the usual tall/narrow terminal cells. Coordinates are 1-based.
    top, left = 8, 2
    red = ColorLike("red")
    for y in range(10):
        for x in range(10):
            # A simple filled circle.
            if (x - 4.5) ** 2 + (y - 4.5) ** 2 <= 20:
                set_pixel(left + x, top + y, red)

    set_cursor_pos(top + 6, 1)
    print("A circle drawn one half-block pixel at a time.")


if __name__ == "__main__":
    run()
