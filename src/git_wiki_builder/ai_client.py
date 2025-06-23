"""AI client for content generation."""

import logging
import os
from typing import Any, Dict

try:
    import anthropic  # type: ignore[import-not-found]
except ImportError:
    anthropic = None

from .config import Config

logger = logging.getLogger(__name__)


class MockAIClient:
    """Mock AI client for testing and dry runs."""

    def __init__(self, config: Config) -> None:
        """Initialize mock AI client."""
        self.config = config

    def generate_content(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate mock content."""
        page_name = context.get("page_name", "Unknown Page")
        project_name = context.get("project_name", "Unknown Project")
        page_name_formatted = page_name.lower().replace("_", " ")

        return f"""# {page_name}

This is mock content generated for the {page_name} page of {project_name}.

## Overview

This page would contain documentation about {page_name_formatted}.

## Key Information

- Project: {project_name}
- Page: {page_name}
- Generated with: Mock AI Client

## Content Structure

The actual content would be generated using AI based on:
- Project analysis
- Custom prompts
- Documentation structure

*Note: This is placeholder content generated in mock mode.*
"""


class AIClient:
    """Client for AI content generation."""

    def __init__(self, config: Config) -> None:
        """Initialize AI client.

        Args:
            config: Configuration instance
        """
        self.config = config
        self.client = self._initialize_client()

    def _initialize_client(self) -> Any:
        """Initialize the appropriate AI client."""
        if self.config.ai_provider == "github":
            try:
                import openai

                return openai.OpenAI(
                    base_url="https://models.inference.ai.azure.com",
                    api_key=os.getenv("GITHUB_TOKEN"),
                )
            except ImportError:
                raise ImportError(
                    "OpenAI package not installed. Run: pip install openai"
                )

        elif self.config.ai_provider == "openai":
            try:
                import openai

                return openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            except ImportError:
                raise ImportError(
                    "OpenAI package not installed. Run: pip install openai"
                )

        elif self.config.ai_provider == "anthropic":
            if anthropic is None:
                raise ImportError(
                    "Anthropic package not installed. Run: pip install "
                    "anthropic"
                )
            return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        else:
            raise ValueError(
                f"Unsupported AI provider: {self.config.ai_provider}"
            )

    def generate_content(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate content using AI.

        Args:
            prompt: The prompt template
            context: Context variables for the prompt

        Returns:
            Generated content
        """
        # Format prompt with context
        formatted_prompt = self._format_prompt(prompt, context)

        logger.debug(
            f"Generating content with {self.config.ai_provider} "
            f"({self.config.ai_model})"
        )

        if self.config.ai_provider in ["github", "openai"]:
            return self._generate_openai_content(formatted_prompt)
        elif self.config.ai_provider == "anthropic":
            return self._generate_anthropic_content(formatted_prompt)
        else:
            raise ValueError(
                f"Unsupported AI provider: {self.config.ai_provider}"
            )

    def _format_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Format prompt with context variables.

        Args:
            prompt: The prompt template
            context: Context variables

        Returns:
            Formatted prompt
        """
        try:
            return prompt.format(**context)
        except KeyError as e:
            logger.warning(f"Missing context variable: {e}")
            # Return prompt with missing variables as placeholders
            return prompt

    def _generate_openai_content(self, prompt: str) -> str:
        """Generate content using OpenAI.

        Args:
            prompt: Formatted prompt

        Returns:
            Generated content
        """
        try:
            response = self.client.chat.completions.create(
                model=self.config.ai_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a technical documentation expert. "
                            "Generate high-quality, "
                            "well-structured markdown documentation that "
                            "follows best practices. "
                            "Ensure proper heading hierarchy, clear "
                            "formatting, and comprehensive "
                            "coverage of the requested topic."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=4000,
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI")

            return str(content).strip()

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def _generate_anthropic_content(self, prompt: str) -> str:
        """Generate content using Anthropic Claude.

        Args:
            prompt: Formatted prompt

        Returns:
            Generated content
        """
        try:
            response = self.client.messages.create(
                model=self.config.ai_model,
                max_tokens=4000,
                temperature=0.3,
                system=(
                    "You are a technical documentation expert. "
                    "Generate high-quality, "
                    "well-structured markdown documentation that "
                    "follows best practices. "
                    "Ensure proper heading hierarchy, clear "
                    "formatting, and comprehensive "
                    "coverage of the requested topic."
                ),
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.content[0].text
            if not content:
                raise ValueError("Empty response from Anthropic")

            return str(content).strip()

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
