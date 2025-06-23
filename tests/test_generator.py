"""Tests for wiki generator."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from git_wiki_builder.config import Config
from git_wiki_builder.content_analyzer import ProjectAnalysis
from git_wiki_builder.generator import WikiGenerator


class TestWikiGenerator:
    """Test wiki generator functionality."""

    def create_mock_analysis(self) -> Mock:
        """Create mock project analysis."""
        analysis = Mock(spec=ProjectAnalysis)
        analysis.project_name = "Test Project"
        analysis.description = "A test project for analysis"
        analysis.readme_content = "# Test Project\n\nA sample project."
        analysis.docs_content = {"guide.md": "# Guide\nUser guide content."}
        analysis.code_structure = {"Python": ["main.py", "utils.py"]}
        analysis.dependencies = ["requests", "click"]
        analysis.key_features = ["Feature 1", "Feature 2"]
        analysis.quick_start_info = "Quick start instructions"
        analysis.has_api_docs = True
        analysis.has_docker = True
        analysis.has_tests = True
        analysis.has_ci_cd = True
        analysis.files = [Path("README.md"), Path("main.py")]
        return analysis

    def test_init_mock_mode(self) -> None:
        """Test initialization with mock mode."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            generator = WikiGenerator(config, mock_mode=True)

            assert generator.config == config
            assert generator.ai_client.__class__.__name__ == "MockAIClient"
            assert generator.content_analyzer is not None
            assert generator.prompt_manager is not None
            assert generator.validator is not None

    def test_init_normal_mode(self) -> None:
        """Test initialization with normal mode."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)

            with patch(
                "git_wiki_builder.generator.AIClient"
            ) as mock_ai_client:
                generator = WikiGenerator(config, mock_mode=False)

                assert generator.config == config
                mock_ai_client.assert_called_once_with(config)
                assert generator.validator is not None

    def test_init_skip_validation(self) -> None:
        """Test initialization with validation disabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path, skip_validation=True)
            generator = WikiGenerator(config, mock_mode=True)

            assert generator.validator is None

    def test_generate_basic(self) -> None:
        """Test basic wiki generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            generator = WikiGenerator(config, mock_mode=True)

            # Mock the content analyzer
            mock_analysis = self.create_mock_analysis()
            generator.content_analyzer.analyze = Mock(
                return_value=mock_analysis
            )

            wiki_content = generator.generate()

            assert isinstance(wiki_content, dict)
            assert "Home" in wiki_content
            assert len(wiki_content) > 1  # Should have multiple pages

    def test_generate_with_validation_errors(self) -> None:
        """Test generation with validation errors that get fixed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            generator = WikiGenerator(config, mock_mode=True)

            # Mock the content analyzer
            mock_analysis = self.create_mock_analysis()
            generator.content_analyzer.analyze = Mock(
                return_value=mock_analysis
            )

            # Mock validation result with errors
            mock_validation_result = Mock()
            mock_validation_result.is_valid = False
            mock_validation_result.errors = ["Error 1", "Error 2"]

            generator.validator.validate_content = Mock(
                return_value=mock_validation_result
            )
            generator.validator.fix_content = Mock(
                side_effect=lambda x: f"Fixed: {x}"
            )

            wiki_content = generator.generate()

            assert isinstance(wiki_content, dict)
            assert "Home" in wiki_content
            # Content should be fixed
            for content in wiki_content.values():
                assert content.startswith("Fixed:")

    def test_generate_without_validation(self) -> None:
        """Test generation without validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path, skip_validation=True)
            generator = WikiGenerator(config, mock_mode=True)

            # Mock the content analyzer
            mock_analysis = self.create_mock_analysis()
            generator.content_analyzer.analyze = Mock(
                return_value=mock_analysis
            )

            wiki_content = generator.generate()

            assert isinstance(wiki_content, dict)
            assert "Home" in wiki_content

    def test_generate_wiki_structure_with_features(self) -> None:
        """Test wiki structure generation with all features."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            generator = WikiGenerator(config, mock_mode=True)

            mock_analysis = self.create_mock_analysis()

            structure = generator._generate_wiki_structure(mock_analysis)

            assert isinstance(structure, dict)
            assert "API Reference" in structure
            assert "Deployment" in structure
            assert "Development" in structure

            # Check that features were added
            assert "sdk_reference" in structure["API Reference"]
            assert "docker_deployment" in structure["Deployment"]
            assert "running_tests" in structure["Development"]
            assert "ci_cd_pipeline" in structure["Development"]

    def test_generate_wiki_structure_without_features(self) -> None:
        """Test wiki structure generation without optional features."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            generator = WikiGenerator(config, mock_mode=True)

            mock_analysis = self.create_mock_analysis()
            mock_analysis.has_api_docs = False
            mock_analysis.has_docker = False
            mock_analysis.has_tests = False
            mock_analysis.has_ci_cd = False

            structure = generator._generate_wiki_structure(mock_analysis)

            assert isinstance(structure, dict)
            # Should not have added extra pages
            api_pages = structure.get("API Reference", [])
            assert "sdk_reference" not in api_pages

            deployment_pages = structure.get("Deployment", [])
            assert "docker_deployment" not in deployment_pages

    def test_generate_wiki_structure_empty_sections_removed(self) -> None:
        """Test that empty sections are removed from wiki structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            generator = WikiGenerator(config, mock_mode=True)

            # Mock config.wiki_structure property to return structure with empty section
            original_structure = config.wiki_structure.copy()
            original_structure["Empty Section"] = []

            with patch.object(
                type(config),
                "wiki_structure",
                new_callable=lambda: original_structure,
            ):
                mock_analysis = self.create_mock_analysis()

                structure = generator._generate_wiki_structure(mock_analysis)

                assert "Empty Section" not in structure

    def test_generate_page_content(self) -> None:
        """Test page content generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            generator = WikiGenerator(config, mock_mode=True)

            mock_analysis = self.create_mock_analysis()

            # Mock AI client response
            generator.ai_client.generate_content = Mock(
                return_value="Generated page content"
            )

            content = generator._generate_page_content(
                "Installation", "Getting Started", mock_analysis
            )

            assert content == "Generated page content"
            generator.ai_client.generate_content.assert_called_once()

            # Check that context was properly prepared
            call_args = generator.ai_client.generate_content.call_args
            context = call_args[0][1]  # Second argument is context

            assert context["project_name"] == "Test Project"
            assert context["page_name"] == "Installation"
            assert context["section_name"] == "Getting Started"
            assert context["has_api"] is True
            assert context["has_docker"] is True

    def test_generate_home_page(self) -> None:
        """Test home page generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            generator = WikiGenerator(config, mock_mode=True)

            mock_analysis = self.create_mock_analysis()
            wiki_structure = {
                "Getting Started": ["installation", "configuration"],
                "User Guide": ["features", "usage"],
            }

            # Mock AI client response
            generator.ai_client.generate_content = Mock(
                return_value="Generated home content"
            )

            content = generator._generate_home_page(
                mock_analysis, wiki_structure
            )

            assert content == "Generated home content"
            generator.ai_client.generate_content.assert_called_once()

            # Check that context was properly prepared
            call_args = generator.ai_client.generate_content.call_args
            context = call_args[0][1]  # Second argument is context

            assert context["project_name"] == "Test Project"
            assert (
                context["project_description"] == "A test project for analysis"
            )
            assert "navigation" in context
            assert len(context["navigation"]) == 2

    def test_generate_home_page_validation_fix(self) -> None:
        """Test home page generation with validation fix."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            generator = WikiGenerator(config, mock_mode=True)

            mock_analysis = self.create_mock_analysis()
            generator.content_analyzer.analyze = Mock(
                return_value=mock_analysis
            )

            # Mock validation result with errors for home page
            home_validation_result = Mock()
            home_validation_result.is_valid = False

            page_validation_result = Mock()
            page_validation_result.is_valid = True

            def validate_side_effect(content):
                if (
                    "home" in content.lower()
                    or content == "Generated home content"
                ):
                    return home_validation_result
                return page_validation_result

            generator.validator.validate_content = Mock(
                side_effect=validate_side_effect
            )
            generator.validator.fix_content = Mock(
                side_effect=lambda x: f"Fixed: {x}"
            )

            # Mock AI client
            def generate_side_effect(prompt, context):
                if "home" in prompt.lower():
                    return "Generated home content"
                return "Generated page content"

            generator.ai_client.generate_content = Mock(
                side_effect=generate_side_effect
            )

            wiki_content = generator.generate()

            assert "Home" in wiki_content
            assert wiki_content["Home"] == "Fixed: Generated home content"

    def test_integration_full_generation(self) -> None:
        """Test full integration of wiki generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text(
                "# Test Project\n\nA comprehensive test project."
            )

            # Create some project structure
            (repo_path / "src").mkdir()
            (repo_path / "src" / "main.py").write_text("print('Hello World')")
            (repo_path / "tests").mkdir()
            (repo_path / "tests" / "test_main.py").write_text(
                "def test_main(): pass"
            )

            config = Config(repo_path=repo_path)
            generator = WikiGenerator(config, mock_mode=True)

            wiki_content = generator.generate()

            assert isinstance(wiki_content, dict)
            assert "Home" in wiki_content
            assert len(wiki_content) > 5  # Should generate multiple pages

            # All content should be strings
            for page_name, content in wiki_content.items():
                assert isinstance(content, str)
                assert len(content) > 0
                # Content should contain meaningful text
                assert "This is mock content" in content or "# " in content

    def test_generate_with_custom_structure(self) -> None:
        """Test generation with custom wiki structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            generator = WikiGenerator(config, mock_mode=True)

            # Mock config.wiki_structure property to return custom structure
            # Include necessary sections that the generator expects
            custom_structure = {
                "Custom Section": ["custom_page1", "custom_page2"],
                "API Reference": [],
                "Deployment": [],
                "Development": [],
            }

            with patch.object(
                type(config),
                "wiki_structure",
                new_callable=lambda: custom_structure,
            ):
                mock_analysis = self.create_mock_analysis()
                generator.content_analyzer.analyze = Mock(
                    return_value=mock_analysis
                )

                wiki_content = generator.generate()

                assert "custom_page1" in wiki_content
                assert "custom_page2" in wiki_content
                assert "Home" in wiki_content

    def test_generate_preserves_validation_enabled_content(self) -> None:
        """Test that valid content is preserved during validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path)
            generator = WikiGenerator(config, mock_mode=True)

            mock_analysis = self.create_mock_analysis()
            generator.content_analyzer.analyze = Mock(
                return_value=mock_analysis
            )

            # Mock validation result - all content is valid
            mock_validation_result = Mock()
            mock_validation_result.is_valid = True

            generator.validator.validate_content = Mock(
                return_value=mock_validation_result
            )

            # Mock AI client to return specific content
            generator.ai_client.generate_content = Mock(
                return_value="Original valid content"
            )

            wiki_content = generator.generate()

            # Content should not be modified since it's valid
            for content in wiki_content.values():
                assert content == "Original valid content"
