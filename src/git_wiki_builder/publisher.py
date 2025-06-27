"""GitHub Wiki publisher."""

import logging
import tempfile
from pathlib import Path
from typing import Dict

import git
import requests

from .config import Config

logger = logging.getLogger(__name__)


class WikiPublisher:
    """Publishes wiki content to GitHub Wiki."""

    def __init__(self, config: Config) -> None:
        """Initialize wiki publisher.

        Args:
            config: Configuration instance
        """
        self.config = config
        self.github_api_base = "https://api.github.com"

        if not config.github_token:
            raise ValueError("GitHub token is required for publishing")

        if not config.github_repo:
            raise ValueError("GitHub repository is required for publishing")

    def publish(self, wiki_content: Dict[str, str]) -> None:
        """Publish wiki content to GitHub.

        Args:
            wiki_content: Dictionary mapping page names to markdown content
        """
        logger.info(f"Publishing {len(wiki_content)} pages to GitHub Wiki")

        # Verify repository access
        self._verify_repository_access()

        # Clone wiki repository
        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_repo_path = Path(temp_dir) / "wiki"
            wiki_repo = self._clone_wiki_repository(wiki_repo_path)

            # Update wiki pages
            self._update_wiki_pages(wiki_repo_path, wiki_content)

            # Commit and push changes
            self._commit_and_push_changes(wiki_repo, wiki_content)

        logger.info("Wiki published successfully")

    def _verify_repository_access(self) -> None:
        """Verify access to the GitHub repository."""
        url = f"{self.github_api_base}/repos/{self.config.github_repo}"
        headers = {
            "Authorization": f"token {self.config.github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 404:
            raise ValueError(
                f"Repository {self.config.github_repo} not found or no access"
            )
        elif response.status_code == 401:
            raise ValueError("Invalid GitHub token")
        elif response.status_code != 200:
            raise ValueError(
                f"GitHub API error: {response.status_code} - {response.text}"
            )

        repo_data = response.json()
        if not repo_data.get("has_wiki", True):
            logger.warning("Repository wiki may be disabled")

    def _clone_wiki_repository(self, wiki_repo_path: Path) -> git.Repo:
        """Clone the wiki repository.

        Args:
            wiki_repo_path: Path where to clone the wiki repository

        Returns:
            GitPython Repo object
        """
        wiki_url = (
            f"https://x-access-token:{self.config.github_token}@github.com/"
            f"{self.config.github_repo}.wiki.git"
        )

        try:
            # Try to clone existing wiki
            repo = git.Repo.clone_from(wiki_url, wiki_repo_path)
            logger.info("Cloned existing wiki repository")
            return repo

        except git.exc.GitCommandError as e:
            if "not found" in str(e).lower():
                # Wiki doesn't exist yet, create new repository
                logger.info("Wiki repository doesn't exist, creating new one")
                repo = git.Repo.init(wiki_repo_path)

                # Add remote
                repo.create_remote("origin", wiki_url)

                # Configure git user
                self._configure_git_user(repo)

                return repo
            else:
                raise ValueError(f"Failed to clone wiki repository: {e}")

    def _configure_git_user(self, repo: git.Repo) -> None:
        """Configure git user for commits."""
        try:
            # Try to get user info from GitHub API
            headers = {
                "Authorization": f"token {self.config.github_token}",
                "Accept": "application/vnd.github.v3+json",
            }

            response = requests.get(
                f"{self.github_api_base}/user", headers=headers, timeout=30
            )

            if response.status_code == 200:
                user_data = response.json()
                name = user_data.get("name") or user_data.get(
                    "login", "Git Wiki Builder"
                )
                email = (
                    user_data.get("email")
                    or f"{user_data.get('login', 'git-wiki-builder')}"
                    f"@users.noreply.github.com"
                )
            else:
                name = "Git Wiki Builder"
                email = "git-wiki-builder@users.noreply.github.com"

            # Configure git user and credentials
            with repo.config_writer() as git_config:
                git_config.set_value("user", "name", name)
                git_config.set_value("user", "email", email)
                # Configure credential helper to avoid password prompts
                git_config.set_value("credential", "helper", "")

            logger.debug(f"Configured git user: {name} <{email}>")

        except Exception as e:
            logger.warning(f"Could not configure git user: {e}")
            # Use default values
            with repo.config_writer() as git_config:
                git_config.set_value("user", "name", "Git Wiki Builder")
                git_config.set_value(
                    "user",
                    "email",
                    "git-wiki-builder@users.noreply.github.com",
                )
                git_config.set_value("credential", "helper", "")

    def _update_wiki_pages(
        self, wiki_repo_path: Path, wiki_content: Dict[str, str]
    ) -> None:
        """Update wiki pages with new content.

        Args:
            wiki_repo_path: Path to the wiki repository
            wiki_content: Dictionary mapping page names to markdown content
        """
        for page_name, content in wiki_content.items():
            # Convert page name to filename
            filename = self._page_name_to_filename(page_name)
            file_path = wiki_repo_path / filename

            # Write content to file
            file_path.write_text(content, encoding="utf-8")
            logger.debug(f"Updated page: {page_name} -> {filename}")

    def _page_name_to_filename(self, page_name: str) -> str:
        """Convert page name to wiki filename.

        Args:
            page_name: Name of the wiki page

        Returns:
            Filename for the wiki page
        """
        # GitHub wiki filename conventions
        # Replace spaces with dashes, remove special characters
        filename = page_name.replace(" ", "-")
        filename = "".join(c for c in filename if c.isalnum() or c in "-_")

        # Ensure it ends with .md
        if not filename.endswith(".md"):
            filename += ".md"

        return filename

    def _commit_and_push_changes(
        self, repo: git.Repo, wiki_content: Dict[str, str]
    ) -> None:
        """Commit and push changes to the wiki repository.

        Args:
            repo: GitPython Repo object
            wiki_content: Dictionary mapping page names to markdown content
        """
        try:
            # Add all changes
            repo.git.add(".")

            # Check if there are changes to commit
            if repo.is_dirty() or repo.untracked_files:
                # Create commit message
                commit_message = self._generate_commit_message(wiki_content)

                # Commit changes
                repo.index.commit(commit_message)
                logger.info(f"Committed changes: {commit_message}")

                # Push to remote
                origin = repo.remote("origin")

                # For new repositories, push to main/master branch
                try:
                    origin.push("HEAD:main")
                    logger.info("Pushed changes to main branch")
                except git.exc.GitCommandError:
                    try:
                        origin.push("HEAD:master")
                        logger.info("Pushed changes to master branch")
                    except git.exc.GitCommandError:
                        # For existing wikis, just push
                        origin.push()
                        logger.info("Pushed changes to remote")
            else:
                logger.info("No changes to commit")

        except git.exc.GitCommandError as e:
            logger.error(f"Git operation failed: {e}")
            raise ValueError(f"Failed to commit and push changes: {e}")

    def _generate_commit_message(self, wiki_content: Dict[str, str]) -> str:
        """Generate commit message for wiki updates.

        Args:
            wiki_content: Dictionary mapping page names to markdown content

        Returns:
            Commit message
        """
        page_count = len(wiki_content)

        if page_count == 1:
            page_name = list(wiki_content.keys())[0]
            return f"Update {page_name} page"
        else:
            return f"Update wiki documentation ({page_count} pages)"
