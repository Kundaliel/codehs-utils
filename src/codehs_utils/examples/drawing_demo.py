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
