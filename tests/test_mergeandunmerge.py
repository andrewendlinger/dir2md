import os
import shutil

from dir2md.constants import MERGED_FILENAME
from dir2md.merge import merge_files
from dir2md.split import split_files


def test_full_cycle(tmp_path):
    """
    1. Create dummy files
    2. Merge them
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
    # We must run merge inside the src_dir because the tool works on CWD
    cwd_backup = os.getcwd()
    os.chdir(src_dir)
    try:
        merge_files()
    finally:
        os.chdir(cwd_backup)

    bundle_path = src_dir / MERGED_FILENAME
    assert bundle_path.exists()

    # Check if summary table exists
    bundle_text = bundle_path.read_text(encoding="utf-8")
    assert "| main.c |" in bundle_text
    assert "Context Bundle Summary" in bundle_text

    # --- SPLIT ---
    # Create a fresh directory to explode files into
    restore_dir = tmp_path / "restored"
    restore_dir.mkdir()

    # Copy bundle there
    shutil.copy(bundle_path, restore_dir / MERGED_FILENAME)

    os.chdir(restore_dir)
    try:
        split_files(restore_dir / MERGED_FILENAME)
    finally:
        os.chdir(cwd_backup)

    # --- VERIFY ---
    # 1. Check C file content
    assert (restore_dir / "main.c").read_text(encoding="utf-8") == c_content

    # 2. Check H file content
    assert (restore_dir / "defs.h").read_text(encoding="utf-8") == h_content

    # 3. Ensure binary file was NOT restored
    assert not (restore_dir / "object.o").exists()
