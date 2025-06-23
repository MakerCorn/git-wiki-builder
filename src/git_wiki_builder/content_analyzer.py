"""Content analyzer for project documentation and code."""

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import tomllib  # type: ignore[import-not-found]
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

import yaml

from .config import Config

logger = logging.getLogger(__name__)


@dataclass
class ProjectAnalysis:
    """Results of project content analysis."""

    project_name: str
    description: str
    readme_content: str
    docs_content: Dict[str, str]
    code_structure: Dict[str, List[str]]
    dependencies: List[str]
    key_features: List[str]
    quick_start_info: Optional[str]
    has_api_docs: bool
    has_docker: bool
    has_tests: bool
    has_ci_cd: bool
    files: List[Path]


class ContentAnalyzer:
    """Analyzes project content to understand structure and generate appropriate wiki content."""

    def __init__(self, config: Config) -> None:
        """Initialize content analyzer.

        Args:
            config: Configuration instance
        """
        self.config = config
        self.ignore_patterns = [
            "*.pyc",
            "__pycache__",
            ".git",
            ".gitignore",
            "node_modules",
            ".env",
            "*.log",
            ".DS_Store",
            "*.tmp",
            "*.temp",
        ]

    def analyze(self) -> ProjectAnalysis:
        """Analyze project content.

        Returns:
            ProjectAnalysis with extracted information
        """
        logger.info("Analyzing project content")

        # Get project name
        project_name = self._extract_project_name()

        # Read README
        readme_content = self._read_readme()

        # Extract project description
        description = self._extract_description(readme_content)

        # Analyze documentation
        docs_content = self._analyze_docs()

        # Analyze code structure
        code_structure = self._analyze_code_structure()

        # Extract dependencies
        dependencies = self._extract_dependencies()

        # Extract key features
        key_features = self._extract_key_features(readme_content, docs_content)

        # Extract quick start information
        quick_start_info = self._extract_quick_start(readme_content)

        # Check for specific project characteristics
        has_api_docs = self._has_api_documentation()
        has_docker = self._has_docker()
        has_tests = self._has_tests()
        has_ci_cd = self._has_ci_cd()

        # Get all analyzed files
        files = self._get_analyzed_files()

        return ProjectAnalysis(
            project_name=project_name,
            description=description,
            readme_content=readme_content,
            docs_content=docs_content,
            code_structure=code_structure,
            dependencies=dependencies,
            key_features=key_features,
            quick_start_info=quick_start_info,
            has_api_docs=has_api_docs,
            has_docker=has_docker,
            has_tests=has_tests,
            has_ci_cd=has_ci_cd,
            files=files,
        )

    def _extract_project_name(self) -> str:
        """Extract project name from various sources."""
        # Try pyproject.toml
        pyproject_path = self.config.repo_path / "pyproject.toml"
        if pyproject_path.exists() and tomllib is not None:
            try:
                with open(pyproject_path, "rb") as f:
                    data = tomllib.load(f)
                    if "project" in data and "name" in data["project"]:
                        return str(data["project"]["name"])
            except Exception:
                # Fallback for Python < 3.11 or other errors
                pass

        # Try package.json
        package_json_path = self.config.repo_path / "package.json"
        if package_json_path.exists():
            try:
                import json

                with open(package_json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "name" in data:
                        return str(data["name"])
            except (json.JSONDecodeError, KeyError):
                pass

        # Use directory name as fallback
        return str(self.config.repo_path.name)

    def _read_readme(self) -> str:
        """Read README content."""
        try:
            return self.config.readme_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            logger.warning("No README file found")
            return ""

    def _extract_description(self, readme_content: str) -> str:
        """Extract project description from README."""
        if not readme_content:
            return "No description available"

        lines = readme_content.split("\n")

        # Look for description after title
        for i, line in enumerate(lines):
            if line.startswith("#") and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and not next_line.startswith("#"):
                    return next_line

        # Fallback to first non-empty, non-header line
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("!"):
                return line

        return "No description available"

    def _analyze_docs(self) -> Dict[str, str]:
        """Analyze documentation files."""
        docs_content: Dict[str, str] = {}

        if not self.config.docs_path.exists():
            return docs_content

        for doc_file in self.config.docs_path.rglob("*.md"):
            if self._should_ignore_file(doc_file):
                continue

            try:
                content = doc_file.read_text(encoding="utf-8")
                relative_path = doc_file.relative_to(self.config.docs_path)
                docs_content[str(relative_path)] = content
            except Exception as e:
                logger.warning(f"Could not read {doc_file}: {e}")

        return docs_content

    def _analyze_code_structure(self) -> Dict[str, List[str]]:
        """Analyze code structure."""
        structure = {}

        # Common source directories
        source_dirs = ["src", "lib", "app", ""]

        for source_dir in source_dirs:
            source_path = (
                self.config.repo_path / source_dir if source_dir else self.config.repo_path
            )
            if not source_path.exists():
                continue

            # Python files
            python_files = list(source_path.rglob("*.py"))
            if python_files:
                structure["Python"] = [
                    str(f.relative_to(self.config.repo_path)) for f in python_files[:10]
                ]

            # JavaScript/TypeScript files
            js_files = list(source_path.rglob("*.js")) + list(source_path.rglob("*.ts"))
            if js_files:
                structure["JavaScript/TypeScript"] = [
                    str(f.relative_to(self.config.repo_path)) for f in js_files[:10]
                ]

            # Java files
            java_files = list(source_path.rglob("*.java"))
            if java_files:
                structure["Java"] = [
                    str(f.relative_to(self.config.repo_path)) for f in java_files[:10]
                ]

        return structure

    def _extract_dependencies(self) -> List[str]:
        """Extract project dependencies."""
        dependencies = []

        # Python dependencies
        requirements_files = [
            "requirements.txt",
            "requirements-dev.txt",
            "pyproject.toml",
            "setup.py",
        ]

        for req_file in requirements_files:
            req_path = self.config.repo_path / req_file
            if req_path.exists():
                if req_file == "pyproject.toml":
                    dependencies.extend(self._extract_pyproject_deps(req_path))
                elif req_file.endswith(".txt"):
                    dependencies.extend(self._extract_requirements_deps(req_path))

        # Node.js dependencies
        package_json_path = self.config.repo_path / "package.json"
        if package_json_path.exists():
            dependencies.extend(self._extract_npm_deps(package_json_path))

        return list(set(dependencies))  # Remove duplicates

    def _extract_pyproject_deps(self, pyproject_path: Path) -> List[str]:
        """Extract dependencies from pyproject.toml."""
        try:
            try:
                import tomllib
            except ImportError:
                # Fallback for Python < 3.11
                try:
                    import tomli as tomllib
                except ImportError:
                    return []

            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                deps = data.get("project", {}).get("dependencies", [])
                return [dep.split(">=")[0].split("==")[0].split("~=")[0] for dep in deps]
        except Exception:
            return []

    def _extract_requirements_deps(self, req_path: Path) -> List[str]:
        """Extract dependencies from requirements.txt."""
        try:
            content = req_path.read_text(encoding="utf-8")
            deps = []
            for line in content.split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    dep = line.split(">=")[0].split("==")[0].split("~=")[0]
                    deps.append(dep)
            return deps
        except Exception:
            return []

    def _extract_npm_deps(self, package_json_path: Path) -> List[str]:
        """Extract dependencies from package.json."""
        try:
            import json

            with open(package_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                deps = list(data.get("dependencies", {}).keys())
                deps.extend(list(data.get("devDependencies", {}).keys()))
                return deps
        except Exception:
            return []

    def _extract_key_features(self, readme_content: str, docs_content: Dict[str, str]) -> List[str]:
        """Extract key features from documentation."""
        features = []

        # Look for features in README
        feature_patterns = [
            r"## Features?\n(.*?)(?=\n##|\n#|\Z)",
            r"### Features?\n(.*?)(?=\n###|\n##|\n#|\Z)",
            r"## What.*does\n(.*?)(?=\n##|\n#|\Z)",
        ]

        for pattern in feature_patterns:
            match = re.search(pattern, readme_content, re.DOTALL | re.IGNORECASE)
            if match:
                feature_text = match.group(1)
                # Extract bullet points
                for line in feature_text.split("\n"):
                    line = line.strip()
                    if line.startswith(("-", "*", "+")):
                        features.append(line[1:].strip())

        return features[:10]  # Limit to top 10 features

    def _extract_quick_start(self, readme_content: str) -> Optional[str]:
        """Extract quick start information."""
        quick_start_patterns = [
            r"## Quick Start\n(.*?)(?=\n##|\n#|\Z)",
            r"### Quick Start\n(.*?)(?=\n###|\n##|\n#|\Z)",
            r"## Getting Started\n(.*?)(?=\n##|\n#|\Z)",
            r"## Installation\n(.*?)(?=\n##|\n#|\Z)",
        ]

        for pattern in quick_start_patterns:
            match = re.search(pattern, readme_content, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _has_api_documentation(self) -> bool:
        """Check if project has API documentation."""
        api_indicators = ["api", "swagger", "openapi", "postman", "endpoints"]

        # Check docs directory
        if self.config.docs_path.exists():
            for doc_file in self.config.docs_path.rglob("*.md"):
                content = doc_file.read_text(encoding="utf-8").lower()
                if any(indicator in content for indicator in api_indicators):
                    return True

        # Check for API spec files
        api_files = [
            "openapi.yml",
            "openapi.yaml",
            "swagger.yml",
            "swagger.yaml",
            "api.yml",
            "api.yaml",
        ]

        return any((self.config.repo_path / api_file).exists() for api_file in api_files)

    def _has_docker(self) -> bool:
        """Check if project uses Docker."""
        docker_files = ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"]
        return any((self.config.repo_path / docker_file).exists() for docker_file in docker_files)

    def _has_tests(self) -> bool:
        """Check if project has tests."""
        test_dirs = ["tests", "test", "spec"]
        test_files = ["test_*.py", "*_test.py", "*.test.js", "*.spec.js"]

        # Check for test directories
        for test_dir in test_dirs:
            if (self.config.repo_path / test_dir).exists():
                return True

        # Check for test files
        for pattern in test_files:
            if list(self.config.repo_path.rglob(pattern)):
                return True

        return False

    def _has_ci_cd(self) -> bool:
        """Check if project has CI/CD configuration."""
        ci_paths = [
            ".github/workflows",
            ".gitlab-ci.yml",
            "azure-pipelines.yml",
            "Jenkinsfile",
            ".travis.yml",
            ".circleci/config.yml",
        ]

        return any((self.config.repo_path / ci_path).exists() for ci_path in ci_paths)

    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored."""
        from pathspec import PathSpec
        from pathspec.patterns import GitWildMatchPattern

        spec = PathSpec.from_lines(GitWildMatchPattern, self.ignore_patterns)
        return spec.match_file(str(file_path.relative_to(self.config.repo_path)))

    def _get_analyzed_files(self) -> List[Path]:
        """Get list of all analyzed files."""
        files = []

        # Add README
        try:
            files.append(self.config.readme_path)
        except FileNotFoundError:
            pass

        # Add docs files
        if self.config.docs_path.exists():
            for doc_file in self.config.docs_path.rglob("*"):
                if doc_file.is_file() and not self._should_ignore_file(doc_file):
                    files.append(doc_file)

        return files
