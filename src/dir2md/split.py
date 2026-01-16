from pathlib import Path

from rich.console import Console

from .constants import HEADER_PATTERN, MERGED_FILENAME

console = Console()


def write_safe_file(filename, content_lines):
    """Writes content to file, ensuring we don't leave directory."""
    try:
        dest = Path(filename)
        # Security check: Prevent writing to absolute paths or using '..'
        if ".." in str(dest) or dest.is_absolute():
            console.print(f"[red]Skipping unsafe filename: {filename}[/red]")
            return

        text = "".join(content_lines).strip() + "\n"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)
        console.print(f"  Saved: {filename}")
    except Exception as e:
        console.print(f"[red]Error writing {filename}: {e}[/red]")


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

    for line in lines:
        header_match = HEADER_PATTERN.match(line.strip())

        if header_match:
            # Write previous file if it exists
            if current_file:
                write_safe_file(current_file, file_content)
                count += 1

            # Start tracking new file
            raw_filename = header_match.group(1).strip()
            current_file = Path(raw_filename).name
            file_content = []
            in_code_block = False
            continue

        # Handle code block markers
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        # Capture content
        if current_file:
            file_content.append(line)

    # Write the very last file
    if current_file and file_content:
        write_safe_file(current_file, file_content)
        count += 1

    console.print(f"[bold green]Success![/bold green] Extracted {count} files.")
