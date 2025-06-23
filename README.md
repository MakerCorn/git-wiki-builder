# Git Wiki Builder

**AI-powered GitHub Wiki generator that automatically creates comprehensive documentation for your projects.**

[![PyPI version](https://badge.fury.io/py/git-wiki-builder.svg)](https://badge.fury.io/py/git-wiki-builder)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🌟 Overview

Git Wiki Builder transforms your project's README, documentation files, and code structure into a comprehensive, well-organized GitHub Wiki using AI. It analyzes your project intelligently and generates professional documentation that follows industry best practices.

### ✨ Key Benefits

- **🤖 AI-Powered**: Uses GitHub's hosted AI models (free for public repos) to generate high-quality content
- **🚀 Zero Configuration**: Works out-of-the-box with sensible defaults
- **⚡ Automated**: Integrates seamlessly with GitHub Actions for continuous documentation
- **📚 Comprehensive**: Creates complete wiki structure with multiple sections
- **🎯 Intelligent**: Analyzes your project to detect APIs, Docker, tests, and more
- **✅ Quality Assured**: Built-in markdown validation and auto-fixing
- **🔧 Customizable**: Flexible prompts and configuration options
- **💰 Cost-Effective**: Uses free GitHub Models for public repositories

### 🏗️ What It Creates

Git Wiki Builder automatically generates a complete wiki structure:

- **🏠 Home**: Project overview and navigation
- **🚀 Getting Started**: Installation, configuration, first steps  
- **📖 User Guide**: Features, usage examples, tutorials
- **🔌 API Reference**: Endpoint documentation (if APIs detected)
- **👩‍💻 Development**: Contributing guidelines, setup, testing
- **🚢 Deployment**: Deployment guides and best practices
- **❓ FAQ**: Common questions and troubleshooting
- **📝 Changelog**: Release notes and migration guides

## 🚀 Quick Start

### 1. Install Git Wiki Builder

```bash
pip install git-wiki-builder
```

### 2. One-Command Setup

Run this in your repository root to set up everything automatically:

```bash
curl -sSL https://raw.githubusercontent.com/example/git-wiki-builder/main/setup-wiki.sh | bash
```

Or manually create the workflow file:

```bash
mkdir -p .github/workflows
```

Create `.github/workflows/wiki.yml`:

```yaml
name: Generate Wiki Documentation

on:
  push:
    branches: [main, master]
    paths: ['README.md', 'docs/**', 'src/**', '*.md']
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  generate-wiki:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install git-wiki-builder
      - run: git-wiki-builder
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPOSITORY: ${{ github.repository }}
```

### 3. Enable Wiki & Push

1. **Enable Wiki in your repository**:
   - Go to Settings → Features → Wikis ✓

2. **Commit and push**:
   ```bash
   git add .github/workflows/wiki.yml
   git commit -m "Add automated wiki generation"
   git push
   ```

3. **Your wiki is ready!** 🎉
   - Visit `https://github.com/yourusername/yourrepo/wiki`
   - Wiki updates automatically when you modify README.md, docs/, or source code

## 🎯 Why Git Wiki Builder?

### Traditional Documentation Problems
- ❌ Manual wiki creation is time-consuming
- ❌ Documentation gets outdated quickly  
- ❌ Inconsistent structure across projects
- ❌ Requires dedicated technical writers
- ❌ Hard to maintain comprehensive coverage

### Git Wiki Builder Solutions
- ✅ **Automated Generation**: AI creates content from your existing files
- ✅ **Always Up-to-Date**: Regenerates on every code change
- ✅ **Consistent Structure**: Professional, standardized wiki layout
- ✅ **Developer-Friendly**: Works with your existing workflow
- ✅ **Comprehensive Coverage**: Analyzes entire project structure

### Perfect For

- 🔧 **Open Source Projects**: Professional documentation attracts contributors
- 🏢 **Enterprise Teams**: Consistent documentation across all repositories  
- 📚 **API Projects**: Automatic API documentation generation
- 🚀 **Startups**: Professional appearance without dedicated resources
- 👨‍🎓 **Learning Projects**: Well-documented code for portfolios

## 🛠️ Advanced Usage

### Local Testing

```bash
# Test locally before publishing
git-wiki-builder --dry-run --output-dir ./wiki-preview

# Use verbose logging for debugging
git-wiki-builder --verbose --dry-run
```

### Custom Configuration

Create `.git-wiki-builder.yml`:

```yaml
# AI Configuration
ai:
  provider: "github"      # Free for public repos
  model: "gpt-4o-mini"    # Fast and efficient

# Custom Wiki Structure
wiki_structure:
  "Home": ["overview", "quick_start"]
  "Documentation": ["user_guide", "api_docs"]
  "Development": ["contributing", "setup"]

# Validation
validation:
  skip: false  # Enable markdown validation
```

### Alternative AI Providers

```yaml
# Use OpenAI (requires API key)
ai:
  provider: "openai"
  model: "gpt-4"

# Use Anthropic Claude (requires API key)  
ai:
  provider: "anthropic"
  model: "claude-3-sonnet-20240229"
```

### Custom Prompts

Create `custom-prompts.yml`:

```yaml
home: |
  Create a welcoming home page for {project_name}.
  Highlight: {key_features}
  Make it beginner-friendly and engaging.

api_reference: |
  Document the API for {project_name}.
  Include authentication, endpoints, and examples.
  Code structure: {code_structure}
```

Use with: `git-wiki-builder --prompt-file custom-prompts.yml`

## 📊 Supported Project Types

Git Wiki Builder works with **any project** but provides enhanced support for:

| Technology | Auto-Detected Features |
|------------|------------------------|
| **Python** | Dependencies, virtual envs, testing frameworks |
| **Node.js** | Package.json, npm scripts, testing |
| **Docker** | Container deployment, compose files |
| **APIs** | OpenAPI specs, endpoint documentation |
| **CI/CD** | GitHub Actions, deployment pipelines |
| **Databases** | Schema documentation, migrations |

## 🔧 Command Line Options

```bash
git-wiki-builder [OPTIONS]

Options:
  -r, --repo-path DIRECTORY    Repository path (default: current directory)
  -c, --config-file FILE       Custom configuration file
  -p, --prompt-file FILE       Custom prompt templates
  -o, --output-dir DIRECTORY   Local output directory
  --ai-provider [github|openai|anthropic]  AI provider (default: github)
  --ai-model TEXT              Specific model to use
  --dry-run                    Generate locally without publishing
  --verbose                    Enable detailed logging
  --skip-validation            Skip markdown validation
  --help                       Show help message
```

## 🌍 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_TOKEN` | GitHub token (auto-provided in Actions) | Yes |
| `GITHUB_REPOSITORY` | Repository name (auto-provided in Actions) | Yes |
| `OPENAI_API_KEY` | OpenAI API key | Only for OpenAI provider |
| `ANTHROPIC_API_KEY` | Anthropic API key | Only for Anthropic provider |

## 🔍 How It Works

1. **📖 Analysis**: Scans README, docs/, and source code
2. **🧠 AI Generation**: Uses AI to create comprehensive content
3. **✅ Validation**: Validates and fixes markdown formatting
4. **📤 Publishing**: Commits to GitHub Wiki repository
5. **🔄 Automation**: Repeats on every relevant change

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/example/git-wiki-builder.git
cd git-wiki-builder
pip install -e ".[dev]"
pytest
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support & Resources

- 📚 [Documentation Wiki](https://github.com/example/git-wiki-builder/wiki)
- 🐛 [Report Issues](https://github.com/example/git-wiki-builder/issues)
- 💬 [GitHub Discussions](https://github.com/example/git-wiki-builder/discussions)
- 📧 [Email Support](mailto:support@example.com)

## 🌟 Examples

See Git Wiki Builder in action:
- [Example Python Project](https://github.com/example/python-project/wiki)
- [Example Node.js API](https://github.com/example/nodejs-api/wiki)  
- [Example Docker App](https://github.com/example/docker-app/wiki)

---

**⭐ Star this repository if Git Wiki Builder helps your project!**

Made with ❤️ for the developer community
