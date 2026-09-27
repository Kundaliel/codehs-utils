"""banner() boxes, side-by-side layout, and alignment.

    from codehs_utils.examples import banners_demo
    banners_demo.run()
"""

from codehs_utils import banner


def run() -> None:
    # A simple colored box.
    print(banner("Hello, World!", color="white", background="blue"))

    # Banners can be added together to sit side by side...
    left = banner("LEFT", background="darkred", color="white")
    right = banner("RIGHT", background="darkgreen", color="white")
    row = left + right
    print(row)

    # ...and a BannerRow can be aligned within a wider space.
    print(row.align(60, align="center"))
    print(row.align(60, align="justify"))

    # width/padding/align control the box itself.
    print(banner("centered, padding=2", width=40, padding=2, align="center", background="purple", color="white"))
    print(banner("left aligned", width=40, align="left", background="purple", color="white"))


if __name__ == "__main__":
    run()
