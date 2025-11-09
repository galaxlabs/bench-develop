# bench/commands/utils.py
from pathlib import Path
import click
from rich import print as rprint
from bench.commands.make import make_workspace


@click.command("init")
@click.argument("path", required=False, default=".")
@click.option("--auto-cd/--no-auto-cd", default=False)
@click.option("--no-venv", is_flag=True, default=False)
def cmd(path, auto_cd, no_venv):
    """Alias for `bench make workspace`."""
    ctx = click.get_current_context()
    ctx.invoke(make_workspace.callback, path=path, py_exe=None, auto_cd=auto_cd, no_venv=no_venv)

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
