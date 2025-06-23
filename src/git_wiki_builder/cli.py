"""Command line interface for Git Wiki Builder."""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import Config
from .generator import WikiGenerator
from .publisher import WikiPublisher
from .utils import setup_logging

console = Console()


@click.command()
@click.option(
    "--repo-path",
    "-r",
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, path_type=Path
    ),
    default=".",
    help="Path to the repository (default: current directory)",
)
@click.option(
    "--config-file",
    "-c",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, path_type=Path
    ),
    help="Path to configuration file",
)
@click.option(
    "--prompt-file",
    "-p",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, path_type=Path
    ),
    help="Path to custom prompt file",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    help="Output directory for generated wiki files",
)
@click.option(
    "--github-token",
    envvar="GITHUB_TOKEN",
    help=(
        "GitHub token for wiki publishing "
        "(can be set via GITHUB_TOKEN env var)"
    ),
)
@click.option(
    "--github-repo",
    envvar="GITHUB_REPOSITORY",
    help=(
        "GitHub repository in format 'owner/repo' "
        "(can be set via GITHUB_REPOSITORY env var)"
    ),
)
@click.option(
    "--ai-provider",
    type=click.Choice(["github", "openai", "anthropic"], case_sensitive=False),
    default="github",
    help="AI provider to use for content generation",
)
@click.option(
    "--ai-model",
    help=(
        "AI model to use "
        "(e.g., gpt-4o-mini, gpt-4, claude-3-sonnet-20240229)"
    ),
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Generate wiki content without publishing",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging",
)
@click.option(
    "--skip-validation",
    is_flag=True,
    help="Skip markdown validation",
)
@click.version_option()
def main(
    repo_path: Path,
    config_file: Optional[Path],
    prompt_file: Optional[Path],
    output_dir: Optional[Path],
    github_token: Optional[str],
    github_repo: Optional[str],
    ai_provider: str,
    ai_model: Optional[str],
    dry_run: bool,
    verbose: bool,
    skip_validation: bool,
) -> None:
    """Generate and publish GitHub Wiki documentation using AI.

    This tool reads your project's README and documentation files,
    then uses AI to generate well-structured wiki content that gets
    published to your GitHub repository's wiki.
    """
    setup_logging(verbose)

    try:
        # Load configuration
        config = Config.load(
            config_file=config_file,
            repo_path=repo_path,
            ai_provider=ai_provider,
            ai_model=ai_model,
            github_token=github_token,
            github_repo=github_repo,
            output_dir=output_dir,
            prompt_file=prompt_file,
            skip_validation=skip_validation,
        )

        # Validate API keys for generation
        if not dry_run:
            config.validate_for_generation()

        console.print(
            f"[bold green]Git Wiki Builder v{config.version}[/bold green]"
        )
        console.print(f"Repository: {config.repo_path}")
        console.print(f"AI Provider: {config.ai_provider}")
        console.print(f"AI Model: {config.ai_model}")

        if dry_run:
            console.print(
                "[yellow]Running in dry-run mode - no publishing will "
                "occur[/yellow]"
            )

        # Generate wiki content
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generating wiki content...", total=None)

            generator = WikiGenerator(config, mock_mode=dry_run)
            wiki_content = generator.generate()

            progress.update(
                task, description="Wiki content generated successfully"
            )

        console.print(
            f"[green]Generated {len(wiki_content)} wiki pages[/green]"
        )

        # Save to output directory if specified
        if config.output_dir:
            config.output_dir.mkdir(parents=True, exist_ok=True)
            for page_name, content in wiki_content.items():
                output_file = config.output_dir / f"{page_name}.md"
                output_file.write_text(content, encoding="utf-8")
            console.print(
                f"[green]Wiki files saved to {config.output_dir}[/green]"
            )

        # Publish to GitHub Wiki
        if not dry_run:
            if not config.github_token or not config.github_repo:
                console.print(
                    "[red]Error: GitHub token and repository are required "
                    "for publishing[/red]"
                )
                console.print(
                    "Set GITHUB_TOKEN and GITHUB_REPOSITORY environment "
                    "variables"
                )
                sys.exit(1)

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(
                    "Publishing to GitHub Wiki...", total=None
                )

                publisher = WikiPublisher(config)
                publisher.publish(wiki_content)

                progress.update(
                    task, description="Published to GitHub Wiki successfully"
                )

            console.print("[green]Wiki published successfully![/green]")
            console.print(
                f"View at: https://github.com/{config.github_repo}/wiki"
            )

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()
