# Find file paths that are too long for many Windows programs

A small read-only Python tool built step by step. Give it a folder. It measures the full path of every file and folder inside and lists the ones that are 260 characters or more. That is the traditional Windows limit called MAX_PATH, and many programs still keep it, so such paths can cause errors when you copy, sync, unzip or open files. The tool never changes, moves or deletes anything.

Microsoft's "Maximum Path Length Limitation" page says the Windows API traditionally limits a full path to 260 characters (MAX_PATH), and that newer Windows versions let each program opt in to longer paths. This tool cannot tell which of your programs opted in, so it simply lists every path at or past the old limit.

## Run it

    python make_sample.py       # makes a small made-up folder tree in sample/
    python pathlen.py sample    # list the long paths inside a folder
    python -m unittest -v       # 33 small fixture tests

On Windows, if `python` is not found, use `py`.

## Files

- `pathlen.py` - the tool
- `make_sample.py` - makes a made-up folder tree with one very deep file
- `test_pathlen.py` - tests

## Notes

- The length counts the full path from the drive or root, not only the part you can see inside the folder you scanned, because that is what Windows counts.
- Characters are counted the way Windows counts them, in UTF-16 units. Most characters count as one; rare ones such as emoji count as two.
- Only the character count is checked. A clean report does not mean every program will open every file, and the tool cannot tell which programs opted in to longer paths.
- Final checker refuses unsafe links/reparse/hardlinks/special entries and traversal, including linked parents. Enumeration errors are visible and return exit 2, not a clean complete report.
- Folders that cannot be read make the report incomplete and return exit 2.
- The tool only reads the folder. Tests check that nothing is changed or created.
- Educational example, no warranty. Use at your own risk.
- Code is MIT licensed (see LICENSE). Python belongs to its owners; this repository does not include it.

## Repaired setup and evidence

Two Windows and two Ubuntu full replays run the exact visible source. 33 tests pass, with two Windows skips (Unix pipe and POSIX chmod). Both exercise symlinks. Pairs differ only in unique temporary lesson paths and unittest time. Displayed output is first Windows run. Full paths and lengths depend on where the lesson folder lives. Recorder uses and removes only its own temporary lesson folder.
NEW sample setup exclusively creates tiny fictional files. Existing/traversal/linked-parent paths refuse; repeat is not a reset. Partial setup remains on failure; use another new folder. Final checker refuses unsafe input/ancestor/tree links/reparse/hardlinks/special entries and traversal. Enumeration errors produce visible incomplete status and exit 2 rather than false clean. Cap 10000 root+tree entries, with sorted listings still consuming memory/time. Stop editors/sync; no hostile-race guarantee.
33 small tests: original 19 count/report/listing cases, four setup-preservation and ten filesystem/error cases. Symlink creation can skip where unavailable. No real migration or desktop Windows proof.
This tool counts absolute path UTF-16 units. Traditional MAX_PATH includes a null terminator; flagging at 260 units is a heuristic, not a precise per-program or destination guarantee. Directory limits, long-path opt-ins and extended prefixes vary. A clean report does not prove every program will accept every path. Read-only checker has no write/network code; paths may be private, and other software/sync is uncontrolled.
