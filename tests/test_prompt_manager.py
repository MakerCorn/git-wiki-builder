"""Tests for prompt manager."""

import tempfile
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest
import yaml

from git_wiki_builder.config import Config
from git_wiki_builder.prompt_manager import PromptManager


class TestPromptManager:
    """Test prompt manager functionality."""

    def test_init_without_custom_prompts(self) -> None:
        """Test initialization without custom prompts file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)

            assert prompt_manager.config == config
            assert prompt_manager.custom_prompts == {}

    def test_init_with_custom_prompts(self) -> None:
        """Test initialization with custom prompts file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            # Create custom prompts file
            prompts_file = repo_path / "custom_prompts.yml"
            custom_prompts = {
                "home": "Custom home prompt",
                "api": "Custom API prompt",
            }
            with open(prompts_file, "w") as f:
                yaml.dump(custom_prompts, f)

            config = Config(repo_path=repo_path, prompt_file=prompts_file)
            prompt_manager = PromptManager(config)

            assert prompt_manager.custom_prompts == custom_prompts

    def test_load_custom_prompts_nonexistent_file(self) -> None:
        """Test loading custom prompts from nonexistent file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(
                repo_path=repo_path, prompt_file=Path("nonexistent.yml")
            )
            prompt_manager = PromptManager(config)

            assert prompt_manager.custom_prompts == {}

    def test_load_custom_prompts_invalid_yaml(self) -> None:
        """Test loading custom prompts from invalid YAML file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            # Create invalid YAML file
            prompts_file = repo_path / "invalid.yml"
            prompts_file.write_text("invalid: yaml: content: [")

            config = Config(repo_path=repo_path, prompt_file=prompts_file)

            with patch("logging.Logger.warning") as mock_warning:
                prompt_manager = PromptManager(config)
                mock_warning.assert_called_once()

            assert prompt_manager.custom_prompts == {}

    def test_load_custom_prompts_empty_file(self) -> None:
        """Test loading custom prompts from empty file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            # Create empty YAML file
            prompts_file = repo_path / "empty.yml"
            prompts_file.write_text("")

            config = Config(repo_path=repo_path, prompt_file=prompts_file)
            prompt_manager = PromptManager(config)

            assert prompt_manager.custom_prompts == {}

    def test_load_custom_prompts_file_error(self) -> None:
        """Test loading custom prompts when file read fails."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            # Create a valid file first
            prompts_file = repo_path / "prompts.yml"
            prompts_file.write_text("valid: yaml")

            config = Config(repo_path=repo_path, prompt_file=prompts_file)

            with patch(
                "builtins.open", side_effect=IOError("File read error")
            ):
                with patch(
                    "git_wiki_builder.prompt_manager.logger.warning"
                ) as mock_warning:
                    prompt_manager = PromptManager(config)
                    mock_warning.assert_called_once()

            assert prompt_manager.custom_prompts == {}

    def test_get_home_prompt_default(self) -> None:
        """Test getting default home prompt."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)

            prompt = prompt_manager.get_home_prompt()

            assert "Create a comprehensive Home page" in prompt
            assert "{project_name}" in prompt
            assert "{project_description}" in prompt

    def test_get_home_prompt_custom(self) -> None:
        """Test getting custom home prompt."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)
            prompt_manager.custom_prompts = {
                "home": "Custom home prompt for {project_name}"
            }

            prompt = prompt_manager.get_home_prompt()

            assert prompt == "Custom home prompt for {project_name}"

    def test_get_page_prompt_custom_specific(self) -> None:
        """Test getting custom prompt for specific page."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)
            prompt_manager.custom_prompts = {
                "test section_test page": "Custom specific prompt"
            }

            prompt = prompt_manager.get_page_prompt(
                "Test Page", "Test Section"
            )

            assert prompt == "Custom specific prompt"

    def test_get_page_prompt_custom_section(self) -> None:
        """Test getting custom prompt for section."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)
            prompt_manager.custom_prompts = {
                "api_reference": "Custom API section prompt"
            }

            prompt = prompt_manager.get_page_prompt(
                "Overview", "API Reference"
            )

            assert prompt == "Custom API section prompt"

    def test_get_page_prompt_installation(self) -> None:
        """Test getting installation prompt."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)

            prompt = prompt_manager.get_page_prompt(
                "Installation", "Getting Started"
            )

            assert "Create comprehensive installation documentation" in prompt
            assert "{dependencies}" in prompt

    def test_get_page_prompt_configuration(self) -> None:
        """Test getting configuration prompt."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)

            prompt = prompt_manager.get_page_prompt("Configuration", "Setup")

            assert "Create detailed configuration documentation" in prompt
            assert "configuration options" in prompt

    def test_get_page_prompt_api_by_section(self) -> None:
        """Test getting API prompt by section name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)

            prompt = prompt_manager.get_page_prompt(
                "Overview", "API Reference"
            )

            assert "Create comprehensive API documentation" in prompt
            assert "{has_api}" in prompt

    def test_get_page_prompt_api_by_page(self) -> None:
        """Test getting API prompt by page name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)

            prompt = prompt_manager.get_page_prompt(
                "API Guide", "Documentation"
            )

            assert "Create comprehensive API documentation" in prompt

    def test_get_page_prompt_development_by_section(self) -> None:
        """Test getting development prompt by section name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)

            prompt = prompt_manager.get_page_prompt("Setup", "Development")

            assert "Create comprehensive development documentation" in prompt
            assert "{has_tests}" in prompt

    def test_get_page_prompt_development_by_page(self) -> None:
        """Test getting development prompt by page name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)

            prompt = prompt_manager.get_page_prompt(
                "Development Guide", "Documentation"
            )

            assert "Create comprehensive development documentation" in prompt

    def test_get_page_prompt_deployment_by_section(self) -> None:
        """Test getting deployment prompt by section name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)

            prompt = prompt_manager.get_page_prompt("Guide", "Deployment")

            assert "Create comprehensive deployment documentation" in prompt
            assert "{has_docker}" in prompt

    def test_get_page_prompt_deployment_by_page(self) -> None:
        """Test getting deployment prompt by page name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)

            prompt = prompt_manager.get_page_prompt(
                "Deploy to AWS", "Documentation"
            )

            assert "Create comprehensive deployment documentation" in prompt

    def test_get_page_prompt_faq(self) -> None:
        """Test getting FAQ prompt."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)

            prompt = prompt_manager.get_page_prompt("FAQ", "Support")

            assert "Create a comprehensive FAQ section" in prompt
            assert "common user questions" in prompt

    def test_get_page_prompt_faq_questions(self) -> None:
        """Test getting FAQ prompt for questions page."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)

            prompt = prompt_manager.get_page_prompt(
                "Common Questions", "Support"
            )

            assert "Create a comprehensive FAQ section" in prompt

    def test_get_page_prompt_troubleshooting(self) -> None:
        """Test getting troubleshooting prompt."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)

            prompt = prompt_manager.get_page_prompt(
                "Troubleshooting", "Support"
            )

            assert (
                "Create comprehensive troubleshooting documentation" in prompt
            )
            assert "common error messages" in prompt

    def test_get_page_prompt_troubleshooting_problems(self) -> None:
        """Test getting troubleshooting prompt for problems page."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)

            prompt = prompt_manager.get_page_prompt(
                "Common Problems", "Support"
            )

            assert (
                "Create comprehensive troubleshooting documentation" in prompt
            )

    def test_get_page_prompt_examples(self) -> None:
        """Test getting examples prompt."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)

            prompt = prompt_manager.get_page_prompt(
                "Examples", "Documentation"
            )

            assert (
                "Create comprehensive examples and usage documentation"
                in prompt
            )
            assert "runnable code examples" in prompt

    def test_get_page_prompt_examples_usage(self) -> None:
        """Test getting examples prompt for usage page."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)

            prompt = prompt_manager.get_page_prompt(
                "Usage Guide", "Documentation"
            )

            assert (
                "Create comprehensive examples and usage documentation"
                in prompt
            )

    def test_get_page_prompt_generic(self) -> None:
        """Test getting generic prompt."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)

            prompt = prompt_manager.get_page_prompt(
                "Custom Page", "Other Section"
            )

            assert (
                'Create comprehensive documentation for the "{page_name}" page'
                in prompt
            )
            assert "{section_name}" in prompt
            assert "{project_name}" in prompt

    def test_get_installation_prompt(self) -> None:
        """Test installation prompt content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)

            prompt = prompt_manager._get_installation_prompt()

            assert "Create comprehensive installation documentation" in prompt
            assert "multiple installation methods" in prompt
            assert "{has_docker}" in prompt

    def test_get_configuration_prompt(self) -> None:
        """Test configuration prompt content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)

            prompt = prompt_manager._get_configuration_prompt()

            assert "Create detailed configuration documentation" in prompt
            assert "configuration options" in prompt
            assert "environment variable" in prompt

    def test_get_api_prompt(self) -> None:
        """Test API prompt content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)

            prompt = prompt_manager._get_api_prompt()

            assert "Create comprehensive API documentation" in prompt
            assert "all endpoints" in prompt
            assert "{has_api}" in prompt

    def test_get_development_prompt(self) -> None:
        """Test development prompt content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)

            prompt = prompt_manager._get_development_prompt()

            assert "Create comprehensive development documentation" in prompt
            assert "development environment setup" in prompt
            assert "{has_tests}" in prompt

    def test_get_deployment_prompt(self) -> None:
        """Test deployment prompt content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)

            prompt = prompt_manager._get_deployment_prompt()

            assert "Create comprehensive deployment documentation" in prompt
            assert "deployment environments" in prompt
            assert "{has_docker}" in prompt

    def test_get_faq_prompt(self) -> None:
        """Test FAQ prompt content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)

            prompt = prompt_manager._get_faq_prompt()

            assert "Create a comprehensive FAQ section" in prompt
            assert "common user questions" in prompt
            assert "Q&A structure" in prompt

    def test_get_troubleshooting_prompt(self) -> None:
        """Test troubleshooting prompt content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)

            prompt = prompt_manager._get_troubleshooting_prompt()

            assert (
                "Create comprehensive troubleshooting documentation" in prompt
            )
            assert "common error messages" in prompt
            assert "diagnostic steps" in prompt

    def test_get_examples_prompt(self) -> None:
        """Test examples prompt content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)

            prompt = prompt_manager._get_examples_prompt()

            assert (
                "Create comprehensive examples and usage documentation"
                in prompt
            )
            assert "runnable code examples" in prompt
            assert "best practices" in prompt

    def test_get_generic_prompt(self) -> None:
        """Test generic prompt content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            prompt_manager = PromptManager(config)

            prompt = prompt_manager._get_generic_prompt()

            assert "Create comprehensive documentation" in prompt
            assert "{page_name}" in prompt
            assert "{section_name}" in prompt
