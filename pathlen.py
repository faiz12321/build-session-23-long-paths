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
import stat
from pathlib import Path

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


def safe_input(value, directory=False):
    path = Path(value).absolute()
    if '..' in path.parts:
        raise OSError('Parent-traversal paths are unsupported.')
    for part in [*reversed(path.parents), path]:
        info = part.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info,'st_file_attributes',0) & 0x400:
            raise OSError('Links/reparse points are unsupported.')
    info = path.lstat()
    if directory:
        if not stat.S_ISDIR(info.st_mode):
            raise OSError('Expected an ordinary directory.')
    elif not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise OSError('Expected an ordinary singly linked file.')
    return path


def scan(folder):
    """Walk a folder and find paths of LIMIT characters or more.

    Returns (root, checked, too_long, errors):
    root     - the absolute path that was scanned
    checked  - how many files and folders were looked at
    too_long - list of (length, path), longest first
    errors   - how many folders could not be read
    """
    root = str(safe_input(folder, directory=True))
    checked = 0
    too_long = []
    errors = []
    stack = [Path(root)]
    while stack:
        current = stack.pop()
        safe_input(current, directory=True)
        checked += 1
        length = win_len(str(current))
        if length >= LIMIT:
            too_long.append((length, str(current)))
        try:
            with os.scandir(current) as entries:
                ordered = sorted(entries, key=lambda entry: entry.name)
        except OSError as error:
            errors.append(error)
            continue
        for entry in ordered:
            info = entry.stat(follow_symlinks=False)
            directory = stat.S_ISDIR(info.st_mode)
            child = safe_input(entry.path, directory=directory)
            if directory:
                stack.append(child)
            else:
                checked += 1
                length = win_len(str(child))
                if length >= LIMIT:
                    too_long.append((length, str(child)))
            if checked + len(stack) > 10000:
                raise OSError('More than 10000 entries; refusing this tree.')
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
    try:
        root, checked, too_long, errors = scan(folder)
    except OSError as error:
        print('Could not read: ' + str(error))
        return 2
    print("Path length report")
    print("Folder: " + root)
    print("Checked: {} files and folders".format(checked))
    if too_long:
        print("")
        print("Too long for many Windows programs (260 characters or more):")
        for length, path in too_long:
            print("{}  {}".format(length, path))
    elif not errors:
        print("No path is 260 characters or more.")
    else:
        print("Incomplete scan: unvisited paths may exceed the limit.")
    if errors:
        print("")
        print("Note: {} folder(s) could not be read.".format(len(errors)))
    return 2 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
