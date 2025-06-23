"""Tests for AI client."""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from git_wiki_builder.ai_client import AIClient, MockAIClient
from git_wiki_builder.config import Config


class TestMockAIClient:
    """Test mock AI client functionality."""

    def test_init(self) -> None:
        """Test mock AI client initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            client = MockAIClient(config)

            assert client.config == config

    def test_generate_content_basic(self) -> None:
        """Test basic content generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            client = MockAIClient(config)

            context = {
                "page_name": "Installation",
                "project_name": "Test Project",
            }

            content = client.generate_content("Test prompt", context)

            assert "# Installation" in content
            assert "Test Project" in content
            assert "Mock AI Client" in content

    def test_generate_content_with_underscore_page(self) -> None:
        """Test content generation with underscore in page name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            client = MockAIClient(config)

            context = {
                "page_name": "API_Reference",
                "project_name": "Test Project",
            }

            content = client.generate_content("Test prompt", context)

            assert "# API_Reference" in content
            assert "api reference" in content  # Formatted version

    def test_generate_content_missing_context(self) -> None:
        """Test content generation with missing context."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            client = MockAIClient(config)

            context = {}  # Missing page_name and project_name

            content = client.generate_content("Test prompt", context)

            assert "# Unknown Page" in content
            assert "Unknown Project" in content


class TestAIClient:
    """Test AI client functionality."""

    def test_init_github_provider(self) -> None:
        """Test initialization with GitHub provider."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path, ai_provider="github")

            with patch("openai.OpenAI") as mock_openai:
                client = AIClient(config)

                assert client.config == config
                mock_openai.assert_called_once_with(
                    base_url="https://models.inference.ai.azure.com",
                    api_key=os.getenv("GITHUB_TOKEN"),
                )

    def test_init_openai_provider(self) -> None:
        """Test initialization with OpenAI provider."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path, ai_provider="openai")

            with patch("openai.OpenAI") as mock_openai:
                client = AIClient(config)

                assert client.config == config
                mock_openai.assert_called_once_with(
                    api_key=os.getenv("OPENAI_API_KEY")
                )

    def test_init_anthropic_provider_available(self) -> None:
        """Test initialization with Anthropic provider when available."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path, ai_provider="anthropic")

            with patch(
                "git_wiki_builder.ai_client.anthropic"
            ) as mock_anthropic:
                mock_anthropic.Anthropic.return_value = Mock()
                client = AIClient(config)

                assert client.config == config
                mock_anthropic.Anthropic.assert_called_once_with(
                    api_key=os.getenv("ANTHROPIC_API_KEY")
                )

    def test_init_anthropic_provider_unavailable(self) -> None:
        """Test initialization with Anthropic provider when unavailable."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path, ai_provider="anthropic")

            with patch("git_wiki_builder.ai_client.anthropic", None):
                with pytest.raises(
                    ImportError, match="Anthropic package not installed"
                ):
                    AIClient(config)

    def test_init_github_openai_not_installed(self) -> None:
        """Test initialization with GitHub provider when OpenAI not installed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path, ai_provider="github")

            with patch(
                "builtins.__import__",
                side_effect=ImportError("No module named 'openai'"),
            ):
                with pytest.raises(
                    ImportError, match="OpenAI package not installed"
                ):
                    AIClient(config)

    def test_init_openai_not_installed(self) -> None:
        """Test initialization with OpenAI provider when OpenAI not installed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path, ai_provider="openai")

            with patch(
                "builtins.__import__",
                side_effect=ImportError("No module named 'openai'"),
            ):
                with pytest.raises(
                    ImportError, match="OpenAI package not installed"
                ):
                    AIClient(config)

    def test_init_unsupported_provider(self) -> None:
        """Test initialization with unsupported provider."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path, ai_provider="github")
            # Manually change to invalid after config creation
            config.ai_provider = "invalid"

            with pytest.raises(
                ValueError, match="Unsupported AI provider: invalid"
            ):
                AIClient(config)

    def test_format_prompt_success(self) -> None:
        """Test successful prompt formatting."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path, ai_provider="github")

            with patch("openai.OpenAI"):
                client = AIClient(config)

                prompt = "Project: {project_name}, Page: {page_name}"
                context = {"project_name": "Test", "page_name": "Home"}

                result = client._format_prompt(prompt, context)

                assert result == "Project: Test, Page: Home"

    def test_format_prompt_missing_variable(self) -> None:
        """Test prompt formatting with missing variable."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path, ai_provider="github")

            with patch("openai.OpenAI"):
                client = AIClient(config)

                prompt = "Project: {project_name}, Page: {missing_var}"
                context = {"project_name": "Test"}

                with patch("logging.Logger.warning") as mock_warning:
                    result = client._format_prompt(prompt, context)
                    mock_warning.assert_called_once()

                assert result == prompt  # Returns original prompt

    def test_generate_content_github(self) -> None:
        """Test content generation with GitHub provider."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path, ai_provider="github")

            # Mock OpenAI response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Generated content"

            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response

            with patch("openai.OpenAI", return_value=mock_client):
                client = AIClient(config)

                context = {"project_name": "Test"}
                result = client.generate_content(
                    "Test prompt: {project_name}", context
                )

                assert result == "Generated content"
                mock_client.chat.completions.create.assert_called_once()

    def test_generate_content_openai(self) -> None:
        """Test content generation with OpenAI provider."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path, ai_provider="openai")

            # Mock OpenAI response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Generated content"

            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response

            with patch("openai.OpenAI", return_value=mock_client):
                client = AIClient(config)

                context = {"project_name": "Test"}
                result = client.generate_content(
                    "Test prompt: {project_name}", context
                )

                assert result == "Generated content"

    def test_generate_content_anthropic(self) -> None:
        """Test content generation with Anthropic provider."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path, ai_provider="anthropic")

            # Mock Anthropic response
            mock_response = Mock()
            mock_response.content = [Mock()]
            mock_response.content[0].text = "Generated content"

            mock_client = Mock()
            mock_client.messages.create.return_value = mock_response

            with patch(
                "git_wiki_builder.ai_client.anthropic"
            ) as mock_anthropic:
                mock_anthropic.Anthropic.return_value = mock_client
                client = AIClient(config)

                context = {"project_name": "Test"}
                result = client.generate_content(
                    "Test prompt: {project_name}", context
                )

                assert result == "Generated content"
                mock_client.messages.create.assert_called_once()

    def test_generate_content_unsupported_provider(self) -> None:
        """Test content generation with unsupported provider."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path, ai_provider="github")

            with patch("openai.OpenAI"):
                client = AIClient(config)
                # Manually change provider to test error case
                client.config.ai_provider = "invalid"

                with pytest.raises(
                    ValueError, match="Unsupported AI provider: invalid"
                ):
                    client.generate_content("Test prompt", {})

    def test_generate_openai_content_empty_response(self) -> None:
        """Test OpenAI content generation with empty response."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path, ai_provider="github")

            # Mock empty response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = None

            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response

            with patch("openai.OpenAI", return_value=mock_client):
                client = AIClient(config)

                with pytest.raises(
                    ValueError, match="Empty response from OpenAI"
                ):
                    client._generate_openai_content("Test prompt")

    def test_generate_openai_content_api_error(self) -> None:
        """Test OpenAI content generation with API error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path, ai_provider="github")

            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception(
                "API Error"
            )

            with patch("openai.OpenAI", return_value=mock_client):
                client = AIClient(config)

                with patch("logging.Logger.error") as mock_error:
                    with pytest.raises(Exception, match="API Error"):
                        client._generate_openai_content("Test prompt")
                    mock_error.assert_called_once()

    def test_generate_anthropic_content_empty_response(self) -> None:
        """Test Anthropic content generation with empty response."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path, ai_provider="anthropic")

            # Mock empty response
            mock_response = Mock()
            mock_response.content = [Mock()]
            mock_response.content[0].text = None

            mock_client = Mock()
            mock_client.messages.create.return_value = mock_response

            with patch(
                "git_wiki_builder.ai_client.anthropic"
            ) as mock_anthropic:
                mock_anthropic.Anthropic.return_value = mock_client
                client = AIClient(config)

                with pytest.raises(
                    ValueError, match="Empty response from Anthropic"
                ):
                    client._generate_anthropic_content("Test prompt")

    def test_generate_anthropic_content_api_error(self) -> None:
        """Test Anthropic content generation with API error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path, ai_provider="anthropic")

            mock_client = Mock()
            mock_client.messages.create.side_effect = Exception("API Error")

            with patch(
                "git_wiki_builder.ai_client.anthropic"
            ) as mock_anthropic:
                mock_anthropic.Anthropic.return_value = mock_client
                client = AIClient(config)

                with patch("logging.Logger.error") as mock_error:
                    with pytest.raises(Exception, match="API Error"):
                        client._generate_anthropic_content("Test prompt")
                    mock_error.assert_called_once()

    def test_generate_content_with_whitespace(self) -> None:
        """Test content generation strips whitespace."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path, ai_provider="github")

            # Mock OpenAI response with whitespace
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = (
                "  \n Generated content \n  "
            )

            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response

            with patch("openai.OpenAI", return_value=mock_client):
                client = AIClient(config)

                result = client._generate_openai_content("Test prompt")

                assert result == "Generated content"

    def test_anthropic_content_with_whitespace(self) -> None:
        """Test Anthropic content generation strips whitespace."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path, ai_provider="anthropic")

            # Mock Anthropic response with whitespace
            mock_response = Mock()
            mock_response.content = [Mock()]
            mock_response.content[0].text = "  \n Generated content \n  "

            mock_client = Mock()
            mock_client.messages.create.return_value = mock_response

            with patch(
                "git_wiki_builder.ai_client.anthropic"
            ) as mock_anthropic:
                mock_anthropic.Anthropic.return_value = mock_client
                client = AIClient(config)

                result = client._generate_anthropic_content("Test prompt")

                assert result == "Generated content"
