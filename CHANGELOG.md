# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-06-23

### Added

- Initial release of Git Wiki Builder
- **GitHub Models Integration**: Default AI provider using GitHub's hosted models (free for public repositories)
- AI-powered wiki content generation with support for multiple providers:
  - GitHub Models (default, free for public repos)
  - OpenAI GPT models
  - Anthropic Claude models
- Intelligent project analysis and content extraction
- Customizable prompt system for tailored content generation
- Built-in markdown validation and auto-fixing
- GitHub Wiki publishing with git workflow integration
- Command-line interface with comprehensive options
- YAML-based configuration system
- Structured wiki organization with standard sections
- **One-command setup script** for instant GitHub Actions integration
- Comprehensive test suite and documentation

### Key Features

- **Zero Configuration**: Works out-of-the-box with sensible defaults
- **Cost-Effective**: Uses free GitHub Models for public repositories
- **Automated Workflows**: Ready-to-use GitHub Actions workflow
- **Content Generation**: Generate high-quality wiki documentation from project files
- **Project Analysis**: Automatically analyze README, docs, and code structure
- **Markdown Validation**: Validate and fix markdown content according to best practices
- **GitHub Integration**: Seamless publishing to GitHub Wiki repositories
- **Flexible Configuration**: YAML configuration with environment variable support
- **Custom Prompts**: Load and use custom prompts for content generation
- **Multiple AI Models**: Support for various AI providers and models
- **CI/CD Ready**: Designed for use in automated workflows
- **Cross-Platform**: Works on Windows, macOS, and Linux

### Default Configuration

- **AI Provider**: GitHub Models (github)
- **Default Model**: gpt-4o-mini (fast, efficient, free for public repos)
- **Triggers**: README.md, docs/, src/, and markdown file changes
- **Authentication**: Uses GITHUB_TOKEN (automatically provided in Actions)
- **Wiki Structure**: Professional, standardized sections

### Supported Project Types

- Python projects (pyproject.toml, requirements.txt, setup.py)
- Node.js projects (package.json)
- Docker projects (Dockerfile, docker-compose.yml)
- Projects with CI/CD configurations
- Any project with README and documentation files

### Wiki Structure

- Home page with project overview and navigation
- Getting Started section with installation and configuration
- User Guide with features and usage examples
- API Reference documentation (when applicable)
- Development guidelines and contribution information
- Deployment guides and best practices
- FAQ and troubleshooting sections
- Changelog and migration guides

### Setup Options

1. **One-Command Setup**:
   ```bash
   curl -sSL https://raw.githubusercontent.com/example/git-wiki-builder/main/setup-wiki.sh | bash
   ```

2. **Manual GitHub Actions Setup**:
   - Create `.github/workflows/wiki.yml`
   - Enable Wiki in repository settings
   - Commit and push

3. **Local Installation**:
   ```bash
   pip install git-wiki-builder
   git-wiki-builder --dry-run
   ```

### Technical Details

- Python 3.8+ support
- Rich CLI interface with progress indicators
- Comprehensive error handling and logging
- Git integration for wiki repository management
- Markdown linting and validation
- File pattern matching and content analysis
- Template-based prompt system
- Configurable wiki structure
- Mock mode for testing without API calls

### Dependencies

- click: Command-line interface framework
- requests: HTTP library for GitHub API
- pyyaml: YAML configuration parsing
- jinja2: Template engine for prompts
- gitpython: Git repository operations
- openai: OpenAI API client (for GitHub Models and OpenAI)
- anthropic: Anthropic API client
- python-dotenv: Environment variable loading
- rich: Rich text and beautiful formatting
- pathspec: File pattern matching

### Development Tools

- pytest: Testing framework
- black: Code formatting
- isort: Import sorting
- flake8: Code linting
- mypy: Type checking
- bandit: Security analysis
- pre-commit: Git hooks

### Breaking Changes

None (initial release)

### Migration Guide

None (initial release)

### Known Issues

- GitHub Models require public repositories for free usage
- Private repositories need alternative AI provider with API key
- Large repositories may hit content analysis limits (configurable)
