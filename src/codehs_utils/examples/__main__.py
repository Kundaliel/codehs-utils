"""CLI runner for :mod:`codehs_utils.examples`.

    python -m codehs_utils.examples            # list every example
    python -m codehs_utils.examples NAME        # run one example by name
    python -m codehs_utils.examples --all       # run all of them, in order
"""

import importlib
import sys

from . import EXAMPLES


def _print_list():
    print("Available codehs_utils examples:\n")
    for name, blurb in EXAMPLES.items():
        print(f"  {name:<18} {blurb}")
    print("\nRun one with:  python -m codehs_utils.examples <name>")


def _run(name: str) -> int:
    if name not in EXAMPLES:
        print(f"Unknown example: '{name}'\n", file=sys.stderr)
        _print_list()
        return 1
    module = importlib.import_module(f".{name}", __package__)
    module.run()
    return 0


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv

    if not argv or argv[0] in ("-h", "--help"):
        _print_list()
        return 0

    if argv[0] == "--all":
        for name in EXAMPLES:
            print(f"\n{'=' * 60}\n{name}\n{'=' * 60}")
            _run(name)
        return 0

    return _run(argv[0])


if __name__ == "__main__":
    raise SystemExit(main())
