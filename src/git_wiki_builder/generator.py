"""Wiki content generator using AI."""

import logging
from typing import Any, Dict, List

from .ai_client import AIClient, MockAIClient
from .config import Config
from .content_analyzer import ContentAnalyzer
from .prompt_manager import PromptManager
from .validator import MarkdownValidator

logger = logging.getLogger(__name__)


class WikiGenerator:
    """Generates wiki content using AI based on project documentation."""

    def __init__(self, config: Config, mock_mode: bool = False) -> None:
        """Initialize the wiki generator.

        Args:
            config: Configuration instance
            mock_mode: Use mock AI client for testing
        """
        self.config = config
        self.ai_client = MockAIClient(config) if mock_mode else AIClient(config)
        self.content_analyzer = ContentAnalyzer(config)
        self.prompt_manager = PromptManager(config)
        self.validator = MarkdownValidator(config) if not config.skip_validation else None

    def generate(self) -> Dict[str, str]:
        """Generate wiki content.

        Returns:
            Dictionary mapping page names to markdown content
        """
        logger.info("Starting wiki generation")

        # Analyze project content
        project_analysis = self.content_analyzer.analyze()
        logger.info(f"Analyzed {len(project_analysis.files)} files")

        # Generate wiki structure
        wiki_structure = self._generate_wiki_structure(project_analysis)
        logger.info(f"Generated structure with {len(wiki_structure)} sections")

        # Generate content for each page
        wiki_content = {}
        for section_name, pages in wiki_structure.items():
            for page_name in pages:
                logger.info(f"Generating content for {page_name}")
                content = self._generate_page_content(page_name, section_name, project_analysis)

                # Validate content if validation is enabled
                if self.validator:
                    validation_result = self.validator.validate_content(content)
                    if not validation_result.is_valid:
                        logger.warning(
                            f"Validation issues for {page_name}: {validation_result.errors}"
                        )
                        # Fix common issues automatically
                        content = self.validator.fix_content(content)

                wiki_content[page_name] = content

        # Generate Home page
        home_content = self._generate_home_page(project_analysis, wiki_structure)
        if self.validator:
            validation_result = self.validator.validate_content(home_content)
            if not validation_result.is_valid:
                home_content = self.validator.fix_content(home_content)

        wiki_content["Home"] = home_content

        logger.info(f"Generated {len(wiki_content)} wiki pages")
        return wiki_content

    def _generate_wiki_structure(self, project_analysis: Any) -> Dict[str, List[str]]:
        """Generate wiki structure based on project analysis.

        Args:
            project_analysis: Project analysis results

        Returns:
            Dictionary mapping section names to page lists
        """
        # Start with default structure
        structure = self.config.wiki_structure.copy()

        # Customize based on project content
        if project_analysis.has_api_docs:
            structure["API Reference"].extend(["sdk_reference", "code_examples"])

        if project_analysis.has_docker:
            structure["Deployment"].extend(["docker_deployment", "container_management"])

        if project_analysis.has_tests:
            structure["Development"].extend(["running_tests", "test_coverage"])

        if project_analysis.has_ci_cd:
            structure["Development"].extend(["ci_cd_pipeline", "automated_deployment"])

        # Remove empty sections
        structure = {k: v for k, v in structure.items() if v}

        return structure

    def _generate_page_content(
        self, page_name: str, section_name: str, project_analysis: Any
    ) -> str:
        """Generate content for a specific page.

        Args:
            page_name: Name of the page
            section_name: Section the page belongs to
            project_analysis: Project analysis results

        Returns:
            Generated markdown content
        """
        # Get appropriate prompt
        prompt = self.prompt_manager.get_page_prompt(page_name, section_name)

        # Prepare context
        context = {
            "project_name": project_analysis.project_name,
            "project_description": project_analysis.description,
            "readme_content": project_analysis.readme_content,
            "docs_content": project_analysis.docs_content,
            "code_structure": project_analysis.code_structure,
            "dependencies": project_analysis.dependencies,
            "page_name": page_name,
            "section_name": section_name,
            "has_api": project_analysis.has_api_docs,
            "has_docker": project_analysis.has_docker,
            "has_tests": project_analysis.has_tests,
            "has_ci_cd": project_analysis.has_ci_cd,
        }

        # Generate content using AI
        content = self.ai_client.generate_content(prompt, context)

        return content

    def _generate_home_page(
        self, project_analysis: Any, wiki_structure: Dict[str, List[str]]
    ) -> str:
        """Generate the Home page content.

        Args:
            project_analysis: Project analysis results
            wiki_structure: Generated wiki structure

        Returns:
            Generated markdown content for Home page
        """
        prompt = self.prompt_manager.get_home_prompt()

        # Create navigation structure
        navigation = []
        for section_name, pages in wiki_structure.items():
            navigation.append({"section": section_name, "pages": pages})

        context = {
            "project_name": project_analysis.project_name,
            "project_description": project_analysis.description,
            "readme_content": project_analysis.readme_content,
            "navigation": navigation,
            "key_features": project_analysis.key_features,
            "quick_start": project_analysis.quick_start_info,
        }

        content = self.ai_client.generate_content(prompt, context)

        return content
