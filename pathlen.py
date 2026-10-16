#!/usr/bin/env python3
"""Report file paths that are too long for many Windows programs.

Windows has a traditional limit called MAX_PATH: 260 characters for a
full path. Newer Windows versions let programs opt in to longer paths,
but many programs have not. This tool scans a folder and lists the
paths that are 260 characters or more, so you can see the ones that
may cause trouble before you copy or share the folder.

The tool only reads the folder. It has no code that creates, changes,
moves or deletes anything.
"""

import os
import sys

LIMIT = 260  # MAX_PATH on Windows, from Microsoft's documentation


def win_len(text):
    """Length in UTF-16 code units, the way Windows counts characters.

    Most characters count as one. Rare ones, such as emoji, count as
    two on Windows, so a plain Python len() would undercount them.
    """
    try:
        return len(text.encode("utf-16-le")) // 2
    except UnicodeEncodeError:
        return len(text)


def scan(folder):
    """Walk a folder and find paths of LIMIT characters or more.

    Returns (root, checked, too_long, errors):
    root     - the absolute path that was scanned
    checked  - how many files and folders were looked at
    too_long - list of (length, path), longest first
    errors   - how many folders could not be read
    """
    root = os.path.abspath(folder)
    checked = 0
    too_long = []
    errors = []

    def on_error(exc):
        errors.append(exc)

    for dirpath, _dirnames, filenames in os.walk(root, onerror=on_error):
        paths = [dirpath]
        paths.extend(os.path.join(dirpath, name) for name in filenames)
        for path in paths:
            checked += 1
            length = win_len(path)
            if length >= LIMIT:
                too_long.append((length, path))
    too_long.sort(reverse=True)
    return root, checked, too_long, errors


def main(argv):
    if len(argv) != 2:
        print("Usage: python pathlen.py FOLDER")
        print("Lists the paths in FOLDER that are 260 characters or more,")
        print("the traditional Windows limit that many programs still have.")
        return 2
    folder = argv[1]
    if not os.path.isdir(folder):
        print("Not a folder: " + folder)
        return 1
    root, checked, too_long, errors = scan(folder)
    print("Path length report")
    print("Folder: " + root)
    print("Checked: {} files and folders".format(checked))
    if too_long:
        print("")
        print("Too long for many Windows programs (260 characters or more):")
        for length, path in too_long:
            print("{}  {}".format(length, path))
    else:
        print("No path is 260 characters or more.")
    if errors:
        print("")
        print("Note: {} folder(s) could not be read.".format(len(errors)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
