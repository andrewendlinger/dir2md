import argparse
import sys

from .constants import MERGED_FILENAME
from .merge import merge_files
from .split import split_files


def main():
    description = """
    Directory to Markdown Context Tool (dir2md)
    -------------------------------------------
    A developer tool to 'flatten' a source code directory into a single
    Markdown file (context bundle) for use with LLMs, and 'explode'
    it back into the original file structure.
    """

    epilog = f"""
    examples:
      dir2md --merge                    # Create {MERGED_FILENAME} from current dir
      dir2md --split                    # Restore files from {MERGED_FILENAME}
      dir2md --split --file context.md  # Restore from a specific file
    """

    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,  # <--- 1. Disable default help so we can customize it
    )

    # Action Group
    action_group = parser.add_mutually_exclusive_group(required=False)

    action_group.add_argument(
        "--merge",
        "-m",
        action="store_true",
        help="Merge all source files in the current directory into a single Markdown bundle.",
    )

    action_group.add_argument(
        "--split",
        "-s",
        action="store_true",
        help="Split a Markdown bundle back into individual source files.",
    )

    # Options Group
    options_group = parser.add_argument_group("configuration")

    # 2. Re-add help manually with Capitalized description
    options_group.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit.",
    )

    options_group.add_argument(
        "--file",
        "-f",
        type=str,
        default=MERGED_FILENAME,
        metavar="FILENAME",
        help=f"Specify the bundle filename (default: {MERGED_FILENAME})",
    )

    args = parser.parse_args()

    if args.merge:
        merge_files()
    elif args.split:
        split_files(args.file)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
