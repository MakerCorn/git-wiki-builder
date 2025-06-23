# Git Wiki Builder Usage Guide

This guide provides comprehensive instructions for using Git Wiki Builder to generate and publish AI-powered GitHub Wiki documentation.

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Command Line Usage](#command-line-usage)
- [GitHub Actions Integration](#github-actions-integration)
- [Custom Prompts](#custom-prompts)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Install Git Wiki Builder

```bash
pip install git-wiki-builder
```

### 2. Set Environment Variables

```bash
export OPENAI_API_KEY="your-openai-api-key"
export GITHUB_TOKEN="your-github-token"
export GITHUB_REPOSITORY="owner/repo-name"
```

### 3. Generate Wiki

```bash
# Navigate to your project directory
cd /path/to/your/project

# Generate and publish wiki
git-wiki-builder
```

## Installation

### From PyPI (Recommended)

```bash
pip install git-wiki-builder
```

### From Source

```bash
git clone https://github.com/example/git-wiki-builder.git
cd git-wiki-builder
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/example/git-wiki-builder.git
cd git-wiki-builder
pip install -e ".[dev]"
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT models | Yes (if using OpenAI) |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude models | Yes (if using Anthropic) |
| `GITHUB_TOKEN` | GitHub personal access token | Yes (for publishing) |
| `GITHUB_REPOSITORY` | Repository in format `owner/repo` | Yes (for publishing) |

### Configuration File

Create `.git-wiki-builder.yml` in your project root:

```yaml
# AI Configuration
ai:
  provider: "openai"  # Options: "openai", "anthropic"
  model: "gpt-4"      # Model to use

# Output Configuration
output:
  directory: "./wiki-output"  # Local output directory

# Validation Configuration
validation:
  skip: false  # Skip markdown validation

# Custom Prompts
prompt:
  file: "./custom-prompts.yml"  # Path to custom prompts
```

## Command Line Usage

### Basic Commands

```bash
# Generate and publish wiki
git-wiki-builder

# Generate without publishing (dry run)
git-wiki-builder --dry-run

# Generate with custom output directory
git-wiki-builder --dry-run --output-dir ./my-wiki

# Use specific AI provider and model
git-wiki-builder --ai-provider anthropic --ai-model claude-3-sonnet-20240229

# Enable verbose logging
git-wiki-builder --verbose
```

### Advanced Options

```bash
# Use custom configuration file
git-wiki-builder --config-file ./my-config.yml

# Use custom prompts
git-wiki-builder --prompt-file ./my-prompts.yml

# Skip markdown validation
git-wiki-builder --skip-validation

# Specify repository path
git-wiki-builder --repo-path /path/to/project
```

### Complete Example

```bash
git-wiki-builder \
  --repo-path ./my-project \
  --config-file ./wiki-config.yml \
  --prompt-file ./custom-prompts.yml \
  --output-dir ./generated-wiki \
  --ai-provider openai \
  --ai-model gpt-4 \
  --verbose \
  --dry-run
```

## GitHub Actions Integration

### Basic Workflow

Create `.github/workflows/wiki.yml`:

```yaml
name: Update Wiki

on:
  push:
    branches: [main]
    paths: ['README.md', 'docs/**']
  workflow_dispatch:

jobs:
  update-wiki:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Git Wiki Builder
        run: pip install git-wiki-builder
      
      - name: Generate and publish wiki
        run: git-wiki-builder
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPOSITORY: ${{ github.repository }}
```

### Advanced Workflow

```yaml
name: Update Wiki

on:
  push:
    branches: [main]
    paths: ['README.md', 'docs/**', 'src/**']
  pull_request:
    branches: [main]
    paths: ['README.md', 'docs/**']
  workflow_dispatch:
    inputs:
      ai_provider:
        description: 'AI Provider'
        required: false
        default: 'openai'
        type: choice
        options:
          - openai
          - anthropic

jobs:
  generate-wiki:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install Git Wiki Builder
        run: pip install git-wiki-builder
      
      - name: Generate wiki (dry run for PRs)
        if: github.event_name == 'pull_request'
        run: git-wiki-builder --dry-run --output-dir ./wiki-preview
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      
      - name: Upload wiki preview
        if: github.event_name == 'pull_request'
        uses: actions/upload-artifact@v4
        with:
          name: wiki-preview
          path: wiki-preview/
      
      - name: Generate and publish wiki
        if: github.event_name != 'pull_request'
        run: git-wiki-builder --ai-provider ${{ inputs.ai_provider || 'openai' }}
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPOSITORY: ${{ github.repository }}
```

## Custom Prompts

### Creating Custom Prompts

Create `custom-prompts.yml`:

```yaml
# Home page prompt
home: |
  Create an engaging home page for {project_name}.
  
  Project: {project_name}
  Description: {project_description}
  Features: {key_features}
  
  Make it welcoming and professional.

# Installation prompt
installation: |
  Create comprehensive installation instructions for {project_name}.
  
  Include:
  1. System requirements
  2. Multiple installation methods
  3. Platform-specific instructions
  4. Verification steps
  5. Troubleshooting tips

# API documentation prompt
api_reference: |
  Document the API for {project_name}.
  
  Code structure: {code_structure}
  
  Include:
  1. API overview
  2. Authentication
  3. Endpoints with examples
  4. Error handling
  5. Rate limiting
```

### Using Custom Prompts

```bash
# Via command line
git-wiki-builder --prompt-file ./custom-prompts.yml

# Via configuration file
# In .git-wiki-builder.yml:
prompt:
  file: "./custom-prompts.yml"
```

## Examples

### Example 1: Python Project

```bash
# Project structure:
# my-python-project/
# ├── README.md
# ├── pyproject.toml
# ├── src/
# │   └── my_package/
# ├── docs/
# │   ├── api.md
# │   └── guide.md
# └── tests/

cd my-python-project
export OPENAI_API_KEY="sk-..."
export GITHUB_TOKEN="ghp_..."
export GITHUB_REPOSITORY="username/my-python-project"

git-wiki-builder --verbose
```

### Example 2: Node.js Project with Custom Config

```yaml
# .git-wiki-builder.yml
ai:
  provider: "anthropic"
  model: "claude-3-sonnet-20240229"

output:
  directory: "./generated-docs"

prompt:
  file: "./prompts/nodejs-prompts.yml"

validation:
  skip: false
```

```bash
cd my-nodejs-project
git-wiki-builder --config-file ./.git-wiki-builder.yml
```

### Example 3: Docker Project

```bash
# For projects with Dockerfile and docker-compose.yml
git-wiki-builder \
  --ai-provider openai \
  --ai-model gpt-4 \
  --output-dir ./docker-wiki \
  --dry-run
```

## Troubleshooting

### Common Issues

#### 1. API Key Not Found

```
Error: OPENAI_API_KEY environment variable is required for OpenAI
```

**Solution:**
```bash
export OPENAI_API_KEY="your-api-key"
# or
export ANTHROPIC_API_KEY="your-api-key"
```

#### 2. GitHub Token Issues

```
Error: Invalid GitHub token
```

**Solution:**
- Ensure token has `repo` and `wiki` permissions
- Check token expiration
- Verify repository access

#### 3. Repository Not Found

```
Error: Repository owner/repo not found or no access
```

**Solution:**
- Check repository name format: `owner/repo`
- Verify repository exists and is accessible
- Ensure token has proper permissions

#### 4. Wiki Disabled

```
Warning: Repository wiki may be disabled
```

**Solution:**
- Enable wiki in repository settings
- Go to Settings → Features → Wikis

#### 5. Markdown Validation Errors

```
Warning: Validation issues for page_name: [errors]
```

**Solution:**
```bash
# Skip validation if needed
git-wiki-builder --skip-validation

# Or fix markdown manually and re-run
```

### Debug Mode

```bash
# Enable verbose logging
git-wiki-builder --verbose

# Generate locally first
git-wiki-builder --dry-run --output-dir ./debug-output --verbose
```

### Getting Help

1. Check the [GitHub Issues](https://github.com/example/git-wiki-builder/issues)
2. Review the [documentation](https://github.com/example/git-wiki-builder/wiki)
3. Use `git-wiki-builder --help` for command reference
4. Enable verbose mode for detailed error information

## Best Practices

### 1. Project Structure

Ensure your project has:
- Clear README.md with project description
- Well-organized docs/ directory
- Proper dependency files (requirements.txt, package.json, etc.)

### 2. Configuration Management

- Use configuration files for consistent settings
- Store sensitive data in environment variables
- Version control your configuration (exclude API keys)

### 3. CI/CD Integration

- Use dry-run for pull requests
- Generate artifacts for review
- Only publish on main branch changes
- Set up proper secrets management

### 4. Content Quality

- Write clear, descriptive README files
- Organize documentation logically
- Use consistent formatting
- Include code examples and usage instructions

### 5. Maintenance

- Regularly update generated content
- Review and refine custom prompts
- Monitor API usage and costs
- Keep dependencies updated
