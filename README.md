# Find file paths that are too long for many Windows programs

A small read-only Python tool built step by step. Give it a folder. It measures the full path of every file and folder inside and lists the ones that are 260 characters or more. That is the traditional Windows limit called MAX_PATH, and many programs still keep it, so such paths can cause errors when you copy, sync, unzip or open files. The tool never changes, moves or deletes anything.

Microsoft's "Maximum Path Length Limitation" page says the Windows API traditionally limits a full path to 260 characters (MAX_PATH), and that newer Windows versions let each program opt in to longer paths. This tool cannot tell which of your programs opted in, so it simply lists every path at or past the old limit.

## Run it

    python make_sample.py       # makes a small made-up folder tree in sample/
    python pathlen.py sample    # list the long paths inside a folder
    python -m unittest -v       # nineteen automated tests

On Windows, if `python` is not found, use `py`.

## Files

- `pathlen.py` - the tool
- `make_sample.py` - makes a made-up folder tree with one very deep file
- `test_pathlen.py` - tests

## Notes

- The length counts the full path from the drive or root, not only the part you can see inside the folder you scanned, because that is what Windows counts.
- Characters are counted the way Windows counts them, in UTF-16 units. Most characters count as one; rare ones such as emoji count as two.
- Only the character count is checked. A clean report does not mean every program will open every file, and the tool cannot tell which programs opted in to longer paths.
- The tool uses Python's os.walk, which by default does not follow links into other folders.
- Folders that cannot be read are counted and mentioned in the report.
- The tool only reads the folder. Tests check that nothing is changed or created.
- Tested only on small made-up folders. Python 3.10 and 3.12 on Linux, and, by GitHub Actions, Python 3.12 on Windows and Ubuntu. One test is skipped on Windows by design: making a folder unreadable with chmod only works on Linux and similar systems. Not tested on a Windows 10 or 11 desktop or on real folders.
- Educational example, no warranty. Use at your own risk.
- Code is MIT licensed (see LICENSE). Python belongs to its owners; this repository does not include it.
