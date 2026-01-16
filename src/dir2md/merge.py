from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)
from rich.table import Table

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
    """Rough estimate: ~4 chars per token."""
    return len(content) // 4


def merge_files(directory="."):
    """Combines all text files in the directory into one Markdown file."""
    base_path = Path(directory)
    parent_folder_name = base_path.resolve().name

    # 1. Gather files
    files = sorted([f for f in base_path.iterdir() if f.is_file()])
    files = [f for f in files if f.name != MERGED_FILENAME and f.name != "main.py"]

    text_files = []
    # Quick pre-scan for binary files (usually fast enough to not need a bar)
    for f in files:
        if not is_binary(f):
            text_files.append(f)

    if not text_files:
        console.print("[bold red]No text files found to merge![/bold red]")
        return

    # 2. Process Files with a Transient Progress Bar
    processed_files = []
    total_lines = 0
    total_tokens = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=None),
        TaskProgressColumn(),
        transient=True,  # <--- The bar will vanish when done
    ) as progress:
        task = progress.add_task("Reading files...", total=len(text_files))

        for f in text_files:
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
                line_count = len(content.splitlines())
                token_count = estimate_tokens(content)

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
                console.print(f"[red]Skipping {f.name}: {e}[/red]")

            progress.advance(task)

    # 3. Write the Bundle
    with open(MERGED_FILENAME, "w", encoding="utf-8") as outfile:
        outfile.write("\n")
        outfile.write("\n\n")

        # --- Summary Header in MD ---
        outfile.write("# Context Bundle Summary\n")
        outfile.write(f"**Source Directory:** `{parent_folder_name}`\n\n")
        outfile.write(
            f"**Total Files:** {len(processed_files)} | "
            f"**Total Lines:** {total_lines:,} | "
            f"**Est. Tokens:** ~{total_tokens:,}\n\n"
        )

        outfile.write("| File Name | Lines | Est. Tokens |\n")
        outfile.write("| :--- | :--- | :--- |\n")
        for p in processed_files:
            outfile.write(f"| {p['name']} | {p['lines']:,} | ~{p['tokens']:,} |\n")
        outfile.write("\n")

        # --- Content ---
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

    # 4. Final Clean Output (Grid inside Panel)
    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="bold white")
    grid.add_column(justify="right", style="cyan")

    grid.add_row("Source:", parent_folder_name)
    grid.add_row("Files:", str(len(processed_files)))
    grid.add_row("Lines:", f"{total_lines:,}")
    grid.add_row("Tokens:", f"~{total_tokens:,}")

    console.print(
        Panel(
            grid,
            title=f"[bold green]Created: {MERGED_FILENAME}[/bold green]",
            border_style="green",
            expand=False,
        )
    )
