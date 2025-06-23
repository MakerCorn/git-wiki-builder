#!/bin/bash

# Git Wiki Builder Setup Script
# This script sets up Git Wiki Builder for your GitHub repository

set -e

echo "🚀 Setting up Git Wiki Builder for your repository..."

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: This script must be run from within a Git repository"
    exit 1
fi

# Create .github/workflows directory if it doesn't exist
mkdir -p .github/workflows

# Download the default workflow
echo "📄 Creating GitHub Actions workflow..."
cat > .github/workflows/wiki.yml << 'EOF'
name: Generate Wiki Documentation

on:
  push:
    branches: [main, master]
    paths: 
      - 'README.md'
      - 'docs/**'
      - 'src/**'
      - 'lib/**'
      - 'app/**'
      - '*.md'
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  generate-wiki:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install Git Wiki Builder
        run: pip install git-wiki-builder

      - name: Generate and publish wiki
        run: git-wiki-builder
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPOSITORY: ${{ github.repository }}

      - name: Generate wiki preview (for debugging)
        if: failure()
        run: git-wiki-builder --dry-run --output-dir ./wiki-debug --verbose
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Upload debug artifacts
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: wiki-debug
          path: wiki-debug/
          retention-days: 7
EOF

# Create default configuration file
echo "⚙️  Creating default configuration..."
cat > .git-wiki-builder.yml << 'EOF'
# Git Wiki Builder Configuration
# Uses GitHub Models (free for public repositories)

ai:
  provider: "github"
  model: "gpt-4o-mini"

validation:
  skip: false

wiki_structure:
  "Home": ["overview", "quick_start"]
  "Getting Started": ["installation", "configuration", "first_steps"]
  "User Guide": ["features", "usage", "examples"]
  "API Reference": ["api_overview", "endpoints", "authentication"]
  "Development": ["contributing", "development_setup", "testing"]
  "Deployment": ["deployment_guide", "environment_setup", "troubleshooting"]
  "FAQ": ["common_questions", "known_issues"]
  "Changelog": ["release_notes", "migration_guide"]
EOF

# Add to .gitignore if it exists
if [ -f .gitignore ]; then
    echo "📝 Updating .gitignore..."
    if ! grep -q "wiki-output" .gitignore; then
        echo "" >> .gitignore
        echo "# Git Wiki Builder" >> .gitignore
        echo "wiki-output/" >> .gitignore
        echo "wiki-debug/" >> .gitignore
    fi
fi

echo ""
echo "✅ Git Wiki Builder setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Commit and push the new workflow file:"
echo "   git add .github/workflows/wiki.yml .git-wiki-builder.yml"
echo "   git commit -m 'Add Git Wiki Builder workflow'"
echo "   git push"
echo ""
echo "2. Enable Wiki in your GitHub repository:"
echo "   - Go to Settings → Features → Wikis ✓"
echo ""
echo "3. The wiki will be automatically generated when you push changes to:"
echo "   - README.md"
echo "   - docs/ folder"
echo "   - source code files"
echo ""
echo "🔗 Your wiki will be available at:"
echo "   https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^.]*\).*/\1/')/wiki"
echo ""
echo "For more information, visit: https://github.com/example/git-wiki-builder"
