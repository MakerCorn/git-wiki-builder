# Quick Start Guide

Get your GitHub Wiki up and running in under 5 minutes with Git Wiki Builder!

## 🚀 Super Quick Setup (Recommended)

### Option 1: One-Command Setup

```bash
# Run this in your repository root
curl -sSL https://raw.githubusercontent.com/example/git-wiki-builder/main/setup-wiki.sh | bash
```

This script will:
- ✅ Create the GitHub Actions workflow
- ✅ Set up default configuration
- ✅ Update your .gitignore
- ✅ Show you next steps

### Option 2: Manual Setup

1. **Create the workflow file**:
   ```bash
   mkdir -p .github/workflows
   ```

2. **Add `.github/workflows/wiki.yml`**:
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

3. **Enable Wiki in GitHub**:
   - Go to your repository Settings
   - Scroll to Features section
   - Check ✅ Wikis

4. **Commit and push**:
   ```bash
   git add .github/workflows/wiki.yml
   git commit -m "Add automated wiki generation"
   git push
   ```

## 🎉 That's It!

Your wiki will be automatically generated at:
`https://github.com/yourusername/yourrepo/wiki`

## 🔧 Default Configuration

Git Wiki Builder works with **zero configuration** using these defaults:

- **AI Provider**: GitHub Models (free for public repos)
- **Model**: gpt-4o-mini (fast and efficient)
- **Triggers**: Changes to README.md, docs/, src/, or any .md files
- **Structure**: Standard wiki sections (Home, Getting Started, User Guide, etc.)

## 📝 What Gets Generated

Based on your project, Git Wiki Builder creates:

### Always Generated
- **Home**: Project overview and navigation
- **Getting Started**: Installation and setup
- **User Guide**: Features and usage

### Conditionally Generated (based on project analysis)
- **API Reference**: If APIs detected
- **Development**: If tests/CI found
- **Deployment**: If Docker/deployment configs found
- **FAQ**: Common questions
- **Changelog**: Release information

## 🛠️ Customization (Optional)

### Custom Configuration

Create `.git-wiki-builder.yml` in your repo root:

```yaml
# Use different AI provider
ai:
  provider: "openai"  # Requires OPENAI_API_KEY
  model: "gpt-4"

# Custom wiki structure
wiki_structure:
  "Home": ["overview", "features"]
  "Documentation": ["user_guide", "api_docs"]
  "Support": ["faq", "troubleshooting"]
```

### Custom Prompts

Create `custom-prompts.yml`:

```yaml
home: |
  Create an engaging home page for {project_name}.
  Focus on: {key_features}
  Make it beginner-friendly.

installation: |
  Write clear installation instructions for {project_name}.
  Include troubleshooting tips.
```

Use with:
```yaml
# In .git-wiki-builder.yml
prompt:
  file: "./custom-prompts.yml"
```

## 🧪 Testing Locally

Before pushing, test your wiki generation:

```bash
# Install locally
pip install git-wiki-builder

# Generate preview (no publishing)
git-wiki-builder --dry-run --output-dir ./wiki-preview

# View generated files
ls wiki-preview/
```

## 🔍 Troubleshooting

### Wiki Not Generating?

1. **Check if Wiki is enabled**:
   - Repository Settings → Features → Wikis ✅

2. **Check workflow logs**:
   - Go to Actions tab in your repository
   - Click on latest "Generate Wiki Documentation" run

3. **Test locally**:
   ```bash
   git-wiki-builder --dry-run --verbose
   ```

### Common Issues

**"No README file found"**
- Ensure you have README.md in your repository root

**"Repository not found"**
- Check repository permissions
- Ensure GITHUB_TOKEN has proper access

**"Wiki generation failed"**
- Check if your repository is public (required for free GitHub Models)
- Or configure alternative AI provider with API key

## 📚 Next Steps

- **Customize**: Add custom prompts or configuration
- **Enhance**: Improve your README and docs for better wiki content
- **Automate**: Set up additional triggers or schedules
- **Share**: Your professional wiki attracts more contributors!

## 🆘 Need Help?

- 📖 [Full Documentation](https://github.com/example/git-wiki-builder/wiki)
- 🐛 [Report Issues](https://github.com/example/git-wiki-builder/issues)
- 💬 [GitHub Discussions](https://github.com/example/git-wiki-builder/discussions)

---

**🎯 Pro Tip**: The better your README and documentation, the better your generated wiki will be!
