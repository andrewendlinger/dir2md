[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![Tests](https://github.com/andrewendlinger/dir2md/actions/workflows/ci.yml/badge.svg)

# dir2md

**Flatten source code into a single Markdown context bundle for LLMs, then unpack it back into valid files.**

`dir2md` creates a token-optimized Markdown snapshot of your codebase. Unlike simple concatenation scripts, it supports **lossless restoration**, allowing you to feed a directory to an LLM and programmatically apply the AI's refactored response back to your local files.

## Installation

**Using uv (Recommended)**

```bash
uv tool install git+https://github.com/andrewendlinger/dir2md.git

```

**From Source**

```bash
git clone https://github.com/andrewendlinger/dir2md.git
cd dir2md
uv tool install .

```

## Usage

### 📥 Merge (Create Context)

Combines your current directory into a single file (`SOURCE_CONTEXT_BUNDLE.md`). Automatically detects text files, ignores binaries, and calculates token counts.

```bash
dir2md --merge

```

### 📤 Split (Restore Files)

Unpacks a bundle back into source files. This parses the Markdown and overwrites the files at the paths specified in the bundle.

```bash
dir2md --split

```

*> **Note:** Includes path traversal protection to prevent writing files outside the current directory.*

## Potential Workflow

1. **Pack:** Run `dir2md --merge` to snapshot your code.
2. **Prompt:** Upload the bundle to your LLM of choice with the prompt: *"Refactor main.py. Return the full updated SOURCE_CONTEXT_BUNDLE.md."*
3. **Restore:** Save the LLM's raw markdown response to a file (e.g., `response.md`) and run:
```bash
dir2md --split --file response.md
```

