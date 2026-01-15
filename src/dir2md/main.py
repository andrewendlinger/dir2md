import argparse
import re
from pathlib import Path

from rich.console import Console
from rich.progress import track

# Initialize Rich Console
console = Console()

# Configuration
MERGED_FILENAME = "context_bundle.md"
HEADER_PATTERN = re.compile(r"^####\s+(.+)\s*$")


def is_binary(file_path):
    """Check if file is binary by reading the first chunk."""
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            if b"\0" in chunk:
                return True
            # Optional: Check for high ASCII/UTF-8 validity if strictly text is required
    except Exception:
        return True  # Assume binary on read error
    return False


def merge_files(directory="."):
    """Combines all text files in the directory into one Markdown file."""
    base_path = Path(directory)
    files = sorted([f for f in base_path.iterdir() if f.is_file()])

    # Filter out the output file and this script itself
    files = [f for f in files if f.name != MERGED_FILENAME and f.name != "main.py"]

    text_files = []

    # Pre-scan for binary files
    for f in files:
        if not is_binary(f):
            text_files.append(f)

    if not text_files:
        console.print("[bold red]No text files found to merge![/bold red]")
        return

    console.print(f"[bold blue]Merging {len(text_files)} files...[/bold blue]")

    with open(MERGED_FILENAME, "w", encoding="utf-8") as outfile:
        # Added headers back for robustness/identification
        outfile.write("\n")
        outfile.write("\n\n")

        for f in track(text_files, description="Processing..."):
            try:
                content = f.read_text(encoding="utf-8", errors="replace")

                # Header
                outfile.write(f"#### {f.name}\n")

                # Language detection for code blocks
                ext = f.suffix.lower()
                lang_map = {
                    ".ppg": "c",
                    ".c": "c",
                    ".h": "c",
                    ".cpp": "cpp",
                    ".py": "python",
                    ".xml": "xml",
                    ".make": "makefile",
                    "makefile": "makefile",
                }
                lang = lang_map.get(ext, "")

                outfile.write(f"```{lang}\n")
                outfile.write(content)
                if not content.endswith("\n"):
                    outfile.write("\n")
                outfile.write("```\n\n")

            except Exception as e:
                console.print(f"[red]Failed to read {f.name}: {e}[/red]")

    console.print(
        f"[bold green]Success![/bold green] Bundle created: [bold]{MERGED_FILENAME}[/bold]"
    )


def split_files(bundle_file=MERGED_FILENAME):
    """Explodes the bundle back into individual files."""
    path = Path(bundle_file)
    if not path.exists():
        console.print(f"[bold red]Error:[/bold red] '{bundle_file}' not found.")
        return

    console.print(f"[bold blue]Extracting files from {bundle_file}...[/bold blue]")

    with open(path, "r", encoding="utf-8") as infile:
        lines = infile.readlines()

    current_file = None
    file_content = []
    in_code_block = False
    count = 0

    # Iterate lines
    for line in lines:
        header_match = HEADER_PATTERN.match(line.strip())

        if header_match:
            # Save previous file
            if current_file:
                write_safe_file(current_file, file_content)
                count += 1

            # Start new file
            raw_filename = header_match.group(1).strip()
            # Security: Prevent path traversal (e.g. ../../hack.sh)
            current_file = Path(raw_filename).name
            file_content = []
            in_code_block = False
            continue

        # Toggle code block state to strip the ``` wrappers
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        # Capture content
        if current_file:
            file_content.append(line)

    # Save last file
    if current_file and file_content:
        write_safe_file(current_file, file_content)
        count += 1

    console.print(f"[bold green]Success![/bold green] Extracted {count} files.")


def write_safe_file(filename, content_lines):
    """Writes content to file, ensuring we don't leave directory."""
    try:
        # Extra safety check
        dest = Path(filename)
        if ".." in str(dest) or dest.is_absolute():
            console.print(f"[red]Skipping unsafe filename: {filename}[/red]")
            return

        text = "".join(content_lines).strip() + "\n"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)
        console.print(f"  Saved: {filename}")
    except Exception as e:
        console.print(f"[red]Error writing {filename}: {e}[/red]")


def main():
    parser = argparse.ArgumentParser(
        description="Directory to Markdown Context Tool (dir2md)"
    )
    parser.add_argument(
        "--merge", action="store_true", help="Merge current directory into bundle"
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
