"""Tests for configuration management."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from git_wiki_builder.config import Config


class TestConfig:
    """Test configuration management."""

    def test_default_config(self) -> None:
        """Test default configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            # Create a README file
            (repo_path / "README.md").write_text(
                "# Test Project\nA test project"
            )

            config = Config(repo_path=repo_path)

            assert config.repo_path == repo_path.resolve()
            assert config.ai_provider == "github"
            assert config.ai_model == "gpt-4o-mini"
            assert not config.skip_validation

    def test_custom_config_from_file(self) -> None:
        """Test loading configuration from file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            config_file = repo_path / "config.yml"

            # Create README and config files
            (repo_path / "README.md").write_text(
                "# Test Project\nA test project"
            )

            config_data = {
                "ai": {
                    "provider": "anthropic",
                    "model": "claude-3-sonnet-20240229",
                },
                "validation": {"skip": True},
            }

            with open(config_file, "w") as f:
                yaml.dump(config_data, f)

            config = Config.load(config_file=config_file, repo_path=repo_path)

            assert config.ai_provider == "anthropic"
            assert config.ai_model == "claude-3-sonnet-20240229"
            assert config.skip_validation is True

    def test_environment_variables(self) -> None:
        """Test configuration from environment variables."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text(
                "# Test Project\nA test project"
            )

            with patch.dict(
                os.environ,
                {
                    "GITHUB_TOKEN": "test-token",
                    "GITHUB_REPOSITORY": "owner/repo",
                },
            ):
                config = Config(
                    repo_path=repo_path,
                    github_token=os.getenv("GITHUB_TOKEN"),
                    github_repo=os.getenv("GITHUB_REPOSITORY"),
                )

                assert config.github_token == "test-token"
                assert config.github_repo == "owner/repo"

    def test_validation_errors(self) -> None:
        """Test configuration validation errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text(
                "# Test Project\nA test project"
            )

            # Test invalid AI provider
            with pytest.raises(ValueError, match="Unsupported AI provider"):
                Config(repo_path=repo_path, ai_provider="invalid")

            # Test invalid repository format
            with pytest.raises(
                ValueError, match="GitHub repository must be in format"
            ):
                Config(repo_path=repo_path, github_repo="invalid-format")

    def test_readme_detection(self) -> None:
        """Test README file detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            # Test with README.md
            readme_path = repo_path / "README.md"
            readme_path.write_text("# Test Project")

            config = Config(repo_path=repo_path)
            assert config.readme_path.name == "README.md"
            assert config.readme_path.exists()

            # Test with README.rst
            readme_path.unlink()
            readme_rst = repo_path / "README.rst"
            readme_rst.write_text("Test Project\n============")

            config = Config(repo_path=repo_path)
            assert config.readme_path.name == "README.rst"
            assert config.readme_path.exists()

    def test_docs_path(self) -> None:
        """Test docs directory path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            assert config.docs_path.name == "docs"
            assert config.docs_path.parent.resolve() == repo_path.resolve()

    def test_wiki_structure(self) -> None:
        """Test default wiki structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            structure = config.wiki_structure

            assert "Home" in structure
            assert "Getting Started" in structure
            assert "User Guide" in structure
            assert isinstance(structure["Home"], list)
