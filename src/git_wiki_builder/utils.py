"""Utility functions for Git Wiki Builder."""

import logging
import sys
from typing import Optional


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration.

    Args:
        verbose: Enable verbose logging
    """
    level = logging.DEBUG if verbose else logging.INFO

    # Configure root logger
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Reduce noise from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("git").setLevel(logging.WARNING)

    if not verbose:
        # Hide debug messages from our own modules in non-verbose mode
        logging.getLogger("git_wiki_builder").setLevel(logging.INFO)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for cross-platform compatibility.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "-")

    # Remove leading/trailing spaces and dots
    filename = filename.strip(". ")

    # Ensure filename is not empty
    if not filename:
        filename = "untitled"

    return filename


def truncate_text(
    text: str, max_length: int = 100, suffix: str = "..."
) -> str:
    """Truncate text to specified length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncating

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def extract_title_from_markdown(content: str) -> Optional[str]:
    """Extract title from markdown content.

    Args:
        content: Markdown content

    Returns:
        Extracted title or None
    """
    lines = content.split("\n")

    for line in lines:
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()

    return None


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size_float = float(size_bytes)

    while size_float >= 1024 and i < len(size_names) - 1:
        size_float = size_float / 1024.0
        i += 1

    return f"{size_float:.1f} {size_names[i]}"


def is_text_file(file_path: str) -> bool:
    """Check if file is a text file.

    Args:
        file_path: Path to the file

    Returns:
        True if file is text, False otherwise
    """
    text_extensions = {
        ".txt",
        ".md",
        ".rst",
        ".py",
        ".js",
        ".ts",
        ".html",
        ".css",
        ".json",
        ".yaml",
        ".yml",
        ".xml",
        ".csv",
        ".sql",
        ".sh",
        ".bat",
        ".ps1",
        ".dockerfile",
        ".gitignore",
        ".env",
    }

    file_path_lower = file_path.lower()

    # Check by extension
    for ext in text_extensions:
        if file_path_lower.endswith(ext):
            return True

    # Check common filenames without extensions
    text_filenames = {
        "readme",
        "license",
        "changelog",
        "dockerfile",
        "makefile",
        "jenkinsfile",
        "vagrantfile",
    }

    filename = file_path.split("/")[-1].lower()
    return filename in text_filenames
