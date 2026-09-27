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
