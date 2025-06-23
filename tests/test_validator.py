"""Tests for markdown validator."""

import tempfile
from pathlib import Path

import pytest

from git_wiki_builder.config import Config
from git_wiki_builder.validator import MarkdownValidator


class TestMarkdownValidator:
    """Test markdown validation functionality."""

    def test_valid_markdown(self) -> None:
        """Test validation of valid markdown."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            validator = MarkdownValidator(config)

            valid_content = """# Main Title

This is a paragraph with proper formatting.

## Section 1

- List item 1
- List item 2

```python
def example():
    return "Hello, World!"
```

## Section 2

Another paragraph with [a link](https://example.com).
"""

            result = validator.validate_content(valid_content)
            assert result.is_valid is True
            assert len(result.errors) == 0

    def test_heading_issues(self) -> None:
        """Test detection of heading issues."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            validator = MarkdownValidator(config)

            # Test multiple H1s
            content_multiple_h1 = """# Title 1

Some content.

# Title 2

More content.
"""

            result = validator.validate_content(content_multiple_h1)
            assert not result.is_valid
            assert any("MD025" in error for error in result.errors)

            # Test heading level jump
            content_level_jump = """# Title

### Subsection

Content here.
"""

            result = validator.validate_content(content_level_jump)
            assert not result.is_valid
            assert any("MD001" in error for error in result.errors)

    def test_code_block_issues(self) -> None:
        """Test detection of code block issues."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            validator = MarkdownValidator(config)

            # Test code block without language
            content_no_lang = """# Title

```
def example():
    return "Hello"
```
"""

            result = validator.validate_content(content_no_lang)
            assert not result.is_valid
            assert any("MD040" in error for error in result.errors)

    def test_list_formatting_issues(self) -> None:
        """Test detection of list formatting issues."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            validator = MarkdownValidator(config)

            # Test inconsistent list markers
            content_inconsistent = """# Title

- Item 1
* Item 2
+ Item 3
"""

            result = validator.validate_content(content_inconsistent)
            assert any("MD004" in warning for warning in result.warnings)

    def test_content_fixing(self) -> None:
        """Test automatic content fixing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            validator = MarkdownValidator(config)

            # Test fixing heading format
            content_bad_headings = """#Title
##  Subtitle
   ### Indented heading
"""

            fixed_content = validator.fix_content(content_bad_headings)

            assert "# Title" in fixed_content
            assert "## Subtitle" in fixed_content
            assert "### Indented heading" in fixed_content
            assert not fixed_content.startswith("   ")

    def test_spacing_fixes(self) -> None:
        """Test spacing issue fixes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            validator = MarkdownValidator(config)

            # Test fixing trailing spaces and multiple blank lines
            content_spacing_issues = """# Title   

This line has trailing spaces.   


Multiple blank lines above.
"""

            fixed_content = validator.fix_content(content_spacing_issues)

            # Check that trailing spaces are removed
            lines = fixed_content.split("\n")
            for line in lines:
                if line.strip():  # Non-empty lines
                    assert not line.endswith(" ") or line.endswith("  ")  # Allow line breaks

            # Check that multiple blank lines are reduced
            assert "\n\n\n" not in fixed_content

    def test_list_marker_fixing(self) -> None:
        """Test list marker standardization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            validator = MarkdownValidator(config)

            content_mixed_markers = """# Title

* Item 1
+ Item 2
- Item 3
"""

            fixed_content = validator.fix_content(content_mixed_markers)

            # All list markers should be standardized to "-"
            lines = fixed_content.split("\n")
            for line in lines:
                if line.strip().startswith(("*", "+")):
                    # Should be converted to "-"
                    pass  # The fix should have converted these
                elif line.strip().startswith("-"):
                    assert True  # This is correct

            # Check that all list items use "-"
            assert "- Item 1" in fixed_content
            assert "- Item 2" in fixed_content
            assert "- Item 3" in fixed_content

    def test_code_language_guessing(self) -> None:
        """Test code language guessing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            validator = MarkdownValidator(config)

            # Test Python code detection
            lines = ["# Python Example", "```", "def hello():", "    print('Hello, World!')", "```"]

            language = validator._guess_code_language(lines, 1)
            assert language == "python"

            # Test JavaScript code detection
            lines = [
                "# JavaScript Example",
                "```",
                "function hello() {",
                "    console.log('Hello, World!');",
                "}",
            ]

            language = validator._guess_code_language(lines, 1)
            assert language == "javascript"
