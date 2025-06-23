"""Configuration management for Git Wiki Builder."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from dotenv import load_dotenv

from . import __version__


class Config:
    """Configuration class for Git Wiki Builder."""

    def __init__(
        self,
        repo_path: Path,
        ai_provider: str = "github",
        ai_model: Optional[str] = None,
        github_token: Optional[str] = None,
        github_repo: Optional[str] = None,
        output_dir: Optional[Path] = None,
        prompt_file: Optional[Path] = None,
        skip_validation: bool = False,
        custom_config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize configuration.

        Args:
            repo_path: Path to the repository
            ai_provider: AI provider to use ('openai' or 'anthropic')
            ai_model: Specific AI model to use
            github_token: GitHub authentication token
            github_repo: GitHub repository in format 'owner/repo'
            output_dir: Directory to save generated files
            prompt_file: Path to custom prompt file
            skip_validation: Skip markdown validation
            custom_config: Additional configuration from file
        """
        self.repo_path = repo_path.resolve()
        self.ai_provider = ai_provider.lower()
        self.github_token = github_token
        self.github_repo = github_repo
        self.output_dir = output_dir
        self.prompt_file = prompt_file
        self.skip_validation = skip_validation
        self.version = __version__

        # Load environment variables
        load_dotenv(self.repo_path / ".env")

        # Set AI model defaults
        if ai_model:
            self.ai_model = ai_model
        elif self.ai_provider == "github":
            self.ai_model = "gpt-4o-mini"  # GitHub Models default
        elif self.ai_provider == "openai":
            self.ai_model = "gpt-4"
        elif self.ai_provider == "anthropic":
            self.ai_model = "claude-3-sonnet-20240229"
        else:
            raise ValueError(f"Unsupported AI provider: {ai_provider}")

        # Merge custom configuration
        if custom_config:
            self._merge_config(custom_config)

        # Validate configuration
        self._validate()

    def _merge_config(self, custom_config: Dict[str, Any]) -> None:
        """Merge custom configuration."""
        # AI configuration
        ai_config = custom_config.get("ai", {})
        if "provider" in ai_config:
            self.ai_provider = ai_config["provider"].lower()
        if "model" in ai_config:
            self.ai_model = ai_config["model"]

        # GitHub configuration
        github_config = custom_config.get("github", {})
        if "token" in github_config:
            self.github_token = github_config["token"]
        if "repository" in github_config:
            self.github_repo = github_config["repository"]

        # Output configuration
        output_config = custom_config.get("output", {})
        if "directory" in output_config:
            self.output_dir = Path(output_config["directory"])

        # Prompt configuration
        prompt_config = custom_config.get("prompt", {})
        if "file" in prompt_config:
            self.prompt_file = Path(prompt_config["file"])

        # Validation configuration
        validation_config = custom_config.get("validation", {})
        if "skip" in validation_config:
            self.skip_validation = validation_config["skip"]

    def _validate(self) -> None:
        """Validate configuration."""
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {self.repo_path}")

        if self.ai_provider not in ["github", "openai", "anthropic"]:
            raise ValueError(f"Unsupported AI provider: {self.ai_provider}")

        # Validate GitHub repository format
        if self.github_repo and "/" not in self.github_repo:
            raise ValueError("GitHub repository must be in format 'owner/repo'")

    def validate_for_generation(self) -> None:
        """Validate configuration for content generation (requires API keys)."""
        # Check for required API keys
        if self.ai_provider == "github" and not os.getenv("GITHUB_TOKEN"):
            raise ValueError(
                "GITHUB_TOKEN environment variable is required for GitHub Models"
            )

        if self.ai_provider == "openai" and not os.getenv("OPENAI_API_KEY"):
            raise ValueError(
                "OPENAI_API_KEY environment variable is required for OpenAI"
            )

        if self.ai_provider == "anthropic" and not os.getenv("ANTHROPIC_API_KEY"):
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is required for Anthropic"
            )

    @property
    def docs_path(self) -> Path:
        """Get the docs directory path."""
        return self.repo_path / "docs"

    @property
    def readme_path(self) -> Path:
        """Get the README file path."""
        for readme_name in ["README.md", "README.rst", "README.txt", "README"]:
            readme_path = self.repo_path / readme_name
            if readme_path.exists():
                return readme_path
        raise FileNotFoundError("No README file found in repository")

    @property
    def wiki_structure(self) -> Dict[str, List[str]]:
        """Get the default wiki structure."""
        return {
            "Home": ["overview", "quick_start"],
            "Getting Started": ["installation", "configuration", "first_steps"],
            "User Guide": ["features", "usage", "examples"],
            "API Reference": ["api_overview", "endpoints", "authentication"],
            "Development": ["contributing", "development_setup", "testing"],
            "Deployment": ["deployment_guide", "environment_setup", "troubleshooting"],
            "FAQ": ["common_questions", "known_issues"],
            "Changelog": ["release_notes", "migration_guide"],
        }

    @classmethod
    def load(
        cls,
        config_file: Optional[Path] = None,
        repo_path: Path = Path("."),
        **kwargs: Any,
    ) -> "Config":
        """Load configuration from file and arguments.

        Args:
            config_file: Path to configuration file
            repo_path: Path to repository
            **kwargs: Additional configuration arguments

        Returns:
            Config instance
        """
        custom_config: Dict[str, Any] = {}

        # Load from config file
        if config_file and config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                if config_file.suffix.lower() in [".yml", ".yaml"]:
                    custom_config = yaml.safe_load(f) or {}
                else:
                    raise ValueError(
                        f"Unsupported config file format: {config_file.suffix}"
                    )

        # Look for default config file
        elif not config_file:
            default_config_files = [
                repo_path / ".git-wiki-builder.yml",
                repo_path / ".git-wiki-builder.yaml",
                repo_path / "git-wiki-builder.yml",
                repo_path / "git-wiki-builder.yaml",
            ]

            for default_file in default_config_files:
                if default_file.exists():
                    with open(default_file, "r", encoding="utf-8") as f:
                        custom_config = yaml.safe_load(f) or {}
                    break

        return cls(
            repo_path=repo_path,
            custom_config=custom_config,
            **kwargs,
        )
