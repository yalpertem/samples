"""Command line interface for audio YAML generator."""

import sys
from pathlib import Path

import click

from .__about__ import __version__
from .audio_monitor import AudioMonitor
from .core import AudioYamlGenerator


@click.command()
@click.version_option(version=__version__, prog_name="audio-yaml")
@click.option(
    "-m",
    "--monitor",
    "mode",
    flag_value="monitor",
    help="Monitor directory for new files (default)",
)
@click.option(
    "-b",
    "--batch",
    "mode",
    flag_value="batch",
    help="Process existing files only (no monitoring)",
)
@click.option(
    "-c",
    "--cleanup",
    "mode",
    flag_value="cleanup",
    help="Clean up orphaned YAML files and exit",
)
@click.argument(
    "directory",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=Path.cwd(),
    required=False,
)
def main(mode: str, directory: Path):
    """Generate YAML metadata files for audio samples.

    DIRECTORY: Directory to process (default: current directory)

    Examples:

        audio-yaml                          # Monitor current directory

        audio-yaml -m samples/              # Monitor samples directory

        audio-yaml -b samples/drums/        # Batch process drums directory

        audio-yaml -c samples/              # Clean up orphaned YAML files
    """
    generator = AudioYamlGenerator(directory)

    if mode is None:
        mode = "monitor"

    try:
        if mode == "batch":
            generator.batch_process(directory)
        elif mode == "cleanup":
            generator.cleanup_orphaned_yaml(directory)
        elif mode == "monitor":
            monitor = AudioMonitor(directory, generator)
            monitor.start_monitoring()
        else:
            click.echo(f"Unknown mode: {mode}", err=True)
            sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
