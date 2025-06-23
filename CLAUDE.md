# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Git Wiki Builder is a Python CLI tool that generates comprehensive GitHub Wiki documentation using AI. It analyzes project documentation and source code, then creates structured wiki content through AI providers (GitHub Models, OpenAI, or Anthropic).

### Core Architecture

- **CLI Entry Point**: `src/git_wiki_builder/cli.py` - Main command-line interface with Click
- **Configuration**: `src/git_wiki_builder/config.py` - Handles settings, environment variables, and YAML config files  
- **Content Analysis**: `src/git_wiki_builder/content_analyzer.py` - Scans and analyzes project files
- **AI Generation**: `src/git_wiki_builder/ai_client.py` - Interfaces with AI providers for content generation
- **Wiki Generation**: `src/git_wiki_builder/generator.py` - Orchestrates content generation workflow
- **Publishing**: `src/git_wiki_builder/publisher.py` - Publishes generated content to GitHub Wiki
- **Templates**: `src/git_wiki_builder/templates/` - Default configuration and prompt templates
- **Validation**: `src/git_wiki_builder/validator.py` - Markdown validation and fixing

## Development Commands

### Setup and Installation
```bash
# Install in development mode
pip install -e ".[dev]"

# Install with all dependencies
pip install -e .
```

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/git_wiki_builder --cov-report=term-missing --cov-report=html

# Run specific test file
pytest tests/test_config.py

# Run tests with verbose output
pytest -v
```

### Code Quality
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/

# Security scanning
bandit -r src/

# Run all quality checks
black --check src/ tests/ && isort --check-only src/ tests/ && flake8 src/ tests/ && mypy src/ && bandit -r src/
```

### Running the CLI
```bash
# Basic usage
git-wiki-builder

# With custom config
git-wiki-builder --config-file custom-config.yml

# Dry run (no publishing)
git-wiki-builder --dry-run --output-dir ./preview

# Verbose output
git-wiki-builder --verbose

# Custom AI provider
git-wiki-builder --ai-provider openai --ai-model gpt-4
```

## Key Configuration Files

- `pyproject.toml` - Python project configuration, dependencies, and tool settings
- `.git-wiki-builder.yml` - User configuration file (not in repo)
- `src/git_wiki_builder/templates/default-config.yml` - Default configuration template
- `src/git_wiki_builder/templates/default-prompts.yml` - Default AI prompt templates

## Environment Variables

Required for publishing:
- `GITHUB_TOKEN` - GitHub authentication token
- `GITHUB_REPOSITORY` - Repository in format 'owner/repo'

Optional for AI providers:
- `OPENAI_API_KEY` - For OpenAI provider
- `ANTHROPIC_API_KEY` - For Anthropic provider

## Testing Strategy

The codebase uses pytest with coverage requirements (80% minimum). Tests are organized by module:
- `tests/test_config.py` - Configuration loading and validation
- `tests/test_content_analyzer.py` - Content analysis functionality  
- `tests/test_validator.py` - Markdown validation

Mock AI clients are used for testing to avoid API calls during development.