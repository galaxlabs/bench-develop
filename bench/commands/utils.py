# bench/commands/utils.py
from pathlib import Path
import click
from rich import print as rprint

@click.group(help="Utility helpers.")
def cmd():
    pass

@cmd.command("tree")
@click.argument("path", required=False, default=".")
def tree(path: str):
    """Print a shallow tree of a directory (1 level)."""
    p = Path(path)
    rprint(f"[bold]Tree:[/] {p.resolve()}")
    for child in sorted(p.iterdir()):
        kind = "[dir]" if child.is_dir() else "[file]"
        rprint(f"  {kind} {child.name}")
