"""Tests for utility functions."""

import logging
import sys
from io import StringIO
from unittest.mock import patch

import pytest

from git_wiki_builder.utils import (
    extract_title_from_markdown,
    format_file_size,
    is_text_file,
    sanitize_filename,
    setup_logging,
    truncate_text,
)


class TestSetupLogging:
    """Test logging setup functionality."""

    def test_setup_logging_verbose(self) -> None:
        """Test verbose logging setup."""
        # Capture log output
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)

        with patch("logging.basicConfig") as mock_config:
            setup_logging(verbose=True)
            mock_config.assert_called_once()
            args, kwargs = mock_config.call_args
            assert kwargs["level"] == logging.DEBUG
            assert "format" in kwargs
            assert "datefmt" in kwargs

    def test_setup_logging_non_verbose(self) -> None:
        """Test non-verbose logging setup."""
        with patch("logging.basicConfig") as mock_config:
            setup_logging(verbose=False)
            mock_config.assert_called_once()
            args, kwargs = mock_config.call_args
            assert kwargs["level"] == logging.INFO

    def test_setup_logging_default(self) -> None:
        """Test default logging setup."""
        with patch("logging.basicConfig") as mock_config:
            setup_logging()
            mock_config.assert_called_once()
            args, kwargs = mock_config.call_args
            assert kwargs["level"] == logging.INFO


class TestSanitizeFilename:
    """Test filename sanitization."""

    def test_sanitize_filename_valid(self) -> None:
        """Test sanitizing valid filename."""
        result = sanitize_filename("valid_filename.txt")
        assert result == "valid_filename.txt"

    def test_sanitize_filename_invalid_chars(self) -> None:
        """Test sanitizing filename with invalid characters."""
        result = sanitize_filename('file<>:"/\\|?*.txt')
        assert result == "file---------.txt"

    def test_sanitize_filename_leading_trailing_spaces(self) -> None:
        """Test sanitizing filename with leading/trailing spaces and dots."""
        result = sanitize_filename("  . filename .txt .  ")
        assert result == "filename .txt"

    def test_sanitize_filename_empty(self) -> None:
        """Test sanitizing empty filename."""
        result = sanitize_filename("")
        assert result == "untitled"

    def test_sanitize_filename_only_invalid(self) -> None:
        """Test sanitizing filename with only invalid characters."""
        result = sanitize_filename('<>:"/\\|?*')
        assert result == "---------"

    def test_sanitize_filename_only_spaces_dots(self) -> None:
        """Test sanitizing filename with only spaces and dots."""
        result = sanitize_filename("  ... ")
        assert result == "untitled"


class TestTruncateText:
    """Test text truncation functionality."""

    def test_truncate_text_short(self) -> None:
        """Test truncating short text."""
        text = "Short text"
        result = truncate_text(text, max_length=100)
        assert result == text

    def test_truncate_text_long(self) -> None:
        """Test truncating long text."""
        text = "This is a very long text that should be truncated"
        result = truncate_text(text, max_length=20)
        assert result == "This is a very lo..."
        assert len(result) == 20

    def test_truncate_text_custom_suffix(self) -> None:
        """Test truncating with custom suffix."""
        text = "This is a long text"
        result = truncate_text(text, max_length=15, suffix="!!!")
        assert result == "This is a lo!!!"
        assert len(result) == 15

    def test_truncate_text_exact_length(self) -> None:
        """Test truncating text at exact max length."""
        text = "Exact length"
        result = truncate_text(text, max_length=12)
        assert result == text

    def test_truncate_text_empty(self) -> None:
        """Test truncating empty text."""
        result = truncate_text("", max_length=10)
        assert result == ""


class TestExtractTitleFromMarkdown:
    """Test markdown title extraction."""

    def test_extract_title_h1(self) -> None:
        """Test extracting H1 title."""
        content = "# Main Title\n\nSome content here"
        result = extract_title_from_markdown(content)
        assert result == "Main Title"

    def test_extract_title_h1_with_spaces(self) -> None:
        """Test extracting H1 title with extra spaces."""
        content = "#   Spaced Title   \n\nContent"
        result = extract_title_from_markdown(content)
        assert result == "Spaced Title"

    def test_extract_title_no_h1(self) -> None:
        """Test extracting title when no H1 exists."""
        content = "## Subtitle\n\nSome content"
        result = extract_title_from_markdown(content)
        assert result is None

    def test_extract_title_multiple_h1(self) -> None:
        """Test extracting first H1 when multiple exist."""
        content = "# First Title\n\nContent\n\n# Second Title"
        result = extract_title_from_markdown(content)
        assert result == "First Title"

    def test_extract_title_empty_content(self) -> None:
        """Test extracting title from empty content."""
        result = extract_title_from_markdown("")
        assert result is None

    def test_extract_title_only_whitespace(self) -> None:
        """Test extracting title from whitespace-only content."""
        result = extract_title_from_markdown("   \n  \n  ")
        assert result is None

    def test_extract_title_h1_in_middle(self) -> None:
        """Test extracting H1 that's not at the beginning."""
        content = "Some intro text\n\n# Main Title\n\nMore content"
        result = extract_title_from_markdown(content)
        assert result == "Main Title"


class TestFormatFileSize:
    """Test file size formatting."""

    def test_format_file_size_zero(self) -> None:
        """Test formatting zero bytes."""
        result = format_file_size(0)
        assert result == "0 B"

    def test_format_file_size_bytes(self) -> None:
        """Test formatting bytes."""
        result = format_file_size(512)
        assert result == "512.0 B"

    def test_format_file_size_kilobytes(self) -> None:
        """Test formatting kilobytes."""
        result = format_file_size(1536)  # 1.5 KB
        assert result == "1.5 KB"

    def test_format_file_size_megabytes(self) -> None:
        """Test formatting megabytes."""
        result = format_file_size(2097152)  # 2 MB
        assert result == "2.0 MB"

    def test_format_file_size_gigabytes(self) -> None:
        """Test formatting gigabytes."""
        result = format_file_size(3221225472)  # 3 GB
        assert result == "3.0 GB"

    def test_format_file_size_terabytes(self) -> None:
        """Test formatting terabytes."""
        result = format_file_size(2199023255552)  # 2 TB
        assert result == "2.0 TB"

    def test_format_file_size_large(self) -> None:
        """Test formatting very large file size."""
        result = format_file_size(1125899906842624)  # 1 PB -> should be TB
        assert result == "1024.0 TB"

    def test_format_file_size_edge_cases(self) -> None:
        """Test formatting edge cases."""
        # Exactly 1 KB
        result = format_file_size(1024)
        assert result == "1.0 KB"

        # Just under 1 KB
        result = format_file_size(1023)
        assert result == "1023.0 B"


class TestIsTextFile:
    """Test text file detection."""

    def test_is_text_file_by_extension(self) -> None:
        """Test detecting text files by extension."""
        text_files = [
            "document.txt",
            "README.md",
            "guide.rst",
            "script.py",
            "app.js",
            "types.ts",
            "page.html",
            "style.css",
            "data.json",
            "config.yaml",
            "config.yml",
            "data.xml",
            "data.csv",
            "query.sql",
            "script.sh",
            "script.bat",
            "script.ps1",
            "docker.dockerfile",
            ".gitignore",
            "settings.env",
        ]

        for file_path in text_files:
            assert is_text_file(
                file_path
            ), f"{file_path} should be detected as text"

    def test_is_text_file_by_filename(self) -> None:
        """Test detecting text files by filename."""
        text_files = [
            "readme",
            "README",
            "license",
            "LICENSE",
            "changelog",
            "CHANGELOG",
            "dockerfile",
            "Dockerfile",
            "makefile",
            "Makefile",
            "jenkinsfile",
            "Jenkinsfile",
            "vagrantfile",
            "Vagrantfile",
        ]

        for file_path in text_files:
            assert is_text_file(
                file_path
            ), f"{file_path} should be detected as text"

    def test_is_text_file_case_insensitive(self) -> None:
        """Test case insensitive detection."""
        assert is_text_file("FILE.TXT")
        assert is_text_file("Script.PY")
        assert is_text_file("CONFIG.YAML")
        assert is_text_file("README")

    def test_is_text_file_with_path(self) -> None:
        """Test detection with file paths."""
        assert is_text_file("/path/to/file.txt")
        assert is_text_file("./relative/path/script.py")
        assert is_text_file("../docs/README.md")

    def test_is_not_text_file(self) -> None:
        """Test detecting non-text files."""
        non_text_files = [
            "image.jpg",
            "photo.png",
            "video.mp4",
            "archive.zip",
            "binary.exe",
            "library.so",
            "document.pdf",
            "unknown_file",
        ]

        for file_path in non_text_files:
            assert not is_text_file(
                file_path
            ), f"{file_path} should not be detected as text"

    def test_is_text_file_edge_cases(self) -> None:
        """Test edge cases."""
        # Empty string
        assert not is_text_file("")

        # Just extension
        assert is_text_file(".txt")

        # Multiple extensions
        assert is_text_file("file.backup.txt")

        # No extension but known filename
        assert is_text_file("dockerfile")
