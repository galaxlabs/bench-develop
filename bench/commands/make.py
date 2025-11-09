import os, sys, platform, stat
from pathlib import Path
import click
from rich import print as rprint

WORKSPACE_FILES = ["Procfile", "patches.txt"]
WORKSPACE_DIRS  = ["apps", "config", "env", "logs", "sites"]

BAD_WINDOWS_DIRS = {r"C:\Windows", r"C:\Windows\System32"}
BAD_POSIX_DIRS   = {"/", "/root", "/var", "/etc"}

def _bad_location(p: Path) -> bool:
    p = p.resolve()
    if platform.system() == "Windows":
        return any(str(p).lower() == x.lower() for x in BAD_WINDOWS_DIRS)
    return str(p) in BAD_POSIX_DIRS

@click.group(help="Scaffold workspaces, sites, and apps.")
def cmd():
    pass

@cmd.command("workspace")
@click.argument("path", required=False, default=".")
@click.option("--py", "py_exe", default=None,
              help="Python executable to use for the venv (e.g. 'py -3.12' on Windows).")
@click.option("--auto-cd/--no-auto-cd", default=False,
              help="Print a ready-to-paste command to cd into the workspace.")
@click.option("--no-venv", is_flag=True, default=False,
              help="Skip creating local venv (env/).")
def make_workspace(path, py_exe, auto_cd, no_venv):
    """Create a bench-style workspace (apps/, env/, sites/, logs/, config/ ...)."""
    dest = Path(path).resolve()
    if _bad_location(dest):
        raise click.ClickException(
            f"Refusing to init here: {dest}\n"
            "Pick a user folder (e.g. C:\\Users\\you\\projects or ~/projects)."
        )
    dest.mkdir(parents=True, exist_ok=True)

    for d in WORKSPACE_DIRS: (dest / d).mkdir(parents=True, exist_ok=True)
    for f in WORKSPACE_FILES: (dest / f).touch(exist_ok=True)

    (dest / "Procfile").write_text(
        "web: python manage.py runserver 0.0.0.0:8000\n"
        "worker: echo worker (stub)\n"
    )

    rprint(f"[bold green]Workspace ready:[/bold green] {dest}")
    rprint("• " + "  • ".join(WORKSPACE_DIRS + WORKSPACE_FILES))

    if not no_venv:
        _create_venv(dest, py_exe)
        _write_enter_scripts(dest)
        _print_activate_hints(dest)

    if auto_cd:
        if platform.system() == "Windows":
            rprint(f"[cyan]PowerShell:[/cyan]  Push-Location '{dest}'")
        else:
            rprint(f"[cyan]bash/zsh :[/cyan]  cd '{dest}'")

def _create_venv(root: Path, py_exe: str | None):
    env_dir = root / "env"
    if (env_dir / "Scripts").exists() or (env_dir / "bin").exists():
        rprint("[yellow]env/ already exists; skipping venv creation[/yellow]")
        return

    # choose python
    if py_exe:
        py_cmd = py_exe.split()
    else:
        py_cmd = ["py", "-3"] if platform.system() == "Windows" else ["python3"]

    rprint(f"[blue]Creating venv:[/blue] {env_dir}")
    rc = os.spawnvp(os.P_WAIT, py_cmd[0], py_cmd + ["-m", "venv", str(env_dir)])
    if rc != 0:
        raise click.ClickException("Failed to create virtual environment.")

    pip = env_dir / ("Scripts/pip.exe" if platform.system() == "Windows" else "bin/pip")
    os.spawnv(os.P_WAIT, str(pip), [str(pip), "install", "--upgrade", "pip", "wheel", "setuptools"])
    rprint("[green]venv ready.[/green]")

def _write_enter_scripts(root: Path):
    """Create helper scripts to enter an activated shell (cross-platform)."""
    env = root / "env"

    if platform.system() == "Windows":
        # CMD
        enter_bat = root / "enter.bat"
        enter_bat.write_text(
            "@echo off\r\n"
            "setlocal\r\n"
            "cd /d %~dp0\r\n"
            "if not exist env\\Scripts\\activate.bat (\r\n"
            "  echo venv missing: env\\Scripts\\activate.bat\r\n"
            "  exit /b 1\r\n"
            ")\r\n"
            "call env\\Scripts\\activate.bat\r\n"
            "cmd /K\r\n"
        )

        # PowerShell (opens a new activated session)
        enter_ps1 = root / "enter.ps1"
        enter_ps1.write_text(
            "$here = Split-Path -Parent $MyInvocation.MyCommand.Path\n"
            "Set-Location $here\n"
            "if (!(Test-Path \"$here/env/Scripts/Activate.ps1\")) { "
            "Write-Error 'venv missing: env/Scripts/Activate.ps1'; exit 1 }\n"
            ". \"$here/env/Scripts/Activate.ps1\"\n"
            "Write-Host 'Activated. Type exit to leave.' -ForegroundColor Green\n"
            "powershell -NoExit\n"
        )
    else:
        # POSIX shell
        enter_sh = root / "enter.sh"
        enter_sh.write_text(
            "#!/usr/bin/env bash\n"
            "cd \"$(dirname \"$0\")\" || exit 1\n"
            "if [ ! -f env/bin/activate ]; then\n"
            "  echo 'venv missing: env/bin/activate' >&2; exit 1; fi\n"
            "source env/bin/activate\n"
            "exec \"${SHELL:-bash}\"\n"
        )
        enter_sh.chmod(enter_sh.stat().st_mode | stat.S_IXUSR)

def _print_activate_hints(root: Path):
    if platform.system() == "Windows":
        rprint("[cyan]Activate (CMD):[/cyan]      " + str(root / "enter.bat"))
        rprint("[cyan]Activate (PowerShell):[/cyan]  " + str(root / "enter.ps1"))
        rprint("[cyan]Manual activation (PS):[/cyan]  " + str(root / "env/Scripts/Activate.ps1"))
    else:
        rprint("[cyan]Activate:[/cyan]  source env/bin/activate")
        rprint("[cyan]Or run:[/cyan]    ./enter.sh")

# # bench/commands/make.py
# import os
# import sys
# from pathlib import Path
# import click
# from rich import print as rprint

# DANGEROUS_POSIX = {"/", "/root", "/usr", "/usr/local", "/etc", "/var"}
# DANGEROUS_WIN   = {"C:\\", "C:\\Windows", "C:\\Windows\\System32"}

# @click.group(help="Scaffold workspaces, sites, and apps.")
# def cmd():
#     pass

# def _is_dangerous(path: Path) -> bool:
#     p = str(path.resolve())
#     if os.name == "nt":
#         p = p.replace("/", "\\")
#         return any(p.lower() == d.lower() or p.lower().startswith(d.lower()+"\\") for d in DANGEROUS_WIN)
#     return p in DANGEROUS_POSIX

# @cmd.command("workspace")
# @click.argument("path", required=False, default=".")
# @click.option("--force", is_flag=True, help="Allow initializing in risky directories.")
# def make_workspace(path: str, force: bool):
#     """Create a bench-like workspace skeleton (apps/, env/, config/, logs/, sites/)."""
#     root = Path(path).resolve()
#     if not force and _is_dangerous(root):
#         rprint(f"[red]Refusing to init in risky location:[/] {root}\nUse [yellow]--force[/] to override.")
#         sys.exit(2)

#     (root / "apps").mkdir(parents=True, exist_ok=True)
#     (root / "env").mkdir(parents=True, exist_ok=True)
#     (root / "config").mkdir(parents=True, exist_ok=True)
#     (root / "logs").mkdir(parents=True, exist_ok=True)
#     (root / "sites").mkdir(parents=True, exist_ok=True)

#     procfile = root / "Procfile"
#     if not procfile.exists():
#         procfile.write_text("web: python manage.py runserver 0.0.0.0:8000\n")
#     patches = root / "patches.txt"
#     if not patches.exists():
#         patches.write_text("# patches (one per line)\n")

#     rprint(f"[green]Workspace ready:[/] {root}")
#     rprint("• apps/  • env/  • config/  • logs/  • sites/  • Procfile  • patches.txt")

# @cmd.command("create-app")
# @click.argument("name")
# @click.option("--apps-dir", default="apps", help="Where to create the app package.")
# def create_app(name: str, apps_dir: str):
#     """Create a bare Python app package in apps/<name>."""
#     base = Path(apps_dir).resolve()
#     pkg = base / name
#     pkg.mkdir(parents=True, exist_ok=True)
#     (pkg / "__init__.py").write_text(f'__all__ = []\n__version__ = "0.0.1"\n')
#     (pkg / "README.md").write_text(f"# {name}\n\nGenerated by bench make create-app\n")
#     rprint(f"[green]App created:[/] {pkg}")

# @cmd.command("new-site")
# @click.argument("sitename")
# @click.option("--sites-dir", default="sites", help="Parent directory for sites.")
# def new_site(sitename: str, sites_dir: str):
#     """Create a site folder (no framework opinion yet; just scaffolding)."""
#     root = Path(sites_dir).resolve()
#     site = root / sitename
#     (site / "backend").mkdir(parents=True, exist_ok=True)
#     (site / "assets").mkdir(parents=True, exist_ok=True)
#     (site / "config").mkdir(parents=True, exist_ok=True)
#     (site / "logs").mkdir(parents=True, exist_ok=True)
#     (site / "README.md").write_text(f"# Site: {sitename}\n")
#     rprint(f"[green]Site created:[/] {site}")
