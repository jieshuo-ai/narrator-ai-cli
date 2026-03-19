"""Narrator AI CLI - main entry point."""

import typer

from narrator_ai import __version__
from narrator_ai.commands import bgm, config_cmd, file, materials, task, user

EPILOG = """
Workflow Paths:

  Path 1 (Standard):
    popular-learning -> generate-writing -> clip-data -> video-composing -> magic-video

  Path 2 (Fast):
    fast-writing -> fast-clip-data -> video-composing -> magic-video

Use 'narrator-ai-cli task types' to list all task types.
Use 'narrator-ai-cli <command> --help' for detailed usage of each command.
"""

app = typer.Typer(
    name="narrator-ai-cli",
    help=(
        "Narrator AI CLI - API client for AI-powered video narration.\n\n"
        "Supports two workflow paths:\n\n"
        "  [Standard] popular-learning -> generate-writing -> clip-data -> video-composing -> magic-video\n\n"
        "  [Fast]     fast-writing -> fast-clip-data -> video-composing -> magic-video\n\n"
        "All commands support --json for machine-readable output.\n"
        "Pass request body via -d '{...}' or -d @file.json."
    ),
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    epilog=EPILOG,
)

app.add_typer(config_cmd.app, name="config")
app.add_typer(user.app, name="user")
app.add_typer(task.app, name="task")
app.add_typer(file.app, name="file")
app.add_typer(materials.app, name="material")
app.add_typer(bgm.app, name="bgm")


def version_callback(value: bool):
    if value:
        print(f"narrator-ai-cli {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show version and exit.",
    ),
):
    """Narrator AI CLI - API client for AI-powered video narration."""
    pass


if __name__ == "__main__":
    app()
