# bench/commands/git.py
import subprocess
import click
from rich import print as rprint

@click.group(help="Git helpers.")
def cmd():
    pass

@cmd.command("clone")
@click.argument("repo")
@click.argument("dest", required=False)
def clone(repo, dest):
    """Clone a repository (thin wrapper)."""
    args = ["git", "clone", repo] + ([dest] if dest else [])
    rprint(f"[cyan]$ {' '.join(args)}[/]")
    subprocess.check_call(args)
