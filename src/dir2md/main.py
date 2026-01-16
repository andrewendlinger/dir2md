import argparse

from .constants import MERGED_FILENAME
from .merge import merge_files
from .split import split_files


def main():
    parser = argparse.ArgumentParser(
        description="Directory to Markdown Context Tool (dir2md)"
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge current directory into single markdown file",
    )
    parser.add_argument(
        "--split", action="store_true", help="Split bundle back into files"
    )
    parser.add_argument(
        "--file", type=str, default=MERGED_FILENAME, help="Specify bundle filename"
    )

    args = parser.parse_args()

    if args.merge:
        merge_files()
    elif args.split:
        split_files(args.file)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
