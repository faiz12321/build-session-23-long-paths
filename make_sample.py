#!/usr/bin/env python3
"""Make a small made-up folder tree for the path length lesson.

One file sits deep inside folders with long names, so its full path is
more than 260 characters on any machine. Nothing here is real.
"""

import os
import stat
from pathlib import Path

TREE = [
    "Project archive copied from the old shared drive",
    "Backup of the marketing folder before the office move",
    "Campaign photos and draft leaflets for the spring launch",
    "Final versions approved and sent to the print shop",
]
DEEP_FILE = "Read me first - printing notes for the leaflets.txt"


def make(folder):
    base = Path(folder).absolute()
    if '..' in base.parts:
        raise OSError('Parent-traversal setup paths are unsupported.')
    for parent in reversed(base.parents):
        info = parent.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise OSError('Linked/reparse parents are unsupported.')
    base.mkdir()
    with open(os.path.join(base, "notes.txt"), "x", encoding="utf-8") as handle:
        handle.write("Shopping: milk, bread, coffee.\n")
    deep = base
    for part in TREE:
        deep = os.path.join(deep, part)
    os.makedirs(deep, exist_ok=False)
    target = os.path.join(deep, DEEP_FILE)
    with open(target, "x", encoding="utf-8") as handle:
        handle.write("Leaflets: 500 copies, matte paper, two sides.\n")
    inside = os.path.join(*TREE, DEEP_FILE)
    print("Made sample/ with 2 files and 5 folders.")
    print("The deep file sits {} characters inside sample/.".format(len(inside)))
    print("Its full path also counts the folders above sample/.")


def main():
    try:
        make(Path(__file__).absolute().parent / 'sample')
    except FileExistsError:
        raise SystemExit('Stopped: sample already exists. Nothing was replaced or deleted.')


if __name__ == "__main__":
    main()
