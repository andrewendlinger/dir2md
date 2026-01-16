import os
import re

from dir2md.constants import MERGED_FILENAME
from dir2md.merge import merge_files
from dir2md.split import split_files


def test_full_cycle(tmp_path):
    """
    1. Create dummy files
    2. Merge them (checking table robustness)
    3. Split them into a clean folder
    4. Verify contents match exactly
    """
    # --- SETUP ---
    src_dir = tmp_path / "source"
    src_dir.mkdir()

    # Create a C file
    c_content = "int main() { return 0; }\n"
    (src_dir / "main.c").write_text(c_content, encoding="utf-8")

    # Create a Header file
    h_content = "#define MAX 100\n"
    (src_dir / "defs.h").write_text(h_content, encoding="utf-8")

    # Create a Binary file (should be ignored)
    (src_dir / "object.o").write_bytes(b"\x00\x01\x02")

    # --- MERGE ---
    cwd_backup = os.getcwd()
    os.chdir(src_dir)
    try:
        merge_files()
    finally:
        os.chdir(cwd_backup)

    bundle_path = src_dir / MERGED_FILENAME
    assert bundle_path.exists()

    bundle_text = bundle_path.read_text(encoding="utf-8")

    # 1. Check for AI Instructions Preamble
    assert "**CONTEXT BUNDLE INSTRUCTIONS**" in bundle_text

    # 2. Check Summary Table (Using Regex to ignore whitespace padding)
    # Looks for: | <spaces> main.c <spaces> |
    assert re.search(r"\|\s+main\.c\s+\|", bundle_text), (
        "main.c missing from summary table"
    )
    assert re.search(r"\|\s+defs\.h\s+\|", bundle_text), (
        "defs.h missing from summary table"
    )

    # --- SPLIT (RESTORE) ---
    # Create a clean directory to restore into
    restore_dir = tmp_path / "restore"
    restore_dir.mkdir()

    # Copy bundle to restore dir (simulate AI returning the file)
    (restore_dir / MERGED_FILENAME).write_text(bundle_text, encoding="utf-8")

    os.chdir(restore_dir)
    try:
        # Run split
        split_files(MERGED_FILENAME)
    finally:
        os.chdir(cwd_backup)

    # --- VERIFY RESTORATION ---
    # The AI preamble should NOT be created as a file
    # Binaries should NOT be there
    # Source files MUST match exactly

    assert (restore_dir / "main.c").exists()
    assert (restore_dir / "main.c").read_text(encoding="utf-8") == c_content

    assert (restore_dir / "defs.h").exists()
    assert (restore_dir / "defs.h").read_text(encoding="utf-8") == h_content

    assert not (restore_dir / "object.o").exists()
