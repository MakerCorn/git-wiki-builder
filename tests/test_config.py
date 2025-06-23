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

    def test_ai_model_defaults(self) -> None:
        """Test AI model defaults for different providers."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            # Test OpenAI default
            config = Config(repo_path=repo_path, ai_provider="openai")
            assert config.ai_model == "gpt-4"

            # Test Anthropic default
            config = Config(repo_path=repo_path, ai_provider="anthropic")
            assert config.ai_model == "claude-3-sonnet-20240229"

            # Test custom model
            config = Config(
                repo_path=repo_path,
                ai_provider="github",
                ai_model="custom-model",
            )
            assert config.ai_model == "custom-model"

    def test_merge_config(self) -> None:
        """Test configuration merging."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            custom_config = {
                "ai": {"provider": "openai", "model": "gpt-3.5-turbo"},
                "github": {"token": "test-token", "repository": "owner/repo"},
                "output": {"directory": "/tmp/output"},
                "prompt": {"file": "/tmp/prompts.yml"},
                "validation": {"skip": True},
            }

            config = Config(repo_path=repo_path, custom_config=custom_config)

            assert config.ai_provider == "openai"
            assert config.ai_model == "gpt-3.5-turbo"
            assert config.github_token == "test-token"
            assert config.github_repo == "owner/repo"
            assert config.output_dir == Path("/tmp/output")
            assert config.prompt_file == Path("/tmp/prompts.yml")
            assert config.skip_validation is True

    def test_validation_errors_extended(self) -> None:
        """Test additional validation errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            # Test nonexistent repository path
            with pytest.raises(
                ValueError, match="Repository path does not exist"
            ):
                Config(repo_path=Path("/nonexistent/path"))

    def test_validate_for_generation(self) -> None:
        """Test validation for generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path, ai_provider="github")

            # Test missing environment variables
            with patch.dict(os.environ, {}, clear=True):
                with pytest.raises(
                    ValueError,
                    match="GITHUB_TOKEN environment variable is required",
                ):
                    config.validate_for_generation()

            # Test OpenAI validation
            config.ai_provider = "openai"
            with patch.dict(os.environ, {}, clear=True):
                with pytest.raises(
                    ValueError,
                    match="OPENAI_API_KEY environment variable is required",
                ):
                    config.validate_for_generation()

            # Test Anthropic validation
            config.ai_provider = "anthropic"
            with patch.dict(os.environ, {}, clear=True):
                with pytest.raises(
                    ValueError,
                    match="ANTHROPIC_API_KEY environment variable is required",
                ):
                    config.validate_for_generation()

    def test_readme_path_not_found(self) -> None:
        """Test README path when no README exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            # Don't create any README file

            config = Config(repo_path=repo_path)

            with pytest.raises(
                FileNotFoundError, match="No README file found"
            ):
                _ = config.readme_path

    def test_load_config_from_file(self) -> None:
        """Test loading configuration from file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config_file = repo_path / "test-config.yml"
            config_data = {
                "ai": {
                    "provider": "anthropic",
                    "model": "claude-3-haiku-20240307",
                }
            }

            with open(config_file, "w") as f:
                yaml.dump(config_data, f)

            config = Config.load(config_file=config_file, repo_path=repo_path)

            assert config.ai_provider == "anthropic"
            assert config.ai_model == "claude-3-haiku-20240307"

    def test_load_config_unsupported_format(self) -> None:
        """Test loading config with unsupported format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config_file = repo_path / "test-config.json"
            config_file.write_text('{"ai": {"provider": "openai"}}')

            with pytest.raises(
                ValueError, match="Unsupported config file format"
            ):
                Config.load(config_file=config_file, repo_path=repo_path)

    def test_load_config_default_files(self) -> None:
        """Test loading from default config files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            # Create default config file
            default_config = repo_path / ".git-wiki-builder.yml"
            config_data = {"ai": {"provider": "openai", "model": "gpt-4"}}

            with open(default_config, "w") as f:
                yaml.dump(config_data, f)

            config = Config.load(repo_path=repo_path)

            assert config.ai_provider == "openai"
            assert config.ai_model == "gpt-4"

    def test_load_config_no_default_files(self) -> None:
        """Test loading when no default config files exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config.load(repo_path=repo_path)

            # Should use defaults
            assert config.ai_provider == "github"
            assert config.ai_model == "gpt-4o-mini"

    def test_validate_unsupported_provider(self) -> None:
        """Test validation with unsupported AI provider."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path, ai_provider="github")
            # Manually change to invalid provider after creation
            config.ai_provider = "invalid"

            with pytest.raises(
                ValueError, match="Unsupported AI provider: invalid"
            ):
                config._validate()
