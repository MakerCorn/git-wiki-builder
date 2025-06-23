"""Tests for content analyzer."""

import tempfile
from pathlib import Path

from git_wiki_builder.config import Config
from git_wiki_builder.content_analyzer import ContentAnalyzer


class TestContentAnalyzer:
    """Test content analyzer functionality."""

    def test_project_name_extraction(self) -> None:
        """Test project name extraction."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text(
                "# Test Project\nA test project"
            )

            # Test with pyproject.toml
            pyproject_content = """
[project]
name = "my-awesome-project"
version = "1.0.0"
"""
            (repo_path / "pyproject.toml").write_text(pyproject_content)

            config = Config(repo_path=repo_path)
            analyzer = ContentAnalyzer(config)

            project_name = analyzer._extract_project_name()
            assert project_name == "my-awesome-project"

    def test_description_extraction(self) -> None:
        """Test description extraction from README."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            readme_content = """# My Project

This is a comprehensive description of my project.

## Features

- Feature 1
- Feature 2
"""
            (repo_path / "README.md").write_text(readme_content)

            config = Config(repo_path=repo_path)
            analyzer = ContentAnalyzer(config)

            description = analyzer._extract_description(readme_content)
            assert description == (
                "This is a comprehensive description of my project."
            )

    def test_docs_analysis(self) -> None:
        """Test documentation analysis."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            # Create docs directory with files
            docs_path = repo_path / "docs"
            docs_path.mkdir()

            (docs_path / "guide.md").write_text(
                "# User Guide\nThis is the user guide."
            )
            (docs_path / "api.md").write_text(
                "# API Reference\nAPI documentation."
            )

            config = Config(repo_path=repo_path)
            analyzer = ContentAnalyzer(config)

            docs_content = analyzer._analyze_docs()

            assert "guide.md" in docs_content
            assert "api.md" in docs_content
            assert "User Guide" in docs_content["guide.md"]

    def test_code_structure_analysis(self) -> None:
        """Test code structure analysis."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            # Create source files
            src_path = repo_path / "src"
            src_path.mkdir()

            (src_path / "main.py").write_text("print('Hello, World!')")
            (src_path / "utils.py").write_text("def helper(): pass")
            (src_path / "app.js").write_text("console.log('Hello');")

            config = Config(repo_path=repo_path)
            analyzer = ContentAnalyzer(config)

            code_structure = analyzer._analyze_code_structure()

            assert "Python" in code_structure
            assert "JavaScript/TypeScript" in code_structure
            assert any("main.py" in file for file in code_structure["Python"])

    def test_dependency_extraction(self) -> None:
        """Test dependency extraction."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            # Create requirements.txt
            requirements_content = """
requests>=2.28.0
click>=8.0.0
pyyaml>=6.0
"""
            (repo_path / "requirements.txt").write_text(requirements_content)

            config = Config(repo_path=repo_path)
            analyzer = ContentAnalyzer(config)

            dependencies = analyzer._extract_dependencies()

            assert "requests" in dependencies
            assert "click" in dependencies
            assert "pyyaml" in dependencies

    def test_feature_extraction(self) -> None:
        """Test key feature extraction."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            readme_content = """# My Project

A great project with many features.

## Features

- Easy to use command line interface
- Supports multiple AI providers
- Automatic markdown validation
- GitHub integration

## Installation

pip install my-project
"""
            (repo_path / "README.md").write_text(readme_content)

            config = Config(repo_path=repo_path)
            analyzer = ContentAnalyzer(config)

            features = analyzer._extract_key_features(readme_content, {})

            assert len(features) > 0
            assert any(
                "command line" in feature.lower() for feature in features
            )
            assert any(
                "ai providers" in feature.lower() for feature in features
            )

    def test_project_characteristics_detection(self) -> None:
        """Test detection of project characteristics."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            # Create Docker files
            (repo_path / "Dockerfile").write_text("FROM python:3.9")
            (repo_path / "docker-compose.yml").write_text("version: '3'")

            # Create test directory
            test_path = repo_path / "tests"
            test_path.mkdir()
            (test_path / "test_main.py").write_text("def test_example(): pass")

            # Create CI/CD files
            github_path = repo_path / ".github" / "workflows"
            github_path.mkdir(parents=True)
            (github_path / "ci.yml").write_text("name: CI")

            config = Config(repo_path=repo_path)
            analyzer = ContentAnalyzer(config)

            assert analyzer._has_docker() is True
            assert analyzer._has_tests() is True
            assert analyzer._has_ci_cd() is True

    def test_full_analysis(self) -> None:
        """Test complete project analysis."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            # Create project structure
            readme_content = """# Test Project

A comprehensive test project for analysis.

## Features

- Feature 1
- Feature 2

## Quick Start

1. Install the package
2. Run the command
3. Enjoy!
"""
            (repo_path / "README.md").write_text(readme_content)

            # Create docs
            docs_path = repo_path / "docs"
            docs_path.mkdir()
            (docs_path / "guide.md").write_text("# Guide\nUser guide content.")

            config = Config(repo_path=repo_path)
            analyzer = ContentAnalyzer(config)

            analysis = analyzer.analyze()

            # Directory name
            assert analysis.project_name == "git-wiki-builder"
            assert "comprehensive test project" in analysis.description.lower()
            assert analysis.readme_content == readme_content
            assert len(analysis.docs_content) > 0
            assert analysis.quick_start_info is not None
            assert len(analysis.key_features) > 0
