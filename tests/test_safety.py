import os
import textwrap

from dir2md.constants import MERGED_FILENAME
from dir2md.split import split_files


def test_path_traversal_prevention(tmp_path):
    """
    Attacker creates a MD file with header: #### ../outside.txt
    The split tool must sanitize this and NOT write to parent directories.
    """
    unsafe_md = tmp_path / MERGED_FILENAME

    # textwrap.dedent removes the common leading whitespace from every line
    # This ensures the '####' starts at the beginning of the line, just like a real file.
    payload = textwrap.dedent("""
        #### ../outside.txt
        ```c
        malicious content
        ```
    """).strip()

    unsafe_md.write_text(payload, encoding="utf-8")

    # Change directory to the temp path to simulate running the tool there
    cwd_backup = os.getcwd()
    os.chdir(tmp_path)
    try:
        split_files(unsafe_md)
    finally:
        os.chdir(cwd_backup)

    # VERIFY:
    # 1. The file should NOT exist in the parent directory (Safety Check)
    assert not (tmp_path.parent / "outside.txt").exists()

    # 2. Depending on your logic in split.py, it should either be skipped
    #    or flattened to exist safely inside the current directory.
    #    Your current logic does: Path(raw_filename).name -> which flattens it.
    assert (tmp_path / "outside.txt").exists()


def test_absolute_path_prevention(tmp_path):
    """
    Attacker tries to write to an absolute path like /etc/passwd (or C:\\Windows).
    """
    unsafe_md = tmp_path / MERGED_FILENAME

    # Simulate an attempt to write to the root directory
    # (Using a harmless name for the test)
    payload = textwrap.dedent("""
        #### /tmp/malicious_test.txt
        ```c
        content
        ```
    """).strip()

    unsafe_md.write_text(payload, encoding="utf-8")

    cwd_backup = os.getcwd()
    os.chdir(tmp_path)
    try:
        split_files(unsafe_md)
    finally:
        os.chdir(cwd_backup)

    # It should be flattened to "malicious_test.txt" in the CURRENT dir
    # rather than trying to write to /tmp/
    assert (tmp_path / "malicious_test.txt").exists()
