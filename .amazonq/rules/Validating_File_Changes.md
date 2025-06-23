# Validation Rules

## Testing Code

- When running tests, use the test environment settings unless different from the deployment pipeline

## When making code changes for Python Code or Python Projects

- Run black to format all Python files
- Run isort to format import statements
- Run flake8 to check for linting issues
- Run mypy on Python code to check for coding errors
- Run bandit to check for security issues

## Markdown Linting Rules

### Core Principles

- Maintain consistent formatting across all markdown files
- Ensure accessibility through proper heading hierarchy  
- Follow markdownlint standards for professional documentation
- Automatically fix common violations when possible

### Critical Rules to Always Enforce for Documentation and Markdown

#### Document Structure

- **MD001**: Heading levels increment by one only (`# H1` → `## H2` → `### H3`)
- **MD041**: Start documents with top-level heading (`# Title`)
- **MD025**: Only one H1 per document
- **MD022**: Surround headings with blank lines

#### Heading Format

- **MD003**: Use consistent heading style (prefer ATX: `# Heading`)
- **MD018**: Space after hash (`# Heading` not `#Heading`)
- **MD019**: Single space after hash (`# Heading` not `#  Heading`)
- **MD023**: Headings start at line beginning (no indentation)

#### Lists

- **MD004**: Consistent list markers (use `-` for unordered lists)
- **MD005**: Same indentation for same-level items
- **MD007**: 2-space indentation for nested items
- **MD032**: Blank lines around lists

#### Code Blocks

- **MD040**: Always specify language (```javascript not ```)
- **MD031**: Blank lines around fenced code blocks
- **MD046**: Use fenced blocks (```) over indented code

#### Links and Images

- **MD034**: No bare URLs (use `[text](url)` or `<url>`)
- **MD045**: Alt text for all images (`![description](image.jpg)`)
- **MD011**: Correct link syntax (`[text](url)` not `(text)[url]`)

#### Spacing

- **MD009**: No trailing spaces (except 2+ for line breaks)
- **MD010**: Use spaces not tabs
- **MD012**: Max 1 consecutive blank line
- **MD013**: 100 character line limit (configurable)

### Exceptions

- Allow HTML in `allowed_elements` (details, summary, etc.)
- Skip line length in code blocks if needed
- Allow bare URLs in reference sections if marked
- Permit heading repetition in different sections if using `allow_different_nesting`

### Priority Order for Fixes

1. Document structure (headings, hierarchy)
2. Code block language specification  
3. Link formatting and alt text
4. List consistency and indentation
5. Spacing and whitespace cleanup
6. Line length (lowest priority, often skipped)

### Configuration Template

```json
{
  "default": true,
  "MD003": { "style": "atx" },
  "MD007": { "indent": 2 },
  "MD013": { "line_length": 100, "code_blocks": false },
  "MD029": { "style": "ordered" },
  "MD033": { "allowed_elements": ["details", "summary"] }
}
```
