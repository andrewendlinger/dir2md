import re

# Updated to be longer and standout
MERGED_FILENAME = "SOURCE_CONTEXT_BUNDLE.md"

HEADER_PATTERN = re.compile(r"^####\s+(.+)\s*$")

# The prompt for the LLM
AI_INSTRUCTIONS = """> **CONTEXT BUNDLE INSTRUCTIONS**
> This document is a flattened representation of a source code repository.
>
> **Structure:**
> * **Headers:** `#### filename` indicates the start of a new file.
> * **Content:** The file content follows immediately in a code block.
>
> **Usage:**
> * Read the files below to understand the project context.
> * **Refactoring:** If asked to generate a full refactor, you must preserve the `#### filename` headers exactly. This allows the `dir2md --split` tool to automatically restore the files to the disk.
"""
