"""Prompt management for AI content generation."""

import logging
from typing import Dict

from .config import Config

logger = logging.getLogger(__name__)


class PromptManager:
    """Manages prompts for different types of wiki content."""

    def __init__(self, config: Config) -> None:
        """Initialize prompt manager.

        Args:
            config: Configuration instance
        """
        self.config = config
        self.custom_prompts = self._load_custom_prompts()

    def _load_custom_prompts(self) -> Dict[str, str]:
        """Load custom prompts from file."""
        if not self.config.prompt_file or not self.config.prompt_file.exists():
            return {}

        try:
            import yaml

            with open(self.config.prompt_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"Could not load custom prompts: {e}")
            return {}

    def get_home_prompt(self) -> str:
        """Get prompt for Home page generation."""
        if "home" in self.custom_prompts:
            return self.custom_prompts["home"]

        return """
Create a comprehensive Home page for the {project_name} project wiki.

Project Information:
- Name: {project_name}
- Description: {project_description}
- README Content: {readme_content}

Navigation Structure:
{navigation}

Key Features:
{key_features}

Quick Start Information:
{quick_start}

Requirements:
1. Start with a clear project title and description
2. Include a table of contents linking to all wiki sections
3. Provide a brief overview of key features
4. Include quick start/getting started information
5. Add navigation links to major sections
6. Use proper markdown formatting with clear headings
7. Make it welcoming and informative for new users
8. Include badges or status indicators if relevant
9. Add contact/support information if available
10. Ensure the content is well-structured and easy to navigate

Format the response as clean markdown with proper heading hierarchy.
"""

    def get_page_prompt(self, page_name: str, section_name: str) -> str:
        """Get prompt for specific page generation.

        Args:
            page_name: Name of the page
            section_name: Section the page belongs to

        Returns:
            Appropriate prompt for the page
        """
        # Check for custom prompt
        prompt_key = f"{section_name.lower()}_{page_name.lower()}"
        if prompt_key in self.custom_prompts:
            return self.custom_prompts[prompt_key]

        # Check for section-specific prompt
        section_key = section_name.lower().replace(" ", "_")
        if section_key in self.custom_prompts:
            return self.custom_prompts[section_key]

        # Return default prompt based on page type
        return self._get_default_page_prompt(page_name, section_name)

    def _get_default_page_prompt(
        self, page_name: str, section_name: str
    ) -> str:
        """Get default prompt for page type."""
        page_lower = page_name.lower()
        section_lower = section_name.lower()

        # Installation pages
        if "install" in page_lower:
            return self._get_installation_prompt()

        # Configuration pages
        elif "config" in page_lower:
            return self._get_configuration_prompt()

        # API documentation pages
        elif section_lower == "api reference" or "api" in page_lower:
            return self._get_api_prompt()

        # Development pages
        elif section_lower == "development" or "develop" in page_lower:
            return self._get_development_prompt()

        # Deployment pages
        elif section_lower == "deployment" or "deploy" in page_lower:
            return self._get_deployment_prompt()

        # FAQ pages
        elif "faq" in page_lower or "question" in page_lower:
            return self._get_faq_prompt()

        # Troubleshooting pages
        elif "troubleshoot" in page_lower or "problem" in page_lower:
            return self._get_troubleshooting_prompt()

        # Examples pages
        elif "example" in page_lower or "usage" in page_lower:
            return self._get_examples_prompt()

        # Default generic prompt
        else:
            return self._get_generic_prompt()

    def _get_installation_prompt(self) -> str:
        """Get installation prompt."""
        return """
Create comprehensive installation documentation for {project_name}.

Project Information:
- Name: {project_name}
- Description: {project_description}
- Dependencies: {dependencies}
- README Content: {readme_content}
- Documentation: {docs_content}

Requirements:
1. Provide multiple installation methods (pip, conda, source, etc.)
2. List system requirements and prerequisites
3. Include platform-specific instructions (Windows, macOS, Linux)
4. Cover dependency installation
5. Provide verification steps
6. Include troubleshooting for common installation issues
7. Add Docker installation if applicable: {has_docker}
8. Use clear step-by-step instructions
9. Include code examples and command snippets
10. Add links to related documentation

Format as clean markdown with proper code blocks and clear sections.
"""

    def _get_configuration_prompt(self) -> str:
        """Get configuration prompt."""
        return """
Create detailed configuration documentation for {project_name}.

Project Information:
- Name: {project_name}
- Description: {project_description}
- README Content: {readme_content}
- Documentation: {docs_content}

Requirements:
1. Explain all configuration options and parameters
2. Provide configuration file examples
3. Cover environment variable setup
4. Include default values and recommended settings
5. Explain configuration file locations
6. Cover different environments (dev, staging, prod)
7. Include security considerations
8. Provide validation and testing steps
9. Add troubleshooting for configuration issues
10. Include links to related sections

Format as clean markdown with proper code blocks and examples.
"""

    def _get_api_prompt(self) -> str:
        """Get API documentation prompt."""
        return """
Create comprehensive API documentation for {project_name}.

Project Information:
- Name: {project_name}
- Description: {project_description}
- Has API Documentation: {has_api}
- README Content: {readme_content}
- Documentation: {docs_content}
- Code Structure: {code_structure}

Requirements:
1. Provide API overview and architecture
2. Document all endpoints with methods, parameters, and responses
3. Include authentication and authorization details
4. Provide request/response examples
5. Cover error handling and status codes
6. Include rate limiting information
7. Add SDK/client library information
8. Provide interactive examples or curl commands
9. Cover versioning and backwards compatibility
10. Include links to code examples

Format as clean markdown with proper code blocks and clear structure.
"""

    def _get_development_prompt(self) -> str:
        """Get development prompt."""
        return """
Create comprehensive development documentation for {project_name}.

Project Information:
- Name: {project_name}
- Description: {project_description}
- Has Tests: {has_tests}
- Has CI/CD: {has_ci_cd}
- Code Structure: {code_structure}
- Dependencies: {dependencies}
- README Content: {readme_content}
- Documentation: {docs_content}

Requirements:
1. Explain development environment setup
2. Cover coding standards and guidelines
3. Document the project structure and architecture
4. Include testing procedures: {has_tests}
5. Explain CI/CD pipeline: {has_ci_cd}
6. Cover contribution guidelines
7. Include debugging and troubleshooting tips
8. Document build and release processes
9. Add code review procedures
10. Include links to development tools

Format as clean markdown with clear sections and code examples.
"""

    def _get_deployment_prompt(self) -> str:
        """Get deployment prompt."""
        return """
Create comprehensive deployment documentation for {project_name}.

Project Information:
- Name: {project_name}
- Description: {project_description}
- Has Docker: {has_docker}
- Has CI/CD: {has_ci_cd}
- README Content: {readme_content}
- Documentation: {docs_content}

Requirements:
1. Cover different deployment environments
2. Include Docker deployment if applicable: {has_docker}
3. Document cloud platform deployment (AWS, GCP, Azure)
4. Cover environment configuration
5. Include monitoring and logging setup
6. Document scaling and performance considerations
7. Cover security best practices
8. Include backup and disaster recovery
9. Document CI/CD deployment: {has_ci_cd}
10. Add troubleshooting for deployment issues

Format as clean markdown with step-by-step instructions.
"""

    def _get_faq_prompt(self) -> str:
        """Get FAQ prompt."""
        return """
Create a comprehensive FAQ section for {project_name}.

Project Information:
- Name: {project_name}
- Description: {project_description}
- README Content: {readme_content}
- Documentation: {docs_content}

Requirements:
1. Address common user questions and issues
2. Cover installation and setup problems
3. Include configuration and usage questions
4. Address performance and troubleshooting
5. Cover compatibility and requirements
6. Include best practices and recommendations
7. Address security and privacy concerns
8. Cover integration and API questions
9. Include links to detailed documentation
10. Organize by categories for easy navigation

Format as clean markdown with clear Q&A structure.
"""

    def _get_troubleshooting_prompt(self) -> str:
        """Get troubleshooting prompt."""
        return """
Create comprehensive troubleshooting documentation for {project_name}.

Project Information:
- Name: {project_name}
- Description: {project_description}
- README Content: {readme_content}
- Documentation: {docs_content}

Requirements:
1. Cover common error messages and solutions
2. Include diagnostic steps and tools
3. Address installation and setup issues
4. Cover runtime and performance problems
5. Include configuration and environment issues
6. Document debugging procedures
7. Provide log analysis guidance
8. Include system requirements troubleshooting
9. Cover integration and compatibility issues
10. Add escalation and support contact information

Format as clean markdown with clear problem-solution structure.
"""

    def _get_examples_prompt(self) -> str:
        """Get examples prompt."""
        return """
Create comprehensive examples and usage documentation for {project_name}.

Project Information:
- Name: {project_name}
- Description: {project_description}
- Code Structure: {code_structure}
- README Content: {readme_content}
- Documentation: {docs_content}

Requirements:
1. Provide basic usage examples
2. Include advanced use cases and scenarios
3. Cover different programming languages if applicable
4. Include complete, runnable code examples
5. Explain each example with clear comments
6. Cover common patterns and best practices
7. Include integration examples
8. Provide sample data and configurations
9. Add links to live demos or repositories
10. Organize examples by complexity and use case

Format as clean markdown with proper code blocks and explanations.
"""

    def _get_generic_prompt(self) -> str:
        """Get generic prompt for any page."""
        return """
Create comprehensive documentation for the "{page_name}" page in the
{section_name} section of the {project_name} wiki.

Project Information:
- Name: {project_name}
- Description: {project_description}
- README Content: {readme_content}
- Documentation: {docs_content}
- Code Structure: {code_structure}

Requirements:
1. Create content relevant to the page name and section
2. Provide comprehensive coverage of the topic
3. Include practical examples and code snippets where appropriate
4. Use clear, well-structured markdown formatting
5. Include proper heading hierarchy
6. Add links to related documentation
7. Provide step-by-step instructions where applicable
8. Include troubleshooting tips if relevant
9. Make content accessible to different skill levels
10. Ensure accuracy and completeness

Format as clean markdown with proper structure and formatting.
"""
