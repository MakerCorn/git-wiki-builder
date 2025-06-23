# Git Wiki Builder - Project Summary

## 🎯 Overview

**Git Wiki Builder** is a production-ready command-line application that automatically generates comprehensive GitHub Wiki documentation using AI. It's designed to work seamlessly with GitHub Actions and uses GitHub's hosted AI models by default, making it **completely free for public repositories**.

## 🌟 Key Highlights

### ✨ **Zero Configuration Required**
- Works out-of-the-box with sensible defaults
- One-command setup script for instant integration
- Automatic project analysis and content generation

### 💰 **Cost-Effective**
- **FREE** for public repositories using GitHub Models
- No API keys required for basic usage
- Optional premium AI providers for advanced needs

### 🚀 **Production Ready**
- Comprehensive error handling and logging
- Built-in markdown validation and fixing
- Robust GitHub integration with proper git workflows
- Cross-platform compatibility (Windows, macOS, Linux)

### 🤖 **AI-Powered Intelligence**
- Analyzes README, documentation, and code structure
- Detects project characteristics (APIs, Docker, tests, CI/CD)
- Generates contextually relevant content
- Supports custom prompts for tailored output

## 🏗️ **Architecture**

### **Core Components**
```
git-wiki-builder/
├── CLI Interface (cli.py)           # Rich command-line interface
├── Configuration (config.py)        # YAML + environment variables
├── Content Generator (generator.py) # Orchestrates wiki generation
├── AI Client (ai_client.py)        # Multi-provider AI integration
├── Content Analyzer (content_analyzer.py) # Project analysis
├── Prompt Manager (prompt_manager.py)     # Template system
├── Markdown Validator (validator.py)      # Quality assurance
├── GitHub Publisher (publisher.py)        # Wiki publishing
└── Utilities (utils.py)            # Helper functions
```

### **AI Provider Support**
1. **GitHub Models** (default, free for public repos)
   - Model: gpt-4o-mini
   - Authentication: GITHUB_TOKEN
   - Cost: Free for public repositories

2. **OpenAI** (premium option)
   - Models: gpt-4, gpt-3.5-turbo, etc.
   - Authentication: OPENAI_API_KEY
   - Cost: Pay-per-use

3. **Anthropic Claude** (premium option)
   - Models: claude-3-sonnet, claude-3-haiku
   - Authentication: ANTHROPIC_API_KEY
   - Cost: Pay-per-use

## 🚀 **Quick Start**

### **Super Quick Setup (< 2 minutes)**
```bash
# 1. Run setup script in your repository
curl -sSL https://raw.githubusercontent.com/example/git-wiki-builder/main/setup-wiki.sh | bash

# 2. Enable Wiki in GitHub repository settings
# 3. Commit and push
git add .github/workflows/wiki.yml .git-wiki-builder.yml
git commit -m "Add automated wiki generation"
git push

# 4. Your wiki is live at: https://github.com/username/repo/wiki
```

### **Manual Setup**
```yaml
# .github/workflows/wiki.yml
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

## 📊 **Generated Wiki Structure**

### **Standard Sections** (automatically generated based on project analysis)
- **🏠 Home**: Project overview, navigation, key features
- **🚀 Getting Started**: Installation, configuration, first steps
- **📖 User Guide**: Features, usage examples, tutorials
- **🔌 API Reference**: Endpoints, authentication (if APIs detected)
- **👩‍💻 Development**: Contributing, setup, testing (if tests found)
- **🚢 Deployment**: Guides, Docker (if Docker files detected)
- **❓ FAQ**: Common questions, troubleshooting
- **📝 Changelog**: Release notes, migration guides

### **Intelligent Detection**
The tool automatically detects and documents:
- **Python projects**: Dependencies, virtual environments, testing
- **Node.js projects**: Package.json, npm scripts, testing
- **Docker projects**: Container deployment, compose files
- **API projects**: OpenAPI specs, endpoint documentation
- **CI/CD projects**: GitHub Actions, deployment pipelines
- **Database projects**: Schema documentation, migrations

## 🛠️ **Advanced Features**

### **Customization Options**
```yaml
# .git-wiki-builder.yml
ai:
  provider: "github"  # or "openai", "anthropic"
  model: "gpt-4o-mini"

wiki_structure:
  "Home": ["overview", "quick_start"]
  "Documentation": ["user_guide", "api_docs"]
  "Support": ["faq", "troubleshooting"]

prompt:
  file: "./custom-prompts.yml"

validation:
  skip: false  # Enable markdown validation
```

### **Custom Prompts**
```yaml
# custom-prompts.yml
home: |
  Create an engaging home page for {project_name}.
  Highlight: {key_features}
  Make it beginner-friendly and professional.

api_reference: |
  Document the API for {project_name}.
  Include authentication, endpoints, and examples.
  Code structure: {code_structure}
```

### **Local Testing**
```bash
# Test locally before publishing
git-wiki-builder --dry-run --output-dir ./wiki-preview --verbose

# Use different AI provider
git-wiki-builder --ai-provider openai --ai-model gpt-4
```

## 🧪 **Quality Assurance**

### **Built-in Validation**
- **Markdown Linting**: Follows markdownlint standards
- **Auto-fixing**: Corrects common formatting issues
- **Link Validation**: Ensures proper link syntax
- **Heading Hierarchy**: Maintains proper document structure
- **Code Block Languages**: Automatically detects and adds language tags

### **Testing & CI/CD**
- Comprehensive test suite with pytest
- Code formatting with Black
- Import sorting with isort
- Linting with flake8
- Type checking with mypy
- Security scanning with bandit
- Pre-commit hooks for quality assurance

## 📦 **Distribution & Installation**

### **PyPI Package**
```bash
pip install git-wiki-builder
```

### **Development Installation**
```bash
git clone https://github.com/example/git-wiki-builder.git
cd git-wiki-builder
pip install -e ".[dev]"
```

### **GitHub Actions Integration**
- Ready-to-use workflow templates
- Automatic dependency caching
- Error handling and debugging
- Artifact generation for troubleshooting

## 🎯 **Use Cases & Benefits**

### **Perfect For**
- **🔧 Open Source Projects**: Professional documentation attracts contributors
- **🏢 Enterprise Teams**: Consistent documentation across repositories
- **📚 API Projects**: Automatic API documentation generation
- **🚀 Startups**: Professional appearance without dedicated resources
- **👨‍🎓 Learning Projects**: Well-documented code for portfolios

### **Key Benefits**
- **⏰ Time Saving**: Eliminates manual wiki creation and maintenance
- **📈 Consistency**: Standardized documentation structure across projects
- **🔄 Always Current**: Automatically updates with code changes
- **💡 Intelligence**: AI understands project context and generates relevant content
- **🎨 Professional**: High-quality, well-formatted documentation
- **🔧 Flexible**: Customizable prompts and structure

## 🌍 **Environment Variables**

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GITHUB_TOKEN` | GitHub authentication | Yes | Auto-provided in Actions |
| `GITHUB_REPOSITORY` | Repository name (owner/repo) | Yes | Auto-provided in Actions |
| `OPENAI_API_KEY` | OpenAI API key | Only for OpenAI | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | Only for Anthropic | - |

## 📈 **Performance & Scalability**

### **Optimizations**
- **Efficient Analysis**: Configurable file limits and content length
- **Caching**: Dependency caching in GitHub Actions
- **Parallel Processing**: Concurrent content generation
- **Smart Filtering**: Ignores irrelevant files and directories

### **Limits & Considerations**
- **GitHub Models**: Free for public repositories
- **Content Length**: Configurable maximum content analysis
- **File Count**: Configurable maximum files per category
- **Rate Limits**: Respects AI provider rate limits

## 🆘 **Support & Resources**

### **Documentation**
- 📚 [Full Documentation](https://github.com/example/git-wiki-builder/wiki)
- 🚀 [Quick Start Guide](docs/quick-start.md)
- 📖 [Usage Guide](docs/usage-guide.md)
- 🤝 [Contributing Guide](CONTRIBUTING.md)

### **Community**
- 🐛 [Report Issues](https://github.com/example/git-wiki-builder/issues)
- 💬 [GitHub Discussions](https://github.com/example/git-wiki-builder/discussions)
- 📧 [Email Support](mailto:support@example.com)

### **Examples**
- [Example Python Project](https://github.com/example/python-project/wiki)
- [Example Node.js API](https://github.com/example/nodejs-api/wiki)
- [Example Docker App](https://github.com/example/docker-app/wiki)

## 🔮 **Future Roadmap**

### **Planned Features**
- Additional AI provider integrations
- Multi-language documentation support
- Advanced customization options
- Integration with other documentation platforms
- Enhanced project analysis capabilities

### **Community Contributions**
- Custom prompt templates library
- Project-specific configurations
- Additional validation rules
- Performance optimizations
- Bug fixes and improvements

---

**Git Wiki Builder** represents a complete solution for automated documentation generation, combining the power of AI with the convenience of GitHub's ecosystem to create professional, comprehensive wikis with minimal effort.

**⭐ Star the repository if Git Wiki Builder helps your project!**
