from pathlib import Path

from rich.console import Console
from rich.progress import track

from .constants import MERGED_FILENAME

console = Console()


def is_binary(file_path):
    """Check if file is binary by reading the first chunk."""
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            if b"\0" in chunk:
                return True
    except Exception:
        return True
    return False


def estimate_tokens(content):
    """
    Rough estimate of token count.
    Rule of thumb: ~4 characters per token for code/English.
    """
    return len(content) // 4


def merge_files(directory="."):
    """Combines all text files in the directory into one Markdown file."""
    base_path = Path(directory)
    parent_folder_name = base_path.resolve().name

    files = sorted([f for f in base_path.iterdir() if f.is_file()])

    # Filter out the output file and main.py
    files = [f for f in files if f.name != MERGED_FILENAME and f.name != "main.py"]

    text_files = []

    # Pre-scan for binary files
    for f in files:
        if not is_binary(f):
            text_files.append(f)

    if not text_files:
        console.print("[bold red]No text files found to merge![/bold red]")
        return

    console.print(f"[bold blue]Processing {len(text_files)} files...[/bold blue]")

    processed_files = []
    total_lines = 0
    total_tokens = 0

    # 1. Read files and calculate stats
    for f in track(text_files, description="Reading files..."):
        try:
            content = f.read_text(encoding="utf-8", errors="replace")

            line_count = len(content.splitlines())
            token_count = estimate_tokens(content)

            # Update grand totals
            total_lines += line_count
            total_tokens += token_count

            processed_files.append(
                {
                    "path": f,
                    "name": f.name,
                    "lines": line_count,
                    "tokens": token_count,
                    "suffix": f.suffix.lower(),
                    "content": content,
                }
            )
        except Exception as e:
            console.print(f"[red]Failed to read {f.name}: {e}[/red]")

    # 2. Write the Bundle
    with open(MERGED_FILENAME, "w", encoding="utf-8") as outfile:
        outfile.write("\n")
        outfile.write("\n\n")

        # --- SUMMARY SECTION ---
        outfile.write("# Context Bundle Summary\n")
        outfile.write(f"**Source Directory:** `{parent_folder_name}`\n\n")

        # Grand Totals
        outfile.write(f"**Total Files:** {len(processed_files)} | ")
        outfile.write(f"**Total Lines:** {total_lines} | ")
        outfile.write(f"**Est. Tokens:** ~{total_tokens}\n\n")

        # Table
        outfile.write("| File Name | Lines | Est. Tokens |\n")
        outfile.write("| :--- | :--- | :--- |\n")

        for p in processed_files:
            outfile.write(f"| {p['name']} | {p['lines']} | ~{p['tokens']} |\n")

        outfile.write("\n")

        # --- CONTENT SECTION ---
        for p in processed_files:
            outfile.write(f"#### {p['name']}\n")

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
            lang = lang_map.get(p["suffix"], "")

            outfile.write(f"```{lang}\n")
            outfile.write(p["content"])
            if not p["content"].endswith("\n"):
                outfile.write("\n")
            outfile.write("```\n\n")

    console.print(
        f"[bold green]Success![/bold green] Bundle created: [bold]{MERGED_FILENAME}[/bold]"
    )
    console.print(f"  Lines: {total_lines}")
    console.print(f"  Tokens: ~{total_tokens}")
