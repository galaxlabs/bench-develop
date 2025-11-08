# bench/commands/config.py
from __future__ import annotations
import json
import os
import shlex
import subprocess
from pathlib import Path
import click
from rich import print as rprint

# Default location: ./config/common_config.json in the current workspace
DEFAULT_CONF = Path("config") / "common_config.json"

@click.group(help="Manage bench workspace config (./config/common_config.json).")
def cmd():
    pass

def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text() or "{}")
    except Exception as e:
        rprint(f"[red]Failed to read JSON:[/] {path}  ({e})")
        return {}

def _save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    rprint(f"[green]Saved:[/] {path.resolve()}")

@cmd.command("path")
@click.option("--file", "conf_path", type=click.Path(path_type=Path), default=DEFAULT_CONF, show_default=True)
def show_path(conf_path: Path):
    """Show the config file path."""
    rprint(str(conf_path.resolve()))

@cmd.command("init")
@click.option("--file", "conf_path", type=click.Path(path_type=Path), default=DEFAULT_CONF, show_default=True)
def init(conf_path: Path):
    """Create an empty config file if missing."""
    if conf_path.exists():
        rprint(f"[yellow]Already exists:[/] {conf_path.resolve()}")
        return
    _save(conf_path, {})

@cmd.command("show")
@click.option("--file", "conf_path", type=click.Path(path_type=Path), default=DEFAULT_CONF, show_default=True)
def show(conf_path: Path):
    """Print the entire config JSON."""
    data = _load(conf_path)
    rprint(data)

@cmd.command("get")
@click.argument("key", required=False)
@click.option("--file", "conf_path", type=click.Path(path_type=Path), default=DEFAULT_CONF, show_default=True)
def get_value(key: str | None, conf_path: Path):
    """Get a value by key. If no key, print all."""
    data = _load(conf_path)
    if key is None:
        rprint(data)
        return
    rprint(data.get(key))

@cmd.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--file", "conf_path", type=click.Path(path_type=Path), default=DEFAULT_CONF, show_default=True)
def set_value(key: str, value: str, conf_path: Path):
    """
    Set a key to a value. 
    Tip: values are stored as strings; if you want JSON, pass it as JSON:
      bench config set features '{"desk":true,"agent":"on"}'
    """
    data = _load(conf_path)
    # If looks like JSON object/array/true/false/null/number, try to parse
    v = value
    try:
        if value and value[0] in "{[\"tfn-0123456789" or value in ("true","false","null"):
            v = json.loads(value)
    except Exception:
        v = value
    data[key] = v
    _save(conf_path, data)

@cmd.command("edit")
@click.option("--file", "conf_path", type=click.Path(path_type=Path), default=DEFAULT_CONF, show_default=True)
def edit(conf_path: Path):
    """Open the config in your editor ($EDITOR on *nix; Notepad on Windows)."""
    conf_path.parent.mkdir(parents=True, exist_ok=True)
    if not conf_path.exists():
        _save(conf_path, {})
    if os.name == "nt":
        subprocess.run(["notepad.exe", str(conf_path)])
    else:
        editor = os.environ.get("EDITOR", "vi")
        subprocess.run(shlex.split(f"{editor} {shlex.quote(str(conf_path))}"))
