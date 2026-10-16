#!/usr/bin/env python3
"""Make a small made-up folder tree for the path length lesson.

One file sits deep inside folders with long names, so its full path is
more than 260 characters on any machine. Nothing here is real.
"""

import os

TREE = [
    "Project archive copied from the old shared drive",
    "Backup of the marketing folder before the office move",
    "Campaign photos and draft leaflets for the spring launch",
    "Final versions approved and sent to the print shop",
]
DEEP_FILE = "Read me first - printing notes for the leaflets.txt"


def main():
    base = "sample"
    os.makedirs(base, exist_ok=True)
    with open(os.path.join(base, "notes.txt"), "w") as handle:
        handle.write("Shopping: milk, bread, coffee.\n")
    deep = base
    for part in TREE:
        deep = os.path.join(deep, part)
    os.makedirs(deep, exist_ok=True)
    target = os.path.join(deep, DEEP_FILE)
    with open(target, "w") as handle:
        handle.write("Leaflets: 500 copies, matte paper, two sides.\n")
    inside = os.path.join(*TREE, DEEP_FILE)
    print("Made sample/ with 2 files and 5 folders.")
    print("The deep file sits {} characters inside sample/.".format(len(inside)))
    print("Its full path also counts the folders above sample/.")


if __name__ == "__main__":
    main()
