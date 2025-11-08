# bench/commands/update.py
from pathlib import Path
import click
from rich import print as rprint

@click.group(help="Apply patches and update workspace.")
def cmd():
    pass

@cmd.command("apply-patches")
@click.option("--file", "patches_file", default="patches.txt", show_default=True)
def apply_patches(patches_file: str):
    """Read patches.txt and (for now) just list them."""
    p = Path(patches_file)
    if not p.exists():
        rprint(f"[yellow]No patches file at[/] {p.resolve()}")
        return
    lines = [ln.strip() for ln in p.read_text().splitlines() if ln.strip() and not ln.strip().startswith("#")]
    if not lines:
        rprint("[green]No patches to apply.[/]")
        return
    rprint("[bold]Would apply patches:[/]")
    for ln in lines:
        rprint(f" - {ln}")
    # Later: call real patch functions by name
