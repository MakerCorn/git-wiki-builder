# Contributing to Git Wiki Builder

We welcome contributions to Git Wiki Builder! This document provides guidelines for contributing to the project.

## Getting Started

### Development Environment Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/your-username/git-wiki-builder.git
   cd git-wiki-builder
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

### Running Tests

Run the full test suite:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=src/git_wiki_builder --cov-report=html
```

Run specific test files:
```bash
pytest tests/test_config.py
```

### Code Quality

We use several tools to maintain code quality:

1. **Format code with Black:**
   ```bash
   black src tests
   ```

2. **Sort imports with isort:**
   ```bash
   isort src tests
   ```

3. **Lint code with flake8:**
   ```bash
   flake8 src tests
   ```

4. **Type check with mypy:**
   ```bash
   mypy src
   ```

5. **Security check with bandit:**
   ```bash
   bandit -r src
   ```

6. **Run all checks:**
   ```bash
   # Format and lint
   black src tests
   isort src tests
   flake8 src tests
   mypy src
   bandit -r src
   
   # Run tests
   pytest
   ```

## Contributing Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep line length to 100 characters maximum
- Use meaningful variable and function names

### Commit Messages

Follow conventional commit format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for test additions or modifications
- `refactor:` for code refactoring
- `style:` for formatting changes
- `chore:` for maintenance tasks

Example:
```
feat: add support for custom wiki structure configuration

- Allow users to define custom wiki sections in config file
- Update prompt manager to handle custom sections
- Add validation for custom structure format
```

### Pull Request Process

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes and commit:**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

3. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a pull request:**
   - Use a clear, descriptive title
   - Provide a detailed description of changes
   - Reference any related issues
   - Include screenshots if applicable

5. **Ensure all checks pass:**
   - All tests must pass
   - Code coverage should not decrease
   - All linting checks must pass
   - Documentation must be updated if needed

### Testing Guidelines

- Write tests for all new functionality
- Maintain or improve code coverage
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies (AI APIs, GitHub API)

Example test structure:
```python
class TestFeatureName:
    """Test feature functionality."""
    
    def test_successful_case(self) -> None:
        """Test successful execution."""
        # Arrange
        # Act
        # Assert
    
    def test_error_case(self) -> None:
        """Test error handling."""
        # Arrange
        # Act & Assert
        with pytest.raises(ExpectedError):
            # Code that should raise error
```

### Documentation

- Update README.md for user-facing changes
- Update docstrings for API changes
- Add examples for new features
- Update CHANGELOG.md for all changes

## Types of Contributions

### Bug Reports

When reporting bugs, please include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Error messages and stack traces

### Feature Requests

For feature requests, please provide:
- Clear description of the feature
- Use case and motivation
- Proposed implementation approach
- Examples of how it would be used

### Code Contributions

We welcome contributions for:
- Bug fixes
- New features
- Performance improvements
- Documentation improvements
- Test coverage improvements

### Areas for Contribution

- **AI Provider Support**: Add support for new AI providers
- **Content Analysis**: Improve project analysis capabilities
- **Prompt Templates**: Create better default prompts
- **Validation Rules**: Add more markdown validation rules
- **Output Formats**: Support for different output formats
- **Integration**: Add support for other platforms (GitLab, Bitbucket)
- **Performance**: Optimize content generation and processing
- **Documentation**: Improve user guides and examples

## Development Tips

### Working with AI APIs

- Use mock responses for testing to avoid API costs
- Test with different AI providers and models
- Handle API rate limits and errors gracefully
- Keep prompts modular and testable

### Testing Locally

1. **Create test repositories:**
   ```bash
   mkdir test-repo
   cd test-repo
   git init
   echo "# Test Project" > README.md
   mkdir docs
   echo "# Documentation" > docs/guide.md
   ```

2. **Test with dry run:**
   ```bash
   git-wiki-builder --dry-run --output-dir ./output --repo-path ./test-repo
   ```

3. **Test different configurations:**
   ```bash
   git-wiki-builder --ai-provider anthropic --ai-model claude-3-sonnet-20240229
   ```

### Debugging

- Use `--verbose` flag for detailed logging
- Check generated content in output directory
- Validate markdown with external tools
- Test with different project structures

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with new version
3. Create release branch
4. Run full test suite
5. Create pull request for release
6. Tag release after merge
7. Publish to PyPI

## Getting Help

- Check existing issues and discussions
- Ask questions in GitHub Discussions
- Join our community chat (if available)
- Read the documentation thoroughly

## Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms.

Thank you for contributing to Git Wiki Builder!
