"""Markdown validation and fixing utilities."""

import logging
import re
from dataclasses import dataclass
from typing import List, Optional

from .config import Config

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of markdown validation."""

    is_valid: bool
    errors: List[str]
    warnings: List[str]


class MarkdownValidator:
    """Validates and fixes markdown content according to best practices."""

    def __init__(self, config: Config) -> None:
        """Initialize markdown validator.

        Args:
            config: Configuration instance
        """
        self.config = config

    def validate_content(self, content: str) -> ValidationResult:
        """Validate markdown content.

        Args:
            content: Markdown content to validate

        Returns:
            ValidationResult with validation status and issues
        """
        errors = []
        warnings = []

        # Check document structure
        structure_issues = self._check_document_structure(content)
        errors.extend(structure_issues)

        # Check heading format
        heading_issues = self._check_heading_format(content)
        errors.extend(heading_issues)

        # Check list formatting
        list_issues = self._check_list_format(content)
        warnings.extend(list_issues)

        # Check code blocks
        code_issues = self._check_code_blocks(content)
        errors.extend(code_issues)

        # Check links and images
        link_issues = self._check_links_and_images(content)
        warnings.extend(link_issues)

        # Check spacing
        spacing_issues = self._check_spacing(content)
        warnings.extend(spacing_issues)

        is_valid = len(errors) == 0

        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)

    def fix_content(self, content: str) -> str:
        """Automatically fix common markdown issues.

        Args:
            content: Markdown content to fix

        Returns:
            Fixed markdown content
        """
        fixed_content = content

        # Fix heading spacing
        fixed_content = self._fix_heading_spacing(fixed_content)

        # Fix heading format
        fixed_content = self._fix_heading_format(fixed_content)

        # Fix list formatting
        fixed_content = self._fix_list_format(fixed_content)

        # Fix code block language specification
        fixed_content = self._fix_code_blocks(fixed_content)

        # Fix spacing issues
        fixed_content = self._fix_spacing(fixed_content)

        # Fix line endings
        fixed_content = self._fix_line_endings(fixed_content)

        return fixed_content

    def _check_document_structure(self, content: str) -> List[str]:
        """Check document structure (MD001, MD041, MD025)."""
        errors = []
        lines = content.split("\n")

        # Check if document starts with H1 (MD041)
        first_heading_found = False
        for line in lines:
            line = line.strip()
            if line.startswith("#"):
                if not line.startswith("# "):
                    errors.append("MD041: Document should start with top-level heading")
                first_heading_found = True
                break
            elif line:  # Non-empty, non-heading line
                errors.append("MD041: Document should start with top-level heading")
                break

        # Check heading level increments (MD001) and multiple H1s (MD025)
        h1_count = 0
        prev_level = 0

        for line in lines:
            line = line.strip()
            if line.startswith("#"):
                level = len(line) - len(line.lstrip("#"))

                if level == 1:
                    h1_count += 1

                if level > prev_level + 1:
                    errors.append(
                        f"MD001: Heading level increment too large (#{level})"
                    )

                prev_level = level

        if h1_count > 1:
            errors.append("MD025: Multiple top-level headings found")

        return errors

    def _check_heading_format(self, content: str) -> List[str]:
        """Check heading format (MD003, MD018, MD019, MD023)."""
        errors = []
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            if line.lstrip().startswith("#"):
                # Check for indented headings (MD023)
                if line.startswith(" ") or line.startswith("\t"):
                    errors.append(f"MD023: Line {i}: Headings should not be indented")

                # Check for space after hash (MD018)
                hash_part = line.lstrip().split()[0]
                if not re.match(r"^#+\s", line.lstrip()):
                    errors.append(
                        f"MD018: Line {i}: No space after hash on atx style heading"
                    )

                # Check for multiple spaces after hash (MD019)
                if re.match(r"^#+\s{2,}", line.lstrip()):
                    errors.append(
                        f"MD019: Line {i}: Multiple spaces after hash on atx style heading"
                    )

        return errors

    def _check_list_format(self, content: str) -> List[str]:
        """Check list formatting (MD004, MD005, MD007, MD032)."""
        issues = []
        lines = content.split("\n")

        in_list = False
        list_markers = set()

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Check for list items
            list_match = re.match(r"^[\s]*[-*+]\s", line)
            if list_match:
                in_list = True
                marker_match = re.match(r"^[\s]*([-*+])", line)
                if marker_match:
                    marker = marker_match.group(1)
                    list_markers.add(marker)

                # Check indentation (MD007)
                indent = len(line) - len(line.lstrip())
                if indent % 2 != 0:
                    issues.append(
                        f"MD007: Line {i}: List indentation should be 2 spaces"
                    )

            elif in_list and not stripped:
                # End of list, check for blank lines around lists (MD032)
                if i < len(lines) and lines[i].strip():
                    issues.append(
                        f"MD032: Line {i}: Lists should be surrounded by blank lines"
                    )
                in_list = False

        # Check for consistent list markers (MD004)
        if len(list_markers) > 1:
            issues.append("MD004: Unordered list style should be consistent")

        return issues

    def _check_code_blocks(self, content: str) -> List[str]:
        """Check code blocks (MD040, MD031, MD046)."""
        errors = []
        lines = content.split("\n")

        in_fenced_block = False

        for i, line in enumerate(lines, 1):
            # Check for fenced code blocks
            if line.strip().startswith("```"):
                if not in_fenced_block:
                    # Starting a code block
                    if line.strip() == "```":
                        errors.append(
                            f"MD040: Line {i}: Fenced code blocks should have a language specified"
                        )

                    # Check for blank line before (MD031)
                    if i > 1 and lines[i - 2].strip():
                        errors.append(
                            f"MD031: Line {i}: Fenced code blocks should be surrounded by blank lines"
                        )

                    in_fenced_block = True
                else:
                    # Ending a code block
                    # Check for blank line after (MD031)
                    if i < len(lines) and lines[i].strip():
                        errors.append(
                            f"MD031: Line {i}: Fenced code blocks should be surrounded by blank lines"
                        )

                    in_fenced_block = False

        return errors

    def _check_links_and_images(self, content: str) -> List[str]:
        """Check links and images (MD034, MD045, MD011)."""
        issues = []
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Check for bare URLs (MD034)
            bare_url_pattern = r"(?<![\[\(])(https?://[^\s\)]+)(?![\]\)])"
            if re.search(bare_url_pattern, line):
                issues.append(f"MD034: Line {i}: Bare URL used")

            # Check for images without alt text (MD045)
            img_pattern = r"!\[\s*\]\([^)]+\)"
            if re.search(img_pattern, line):
                issues.append(f"MD045: Line {i}: Images should have alternate text")

            # Check for reversed link syntax (MD011)
            reversed_link_pattern = r"\([^)]+\)\[[^\]]*\]"
            if re.search(reversed_link_pattern, line):
                issues.append(f"MD011: Line {i}: Reversed link syntax")

        return issues

    def _check_spacing(self, content: str) -> List[str]:
        """Check spacing issues (MD009, MD010, MD012)."""
        issues = []
        lines = content.split("\n")

        consecutive_blank_lines = 0

        for i, line in enumerate(lines, 1):
            # Check for trailing spaces (MD009)
            if line.endswith(" ") and not line.endswith(
                "  "
            ):  # Allow 2+ spaces for line breaks
                issues.append(f"MD009: Line {i}: Trailing spaces")

            # Check for tabs (MD010)
            if "\t" in line:
                issues.append(f"MD010: Line {i}: Hard tabs")

            # Check for multiple consecutive blank lines (MD012)
            if not line.strip():
                consecutive_blank_lines += 1
                if consecutive_blank_lines > 1:
                    issues.append(f"MD012: Line {i}: Multiple consecutive blank lines")
            else:
                consecutive_blank_lines = 0

        return issues

    def _fix_heading_spacing(self, content: str) -> str:
        """Fix heading spacing issues (MD022)."""
        lines = content.split("\n")
        fixed_lines: List[str] = []

        for i, line in enumerate(lines):
            if line.strip().startswith("#"):
                # Add blank line before heading if needed
                if i > 0 and lines[i - 1].strip() and not fixed_lines[-1] == "":
                    fixed_lines.append("")

                fixed_lines.append(line)

                # Add blank line after heading if needed
                if (
                    i < len(lines) - 1
                    and lines[i + 1].strip()
                    and not lines[i + 1].strip().startswith("#")
                ):
                    fixed_lines.append("")
            else:
                fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def _fix_heading_format(self, content: str) -> str:
        """Fix heading format issues."""
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            if line.lstrip().startswith("#"):
                # Remove indentation
                line = line.lstrip()

                # Fix spacing after hash
                match = re.match(r"^(#+)\s*(.*)", line)
                if match:
                    hashes, text = match.groups()
                    line = f"{hashes} {text}".rstrip()

            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def _fix_list_format(self, content: str) -> str:
        """Fix list formatting issues."""
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            # Standardize list markers to "-"
            if re.match(r"^[\s]*[*+]\s", line):
                line = re.sub(r"^([\s]*)[*+](\s)", r"\1-\2", line)

            # Fix indentation to 2 spaces
            match = re.match(r"^(\s*)([-*+])\s+(.*)", line)
            if match:
                indent, marker, text = match.groups()
                # Calculate proper indentation (multiples of 2)
                level = len(indent) // 2
                proper_indent = "  " * level
                line = f"{proper_indent}- {text}"

            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def _fix_code_blocks(self, content: str) -> str:
        """Fix code block issues."""
        lines = content.split("\n")
        fixed_lines = []

        for i, line in enumerate(lines):
            if line.strip() == "```":
                # Add language specification for code blocks
                # Try to guess language from context
                language = self._guess_code_language(lines, i)
                fixed_lines.append(f"```{language}")
            else:
                fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def _fix_spacing(self, content: str) -> str:
        """Fix spacing issues."""
        lines = content.split("\n")
        fixed_lines = []
        prev_blank = False

        for line in lines:
            # Remove trailing spaces (except line breaks)
            if line.endswith(" ") and not line.endswith("  "):
                line = line.rstrip()

            # Replace tabs with spaces
            line = line.replace("\t", "    ")

            # Remove multiple consecutive blank lines
            if not line.strip():
                if not prev_blank:
                    fixed_lines.append(line)
                prev_blank = True
            else:
                fixed_lines.append(line)
                prev_blank = False

        return "\n".join(fixed_lines)

    def _fix_line_endings(self, content: str) -> str:
        """Fix line endings and ensure file ends with newline."""
        # Normalize line endings
        content = content.replace("\r\n", "\n").replace("\r", "\n")

        # Ensure file ends with single newline
        content = content.rstrip() + "\n"

        return content

    def _guess_code_language(self, lines: List[str], code_block_start: int) -> str:
        """Guess programming language for code block."""
        # Look at surrounding context and code content
        context_lines = lines[max(0, code_block_start - 5) : code_block_start + 10]
        context = " ".join(context_lines).lower()

        # Simple heuristics for language detection
        if any(
            keyword in context
            for keyword in ["python", "pip", "import", "def ", "class "]
        ):
            return "python"
        elif any(
            keyword in context
            for keyword in ["javascript", "js", "npm", "function", "const ", "let "]
        ):
            return "javascript"
        elif any(
            keyword in context for keyword in ["bash", "shell", "command", "$", "sudo"]
        ):
            return "bash"
        elif any(keyword in context for keyword in ["json", "api", "response"]):
            return "json"
        elif any(keyword in context for keyword in ["yaml", "yml", "config"]):
            return "yaml"
        elif any(
            keyword in context for keyword in ["sql", "database", "select", "insert"]
        ):
            return "sql"
        elif any(keyword in context for keyword in ["html", "web", "<", ">"]):
            return "html"
        elif any(keyword in context for keyword in ["css", "style", "selector"]):
            return "css"
        else:
            return "text"
