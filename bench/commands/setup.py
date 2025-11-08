# bench/commands/setup.py
import click
from rich import print as rprint

@click.group(help="Production/deployment helpers (nginx/systemd/ssl stubs).")
def cmd():
    pass

@cmd.command("production")
@click.option("--nginx", is_flag=True)
@click.option("--systemd", is_flag=True)
@click.option("--ssl", is_flag=True)
def production(nginx, systemd, ssl):
    rprint("[bold]Setup production (stub)[/]")
    if nginx: rprint(" - would render Nginx conf")
    if systemd: rprint(" - would render systemd units")
    if ssl: rprint(" - would request/renew certificates")
