# dir2md

> **Flatten source code into a single Markdown context bundle for LLMs, then unpack it back into valid files.**

`dir2md` creates a token-optimized Markdown snapshot of your codebase for AI context. Crucially, it supports **lossless restoration**, allowing you to apply AI-generated refactors back to your source files automatically.

## 📦 Installation

**Using uv (Recommended):**
```bash
uv tool install git+https://github.com/andrewendlinger/dir2md.git

```

**From Source:**

```bash
git clone https://github.com/andrewendlinger/dir2md.git
cd dir2md
uv tool install .

```

## 🛠️ Usage

### 1. Merge (Create Context)

Combine your current directory into `SOURCE_CONTEXT_BUNDLE.md`:

```bash
dir2md --merge

```

*Features: Auto-detects text files, skips binaries, and calculates token counts.*

### 2. Split (Restore Files)

Unpack a bundle back into source files (overwrites existing files):

```bash
dir2md --split

```

*Safety: Includes path traversal protection (prevents writing to parent directories).*

## 🤖 AI Workflow

1. **Pack:** Run `dir2md --merge`.
2. **Prompt:** Upload the bundle to ChatGPT/Claude: *"Refactor main.py. Return the updated SOURCE_CONTEXT_BUNDLE.md."*
3. **Restore:** Save the AI's response and run `dir2md --split --file response.md`.
