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
