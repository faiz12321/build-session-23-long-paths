import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "pathlen.py")

sys.path.insert(0, HERE)
import pathlen


def run_tool(*args):
    return subprocess.run(
        [sys.executable, TOOL] + list(args),
        capture_output=True, text=True, timeout=60,
    )


def deep(root, parts):
    """Make nested folders from parts and return the deepest path."""
    current = root
    for part in parts:
        current = os.path.join(current, part)
    os.makedirs(current)
    return current


class WinLenTests(unittest.TestCase):
    def test_plain_ascii_counts_one_each(self):
        self.assertEqual(pathlen.win_len("abc"), 3)

    def test_emoji_counts_two_like_windows(self):
        self.assertEqual(pathlen.win_len("a\U0001F600"), 3)

    def test_accented_letter_counts_one(self):
        self.assertEqual(pathlen.win_len("caf\u00e9"), 4)


class ScanTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_short_paths_are_not_flagged(self):
        deep(self.tmp, ["a", "b"])
        open(os.path.join(self.tmp, "a", "note.txt"), "w").close()
        _root, checked, too_long, errors = pathlen.scan(self.tmp)
        self.assertEqual(too_long, [])
        self.assertEqual(errors, [])
        self.assertGreaterEqual(checked, 3)

    def test_long_path_is_flagged_with_utf16_length(self):
        # Build a name that pushes the full path to exactly 260 units.
        base = os.path.join(self.tmp, "x")
        os.makedirs(base)
        room = 260 - pathlen.win_len(base) - 1  # minus the separator
        name = "n" * room
        target = os.path.join(base, name)
        os.makedirs(target)
        self.assertEqual(pathlen.win_len(target), 260)
        _root, _checked, too_long, _errors = pathlen.scan(self.tmp)
        self.assertIn((260, os.path.abspath(target)), too_long)

    def test_259_is_not_flagged(self):
        base = os.path.join(self.tmp, "x")
        os.makedirs(base)
        room = 259 - pathlen.win_len(base) - 1
        target = os.path.join(base, "n" * room)
        os.makedirs(target)
        self.assertEqual(pathlen.win_len(target), 259)
        _root, _checked, too_long, _errors = pathlen.scan(self.tmp)
        self.assertEqual(too_long, [])

    def test_longest_comes_first(self):
        base = os.path.join(self.tmp, "x")
        os.makedirs(base)
        room = 260 - pathlen.win_len(base) - 1
        shorter = os.path.join(base, "s" * room)
        longer = os.path.join(shorter, "t" * 10)
        os.makedirs(longer)
        _root, _checked, too_long, _errors = pathlen.scan(self.tmp)
        self.assertEqual(len(too_long), 2)
        self.assertGreater(too_long[0][0], too_long[1][0])

    def test_relative_path_is_measured_as_absolute(self):
        base = os.path.join(self.tmp, "x")
        os.makedirs(base)
        room = 259 - pathlen.win_len(base) - 1
        os.makedirs(os.path.join(base, "n" * room))
        cwd = os.getcwd()
        try:
            os.chdir(self.tmp)
            root, _checked, too_long, _errors = pathlen.scan(".")
        finally:
            os.chdir(cwd)
        self.assertEqual(root, os.path.abspath(self.tmp))
        self.assertEqual(too_long, [])

    def test_empty_folder_scans_clean(self):
        _root, checked, too_long, errors = pathlen.scan(self.tmp)
        self.assertEqual((too_long, errors), ([], []))
        self.assertEqual(checked, 1)


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_no_arguments_prints_usage(self):
        result = run_tool()
        self.assertEqual(result.returncode, 2)
        self.assertIn("Usage:", result.stdout)

    def test_missing_folder_is_a_clear_error(self):
        result = run_tool(os.path.join(self.tmp, "nope"))
        self.assertEqual(result.returncode, 1)
        self.assertIn("Not a folder:", result.stdout)

    def test_a_file_is_not_a_folder(self):
        path = os.path.join(self.tmp, "note.txt")
        open(path, "w").close()
        result = run_tool(path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Not a folder:", result.stdout)

    def test_clean_folder_says_so(self):
        result = run_tool(self.tmp)
        self.assertEqual(result.returncode, 0)
        self.assertIn("No path is 260 characters or more.", result.stdout)
        self.assertIn("Checked:", result.stdout)

    def test_long_path_is_listed_with_its_length(self):
        base = os.path.join(self.tmp, "x")
        os.makedirs(base)
        room = 265 - pathlen.win_len(base) - 1
        target = os.path.join(base, "n" * room)
        os.makedirs(target)
        result = run_tool(self.tmp)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Too long for many Windows programs", result.stdout)
        self.assertIn("265  " + os.path.abspath(target), result.stdout)

    def test_tool_does_not_change_the_tree(self):
        deep(self.tmp, ["a", "b"])
        with open(os.path.join(self.tmp, "a", "note.txt"), "w") as handle:
            handle.write("hi")
        before = []
        for dirpath, dirnames, filenames in os.walk(self.tmp):
            before.append((dirpath, sorted(dirnames), sorted(filenames)))
        run_tool(self.tmp)
        after = []
        for dirpath, dirnames, filenames in os.walk(self.tmp):
            after.append((dirpath, sorted(dirnames), sorted(filenames)))
        self.assertEqual(before, after)
        with open(os.path.join(self.tmp, "a", "note.txt")) as handle:
            self.assertEqual(handle.read(), "hi")

    def test_tool_has_no_write_code(self):
        with open(TOOL) as handle:
            source = handle.read()
        for word in ("os.remove", "os.rmdir", "os.rename", "shutil.rmtree",
                     "open(", "os.makedirs", "os.mkdir"):
            self.assertNotIn(word, source)


class ScanCountingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_emoji_name_measured_like_windows(self):
        # One emoji counts as one in Python but two on Windows.
        base = os.path.join(self.tmp, "x")
        os.makedirs(base)
        room = 259 - pathlen.win_len(base) - 1
        name = "\U0001F600" + "n" * room  # one emoji: two UTF-16 units
        target = os.path.join(base, name)
        os.makedirs(target)
        self.assertEqual(len(os.path.abspath(target)), 260)
        self.assertEqual(pathlen.win_len(os.path.abspath(target)), 261)
        _root, _checked, too_long, _errors = pathlen.scan(self.tmp)
        self.assertEqual([p for _n, p in too_long], [os.path.abspath(target)])

    @unittest.skipUnless(os.name == "posix", "chmod makes a folder unreadable on POSIX only")
    def test_unreadable_folder_is_counted(self):
        blocked = os.path.join(self.tmp, "blocked")
        os.makedirs(blocked)
        os.chmod(blocked, 0)
        try:
            _root, _checked, _too_long, errors = pathlen.scan(self.tmp)
            result = run_tool(self.tmp)
        finally:
            os.chmod(blocked, 0o700)
        self.assertEqual(len(errors), 1)
        self.assertIn("could not be read", result.stdout)


class CliExtraTests(unittest.TestCase):
    def test_extra_argument_prints_usage(self):
        result = run_tool("one", "two")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Usage:", result.stdout)


if __name__ == "__main__":
    unittest.main()
