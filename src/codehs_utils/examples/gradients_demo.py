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
