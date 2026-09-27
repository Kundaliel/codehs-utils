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
