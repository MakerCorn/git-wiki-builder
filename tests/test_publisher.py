"""Tests for wiki publisher."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, call, patch

import pytest

from git_wiki_builder.config import Config
from git_wiki_builder.publisher import WikiPublisher


class TestWikiPublisher:
    """Test wiki publisher functionality."""

    def create_config_with_github(self) -> Config:
        """Create config with GitHub settings."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(
                repo_path=repo_path,
                github_token="test-token",
                github_repo="owner/repo",
            )
            return config

    def test_init_success(self) -> None:
        """Test successful initialization."""
        config = self.create_config_with_github()
        publisher = WikiPublisher(config)

        assert publisher.config == config
        assert publisher.github_api_base == "https://api.github.com"

    def test_init_missing_token(self) -> None:
        """Test initialization with missing GitHub token."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path, github_repo="owner/repo")

            with pytest.raises(ValueError, match="GitHub token is required"):
                WikiPublisher(config)

    def test_init_missing_repo(self) -> None:
        """Test initialization with missing GitHub repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / "README.md").write_text("# Test Project")

            config = Config(repo_path=repo_path, github_token="test-token")

            with pytest.raises(
                ValueError, match="GitHub repository is required"
            ):
                WikiPublisher(config)

    @patch("git_wiki_builder.publisher.requests.get")
    def test_verify_repository_access_success(self, mock_get: Mock) -> None:
        """Test successful repository access verification."""
        config = self.create_config_with_github()
        publisher = WikiPublisher(config)

        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"has_wiki": True}
        mock_get.return_value = mock_response

        # Should not raise any exception
        publisher._verify_repository_access()

        mock_get.assert_called_once_with(
            "https://api.github.com/repos/owner/repo",
            headers={
                "Authorization": "token test-token",
                "Accept": "application/vnd.github.v3+json",
            },
            timeout=30,
        )

    @patch("git_wiki_builder.publisher.requests.get")
    def test_verify_repository_access_not_found(self, mock_get: Mock) -> None:
        """Test repository access verification with 404 error."""
        config = self.create_config_with_github()
        publisher = WikiPublisher(config)

        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with pytest.raises(
            ValueError, match="Repository owner/repo not found"
        ):
            publisher._verify_repository_access()

    @patch("git_wiki_builder.publisher.requests.get")
    def test_verify_repository_access_unauthorized(
        self, mock_get: Mock
    ) -> None:
        """Test repository access verification with 401 error."""
        config = self.create_config_with_github()
        publisher = WikiPublisher(config)

        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="Invalid GitHub token"):
            publisher._verify_repository_access()

    @patch("git_wiki_builder.publisher.requests.get")
    def test_verify_repository_access_other_error(
        self, mock_get: Mock
    ) -> None:
        """Test repository access verification with other HTTP error."""
        config = self.create_config_with_github()
        publisher = WikiPublisher(config)

        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="GitHub API error: 500"):
            publisher._verify_repository_access()

    @patch("git_wiki_builder.publisher.requests.get")
    def test_verify_repository_access_wiki_disabled_warning(
        self, mock_get: Mock
    ) -> None:
        """Test repository access verification with wiki disabled warning."""
        config = self.create_config_with_github()
        publisher = WikiPublisher(config)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"has_wiki": False}
        mock_get.return_value = mock_response

        with patch(
            "git_wiki_builder.publisher.logger.warning"
        ) as mock_warning:
            publisher._verify_repository_access()
            mock_warning.assert_called_once_with(
                "Repository wiki may be disabled"
            )

    @patch("git_wiki_builder.publisher.git.Repo.clone_from")
    def test_clone_wiki_repository_existing(self, mock_clone: Mock) -> None:
        """Test cloning existing wiki repository."""
        config = self.create_config_with_github()
        publisher = WikiPublisher(config)

        mock_repo = Mock()
        mock_clone.return_value = mock_repo

        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_path = Path(temp_dir) / "wiki"

            result = publisher._clone_wiki_repository(wiki_path)

            assert result == mock_repo
            base_url = "https://x-access-token:test-token@github.com/"
            expected_url = base_url + "owner/repo.wiki.git"
            mock_clone.assert_called_once_with(expected_url, wiki_path)

    @patch("git_wiki_builder.publisher.git.Repo.init")
    @patch("git_wiki_builder.publisher.git.Repo.clone_from")
    def test_clone_wiki_repository_new(
        self, mock_clone: Mock, mock_init: Mock
    ) -> None:
        """Test creating new wiki repository when it doesn't exist."""
        config = self.create_config_with_github()
        publisher = WikiPublisher(config)

        # Mock clone failure with GitCommandError specifically
        from git.exc import GitCommandError

        mock_clone.side_effect = GitCommandError(
            "clone", "repository not found"
        )

        mock_repo = Mock()
        mock_init.return_value = mock_repo

        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_path = Path(temp_dir) / "wiki"

            with patch.object(
                publisher, "_configure_git_user"
            ) as mock_configure:
                result = publisher._clone_wiki_repository(wiki_path)

                assert result == mock_repo
                mock_init.assert_called_once_with(wiki_path)
                base_url = "https://x-access-token:test-token@github.com/"
                expected_url = base_url + "owner/repo.wiki.git"
                mock_repo.create_remote.assert_called_once_with(
                    "origin", expected_url
                )
                mock_configure.assert_called_once_with(mock_repo)

    @patch("git_wiki_builder.publisher.git.Repo.clone_from")
    def test_clone_wiki_repository_other_error(self, mock_clone: Mock) -> None:
        """Test clone failure with other error."""
        config = self.create_config_with_github()
        publisher = WikiPublisher(config)

        from git.exc import GitCommandError

        mock_clone.side_effect = GitCommandError("clone", "permission denied")

        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_path = Path(temp_dir) / "wiki"

            with pytest.raises(
                ValueError, match="Failed to clone wiki repository"
            ):
                publisher._clone_wiki_repository(wiki_path)

    @patch("git_wiki_builder.publisher.requests.get")
    def test_configure_git_user_success(self, mock_get: Mock) -> None:
        """Test successful git user configuration."""
        config = self.create_config_with_github()
        publisher = WikiPublisher(config)

        # Mock GitHub API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "Test User",
            "email": "test@example.com",
            "login": "testuser",
        }
        mock_get.return_value = mock_response

        # Mock git repo and config writer
        mock_repo = Mock()
        mock_config_writer = Mock()
        mock_repo.config_writer.return_value.__enter__ = Mock(
            return_value=mock_config_writer
        )
        mock_repo.config_writer.return_value.__exit__ = Mock(
            return_value=False
        )

        publisher._configure_git_user(mock_repo)

        mock_config_writer.set_value.assert_any_call(
            "user", "name", "Test User"
        )
        mock_config_writer.set_value.assert_any_call(
            "user", "email", "test@example.com"
        )

    @patch("git_wiki_builder.publisher.requests.get")
    def test_configure_git_user_no_name(self, mock_get: Mock) -> None:
        """Test git user configuration with no name in API response."""
        config = self.create_config_with_github()
        publisher = WikiPublisher(config)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"login": "testuser"}
        mock_get.return_value = mock_response

        mock_repo = Mock()
        mock_config_writer = Mock()
        mock_repo.config_writer.return_value.__enter__ = Mock(
            return_value=mock_config_writer
        )
        mock_repo.config_writer.return_value.__exit__ = Mock(
            return_value=False
        )

        publisher._configure_git_user(mock_repo)

        mock_config_writer.set_value.assert_any_call(
            "user", "name", "testuser"
        )
        mock_config_writer.set_value.assert_any_call(
            "user", "email", "testuser@users.noreply.github.com"
        )

    @patch("git_wiki_builder.publisher.requests.get")
    def test_configure_git_user_api_failure(self, mock_get: Mock) -> None:
        """Test git user configuration when API fails."""
        config = self.create_config_with_github()
        publisher = WikiPublisher(config)

        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        mock_repo = Mock()
        mock_config_writer = Mock()
        mock_repo.config_writer.return_value.__enter__ = Mock(
            return_value=mock_config_writer
        )
        mock_repo.config_writer.return_value.__exit__ = Mock(
            return_value=False
        )

        publisher._configure_git_user(mock_repo)

        mock_config_writer.set_value.assert_any_call(
            "user", "name", "Git Wiki Builder"
        )
        mock_config_writer.set_value.assert_any_call(
            "user", "email", "git-wiki-builder@users.noreply.github.com"
        )

    @patch("git_wiki_builder.publisher.requests.get")
    def test_configure_git_user_exception(self, mock_get: Mock) -> None:
        """Test git user configuration with exception handling."""
        config = self.create_config_with_github()
        publisher = WikiPublisher(config)

        mock_get.side_effect = Exception("Network error")

        mock_repo = Mock()
        mock_config_writer = Mock()
        mock_repo.config_writer.return_value.__enter__ = Mock(
            return_value=mock_config_writer
        )
        mock_repo.config_writer.return_value.__exit__ = Mock(
            return_value=False
        )

        publisher._configure_git_user(mock_repo)

        # Should fall back to default values
        mock_config_writer.set_value.assert_any_call(
            "user", "name", "Git Wiki Builder"
        )
        mock_config_writer.set_value.assert_any_call(
            "user", "email", "git-wiki-builder@users.noreply.github.com"
        )

    def test_update_wiki_pages(self) -> None:
        """Test updating wiki pages."""
        config = self.create_config_with_github()
        publisher = WikiPublisher(config)

        wiki_content = {
            "Home": "# Home\nWelcome to the wiki",
            "Installation": "# Installation\nHow to install",
            "API Reference": "# API Reference\nAPI documentation",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            wiki_path = Path(temp_dir)

            publisher._update_wiki_pages(wiki_path, wiki_content)

            # Check files were created
            assert (wiki_path / "Home.md").exists()
            assert (wiki_path / "Installation.md").exists()
            assert (wiki_path / "API-Reference.md").exists()

            # Check content
            assert (
                wiki_path / "Home.md"
            ).read_text() == "# Home\nWelcome to the wiki"
            assert (
                wiki_path / "Installation.md"
            ).read_text() == "# Installation\nHow to install"
            assert (
                wiki_path / "API-Reference.md"
            ).read_text() == "# API Reference\nAPI documentation"

    def test_page_name_to_filename(self) -> None:
        """Test page name to filename conversion."""
        config = self.create_config_with_github()
        publisher = WikiPublisher(config)

        assert publisher._page_name_to_filename("Home") == "Home.md"
        assert (
            publisher._page_name_to_filename("API Reference")
            == "API-Reference.md"
        )
        assert (
            publisher._page_name_to_filename("Getting Started")
            == "Getting-Started.md"
        )
        assert publisher._page_name_to_filename("test_file") == "test_file.md"
        assert (
            publisher._page_name_to_filename("Special!@#Characters")
            == "SpecialCharacters.md"
        )
        assert publisher._page_name_to_filename("already.md") == "alreadymd.md"

    def test_commit_and_push_changes_with_changes(self) -> None:
        """Test committing and pushing changes when there are changes."""
        config = self.create_config_with_github()
        publisher = WikiPublisher(config)

        mock_repo = Mock()
        mock_repo.is_dirty.return_value = True
        mock_repo.untracked_files = ["Home.md"]
        mock_origin = Mock()
        mock_repo.remote.return_value = mock_origin

        wiki_content = {"Home": "# Home\nContent"}

        publisher._commit_and_push_changes(mock_repo, wiki_content)

        mock_repo.git.add.assert_called_once_with(".")
        mock_repo.index.commit.assert_called_once_with("Update Home page")
        mock_origin.push.assert_called_once_with("HEAD:main")

    def test_commit_and_push_changes_multiple_pages(self) -> None:
        """Test committing multiple pages."""
        config = self.create_config_with_github()
        publisher = WikiPublisher(config)

        mock_repo = Mock()
        mock_repo.is_dirty.return_value = True
        mock_repo.untracked_files = []
        mock_origin = Mock()
        mock_repo.remote.return_value = mock_origin

        wiki_content = {
            "Home": "# Home\nContent",
            "Installation": "# Installation\nContent",
        }

        publisher._commit_and_push_changes(mock_repo, wiki_content)

        mock_repo.index.commit.assert_called_once_with(
            "Update wiki documentation (2 pages)"
        )

    def test_commit_and_push_changes_no_changes(self) -> None:
        """Test when there are no changes to commit."""
        config = self.create_config_with_github()
        publisher = WikiPublisher(config)

        mock_repo = Mock()
        mock_repo.is_dirty.return_value = False
        mock_repo.untracked_files = []

        wiki_content = {"Home": "# Home\nContent"}

        publisher._commit_and_push_changes(mock_repo, wiki_content)

        mock_repo.git.add.assert_called_once_with(".")
        mock_repo.index.commit.assert_not_called()

    def test_commit_and_push_changes_master_fallback(self) -> None:
        """Test push fallback to master branch."""
        config = self.create_config_with_github()
        publisher = WikiPublisher(config)

        mock_repo = Mock()
        mock_repo.is_dirty.return_value = True
        mock_repo.untracked_files = []
        mock_origin = Mock()
        mock_repo.remote.return_value = mock_origin

        # Main branch push fails, master succeeds
        from git.exc import GitCommandError

        mock_origin.push.side_effect = [
            GitCommandError("push", "main failed"),
            None,
        ]

        wiki_content = {"Home": "# Home\nContent"}

        publisher._commit_and_push_changes(mock_repo, wiki_content)

        # Should try main first, then master
        assert mock_origin.push.call_count == 2
        mock_origin.push.assert_has_calls(
            [call("HEAD:main"), call("HEAD:master")]
        )

    def test_commit_and_push_changes_generic_push(self) -> None:
        """Test generic push when both main and master fail."""
        config = self.create_config_with_github()
        publisher = WikiPublisher(config)

        mock_repo = Mock()
        mock_repo.is_dirty.return_value = True
        mock_repo.untracked_files = []
        mock_origin = Mock()
        mock_repo.remote.return_value = mock_origin

        # Both main and master fail, generic push succeeds
        from git.exc import GitCommandError

        mock_origin.push.side_effect = [
            GitCommandError("push", "main failed"),
            GitCommandError("push", "master failed"),
            None,
        ]

        wiki_content = {"Home": "# Home\nContent"}

        publisher._commit_and_push_changes(mock_repo, wiki_content)

        # Should try all three push methods
        assert mock_origin.push.call_count == 3
        mock_origin.push.assert_has_calls(
            [call("HEAD:main"), call("HEAD:master"), call()]
        )

    def test_commit_and_push_changes_git_error(self) -> None:
        """Test git error handling during commit and push."""
        config = self.create_config_with_github()
        publisher = WikiPublisher(config)

        mock_repo = Mock()
        mock_repo.is_dirty.return_value = True
        mock_repo.untracked_files = []
        from git.exc import GitCommandError

        mock_repo.git.add.side_effect = GitCommandError("add", "Git error")

        wiki_content = {"Home": "# Home\nContent"}

        with pytest.raises(
            ValueError, match="Failed to commit and push changes"
        ):
            publisher._commit_and_push_changes(mock_repo, wiki_content)

    def test_generate_commit_message_single_page(self) -> None:
        """Test commit message generation for single page."""
        config = self.create_config_with_github()
        publisher = WikiPublisher(config)

        wiki_content = {"Home": "# Home\nContent"}
        message = publisher._generate_commit_message(wiki_content)

        assert message == "Update Home page"

    def test_generate_commit_message_multiple_pages(self) -> None:
        """Test commit message generation for multiple pages."""
        config = self.create_config_with_github()
        publisher = WikiPublisher(config)

        wiki_content = {
            "Home": "# Home\nContent",
            "Installation": "# Installation\nContent",
            "API": "# API\nContent",
        }
        message = publisher._generate_commit_message(wiki_content)

        assert message == "Update wiki documentation (3 pages)"

    def test_publish_integration(self) -> None:
        """Test full publish integration."""
        config = self.create_config_with_github()
        publisher = WikiPublisher(config)

        wiki_content = {"Home": "# Home\nWelcome to the wiki"}

        with (
            patch.object(
                publisher, "_verify_repository_access"
            ) as mock_verify,
            patch.object(publisher, "_clone_wiki_repository") as mock_clone,
            patch.object(publisher, "_update_wiki_pages") as mock_update,
            patch.object(publisher, "_commit_and_push_changes") as mock_commit,
            patch(
                "git_wiki_builder.publisher.tempfile.TemporaryDirectory"
            ) as mock_temp_dir,
        ):

            # Mock temporary directory context manager
            mock_temp_dir.return_value.__enter__ = Mock(
                return_value="/tmp/test"
            )
            mock_temp_dir.return_value.__exit__ = Mock(return_value=False)

            mock_repo = Mock()
            mock_clone.return_value = mock_repo

            publisher.publish(wiki_content)

            mock_verify.assert_called_once()
            mock_clone.assert_called_once_with(Path("/tmp/test") / "wiki")
            mock_update.assert_called_once_with(
                Path("/tmp/test") / "wiki", wiki_content
            )
            mock_commit.assert_called_once_with(mock_repo, wiki_content)
