# bench/commands/install.py
import subprocess
import sys
import click
from rich import print as rprint

@click.group(help="Install extra tools/dependencies.")
def cmd():
    pass

@cmd.command("pip")
@click.argument("package", nargs=-1, required=True)
def install_pip(package):
    """Install one or more pip packages in the current environment."""
    args = [sys.executable, "-m", "pip", "install", *package]
    rprint(f"[cyan]$ {' '.join(args)}[/]")
    subprocess.check_call(args)
