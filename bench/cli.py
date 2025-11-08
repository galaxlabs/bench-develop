# bench/cli.py
import os
import sys
import platform
import importlib
import click
from rich import print as rprint

CTX = {"help_option_names": ["-h", "--help"]}

def _try_add(group: click.Group, module_path: str, name: str):
    """Attempt to import a command group at module_path and add as subcommand."""
    try:
        mod = importlib.import_module(module_path)
        cmd = getattr(mod, "cmd", None)
        if isinstance(cmd, click.core.BaseCommand):
            group.add_command(cmd, name=name)
        else:
            rprint(f"[yellow]warn:[/] {module_path} has no exported Click command `cmd`")
    except ModuleNotFoundError:
        # Silent: command not available yet (OK during early scaffolding)
        pass
    except Exception as e:
        rprint(f"[red]error:[/] failed loading {module_path}: {e}")

@click.group(context_settings=CTX)
@click.version_option(package_name="bench")
def main():
    """Bench CLI (Orbit) – workspace/site/app manager."""
    # Nothing to do here; subcommands are registered below.

@main.command("doctor")
def doctor():
    """Inspect the current workspace and Python environment."""
    rprint("[bold]Bench Doctor[/]")
    rprint(f"- Python : {sys.version.split()[0]}")
    rprint(f"- Platform: {platform.platform()}")
    rprint(f"- Executable: {sys.executable}")
    rprint(f"- CWD     : {os.getcwd()}")
    venv = os.environ.get("VIRTUAL_ENV")
    rprint(f"- VENV    : {venv or '—'}")
    path_head = os.environ.get("PATH", "").split(os.pathsep)[:5]
    rprint(f"- PATH[0:5]: {path_head}")

@main.command("hello")
def hello():
    """Quick sanity check."""
    rprint("[bold green]Bench is wired correctly![/] 🎉")

# Dynamically plug in subcommand groups (only if present)
_try_add(main, "bench.commands.make",   "make")     # bench make ...
_try_add(main, "bench.commands.install","install")  # bench install ...
_try_add(main, "bench.commands.update", "update")   # bench update ...
_try_add(main, "bench.commands.setup",  "setup")    # bench setup ...
_try_add(main, "bench.commands.config", "config")   # bench config ...
_try_add(main, "bench.commands.git",    "git")      # bench git ...
_try_add(main, "bench.commands.utils",  "utils")    # bench utils ...

if __name__ == "__main__":
    main()

# ## Activate venv
# {"." if IS_WIN else "source"} {"Activate.ps1" if IS_WIN else "./activate.sh"}
# """, encoding="utf-8")

# # ---------- DB UTIL ----------

# def db_choice_prompt(non_interactive: bool = False, db: str | None = None) -> str:
#     allowed = ["sqlite", "mysql", "mariadb", "postgres"]
#     if non_interactive and db:
#         if db not in allowed:
#             raise SystemExit(f"Invalid db '{db}'. Choose from: {allowed}")
#         return db
#     rprint("[bold]Database type?[/] [sqlite/mysql/mariadb/postgres] (default: sqlite)")
#     while True:
#         ans = (db or input("> ").strip().lower() or "sqlite")
#         if ans in allowed:
#             return ans
#         rprint(f"[red]Invalid[/]. Choose one of: {allowed}")

# def ensure_db_driver(ws: Path, db: str):
#     # install appropriate driver (best-effort)
#     if db == "sqlite":
#         return
#     if db == "postgres":
#         pip_install(ws, "psycopg[binary]>=3.2")
#     else:
#         # mysql/mariadb: prefer mysqlclient; fallback PyMySQL if build fails
#         try:
#             pip_install(ws, "mysqlclient>=2.2")
#         except subprocess.CalledProcessError:
#             rprint("[yellow]mysqlclient build failed; falling back to PyMySQL[/]")
#             pip_install(ws, "PyMySQL>=1.1")

# def build_database_url(db: str, sitename: str) -> str:
#     if db == "sqlite":
#         return f"sqlite:///sites/{sitename}/{sitename}.sqlite3"
#     if db in ("mysql", "mariadb"):
#         host = input("DB host [127.0.0.1]: ").strip() or "127.0.0.1"
#         port = input("DB port [3306]: ").strip() or "3306"
#         name = input(f"Database name [{sitename}]: ").strip() or sitename
#         user = input("DB user [root]: ").strip() or "root"
#         pwd  = input("DB password: ").strip()
#         scheme = "mysql" if db == "mysql" else "mariadb"
#         return f"{scheme}://{user}:{pwd}@{host}:{port}/{name}"
#     if db == "postgres":
#         host = input("DB host [127.0.0.1]: ").strip() or "127.0.0.1"
#         port = input("DB port [5432]: ").strip() or "5432"
#         name = input(f"Database name [{sitename}]: ").strip() or sitename
#         user = input("DB user [postgres]: ").strip() or "postgres"
#         pwd  = input("DB password: ").strip()
#         return f"postgresql://{user}:{pwd}@{host}:{port}/{name}"
#     raise SystemExit("Unsupported db")

# # ---------- DJANGO SITE SCAFFOLD ----------

# DJANGO_SETTINGS = """\
# import os
# from pathlib import Path
# import dj_database_url

# BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret")
# DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
# ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")

# INSTALLED_APPS = [
#     "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
#     "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
# ]

# MIDDLEWARE = [
#     "django.middleware.security.SecurityMiddleware",
#     "django.contrib.sessions.middleware.SessionMiddleware",
#     "django.middleware.common.CommonMiddleware",
#     "django.middleware.csrf.CsrfViewMiddleware",
#     "django.contrib.auth.middleware.AuthenticationMiddleware",
#     "django.contrib.messages.middleware.MessageMiddleware",
#     "django.middleware.clickjacking.XFrameOptionsMiddleware",
# ]

# ROOT_URLCONF = "config.urls"
# TEMPLATES = [{
#     "BACKEND": "django.template.backends.django.DjangoTemplates",
#     "DIRS": [BASE_DIR / "templates"],
#     "APP_DIRS": True,
#     "OPTIONS": {
#         "context_processors": [
#             "django.template.context_processors.debug",
#             "django.template.context_processors.request",
#             "django.contrib.auth.context_processors.auth",
#             "django.contrib.messages.context_processors.messages",
#         ],
#     },
# }]
# WSGI_APPLICATION = "config.wsgi.application"

# DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/db.sqlite3")
# DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)}

# STATIC_URL = "static/"
# STATIC_ROOT = BASE_DIR / "staticfiles"
# DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# """

# DJANGO_URLS = """\
# from django.contrib import admin
# from django.urls import path

# urlpatterns = [
#     path("admin/", admin.site.urls),
# ]
# """

# DJANGO_WSGI = """\
# import os
# from django.core.wsgi import get_wsgi_application
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
# application = get_wsgi_application()
# """

# DJANGO_MANAGE = """\
# #!/usr/bin/env python
# import os, sys
# if __name__ == "__main__":
#     os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
#     from django.core.management import execute_from_command_line
#     execute_from_command_line(sys.argv)
# """

# def scaffold_site(ws: Path, sitename: str, database_url: str):
#     site_root = ws / "sites" / sitename
#     backend = site_root / "backend" / "config"
#     (backend).mkdir(parents=True, exist_ok=True)
#     (site_root / "backend" / "templates").mkdir(parents=True, exist_ok=True)
#     (site_root / "logs").mkdir(parents=True, exist_ok=True)

#     # manage.py
#     manage = site_root / "backend" / "manage.py"
#     manage.write_text(DJANGO_MANAGE, encoding="utf-8")
#     if not IS_WIN:
#         os.chmod(manage, 0o755)

#     # config package
#     (backend / "__init__.py").write_text("", encoding="utf-8")
#     (backend / "settings.py").write_text(DJANGO_SETTINGS, encoding="utf-8")
#     (backend / "urls.py").write_text(DJANGO_URLS, encoding="utf-8")
#     (backend / "wsgi.py").write_text(DJANGO_WSGI, encoding="utf-8")

#     # .env
#     (site_root / ".env").write_text(f"DJANGO_DEBUG=1\nDATABASE_URL={database_url}\n", encoding="utf-8")

#     # site marker
#     (site_root / "site_config.json").write_text(json.dumps({"database_url": database_url}, indent=2), encoding="utf-8")

# # ---------- COMMANDS ----------

# @app.command()
# def init(
#     path: str = typer.Argument(None, help="Workspace path (default: current directory)"),
#     py: str = typer.Option(None, "--py", help="Python executable to create venv (e.g. python3.12)"),
#     cd: bool = typer.Option(False, "--cd", help="Echo shell command to cd + activate after init"),
#     force: bool = typer.Option(False, "--force", help="Allow unsafe locations"),
# ):
#     """Create an obench workspace (bench-like skeleton + venv)."""
#     ws = Path(path or os.getcwd()).expanduser()
#     if is_admin():
#         rprint("[yellow]Warning:[/] running as Administrator/root. Prefer a normal user.")
#     if is_unsafe_path(ws) and not force:
#         rprint(f"[red]Refusing unsafe path[/] '{ws}'. Use a dev folder (e.g. $HOME/dev) or pass --force.")
#         raise typer.Exit(2)

#     ws.mkdir(parents=True, exist_ok=True)
#     ensure_workspace_skeleton(ws)
#     ensure_venv(ws, py)
#     write_activation_helpers(ws)
#     write_readme(ws)
#     # install baseline deps used by generated site(s)
#     pip_install(ws, "Django>=5.2,<6.0", "dj-database-url>=2.2")

#     rprint(f"[green]Workspace ready.[/]\nPath : {ws}")
#     if cd:
#         if IS_WIN:
#             rprint(f'Paste to switch now:\n[bold]cd "{ws}" ; . .\\Activate.ps1[/bold]')
#         else:
#             rprint(f'Paste to switch now:\n[bold]cd "{ws}" && source ./activate.sh[/bold]')

# @app.command("new-site")
# def new_site(
#     sitename: str = typer.Argument(..., help="Site name (folder under sites/)"),
#     db: str = typer.Option(None, "--db", help="sqlite|mysql|mariadb|postgres"),
#     non_interactive: bool = typer.Option(False, "--non-interactive", help="Do not prompt (requires --db)"),
# ):
#     """Create a new site (Django project) with DB config and drivers."""
#     ws = Path(os.getcwd()).expanduser()
#     if not (ws / ".obench" / "state.json").exists():
#         rprint("[red]Not an obench workspace[/]. Run: obench init")
#         raise typer.Exit(2)

#     choice = db_choice_prompt(non_interactive=non_interactive, db=db)
#     ensure_db_driver(ws, choice)
#     database_url = build_database_url(choice, sitename)
#     scaffold_site(ws, sitename, database_url)

#     # migrate
#     py = str(venv_python(ws))
#     manage = ws / "sites" / sitename / "backend" / "manage.py"
#     env = os.environ.copy()
#     env["DATABASE_URL"] = database_url
#     subprocess.check_call([py, str(manage), "migrate"], env=env)

#     # mark as current if none set
#     current = ws / "sites" / "current"
#     if not current.exists():
#         try:
#             current.symlink_to(ws / "sites" / sitename, target_is_directory=True)
#         except Exception:
#             # fallback: copy a pointer file
#             (ws / "sites" / "CURRENT.txt").write_text(sitename, encoding="utf-8")

#     rprint(f"[green]Site created:[/] sites/{sitename}\nDB   : {database_url}")

# @app.command("create-app")
# def create_app(appname: str = typer.Argument(..., help="App name (Python package under apps/)")):
#     """Scaffold a bare Python package under apps/<appname>/"""
#     ws = Path(os.getcwd()).expanduser()
#     target = ws / "apps" / appname
#     target.mkdir(parents=True, exist_ok=True)
#     (target / "__init__.py").write_text("# app package\n", encoding="utf-8")
#     (target / "models.py").write_text("# your models here\n", encoding="utf-8")
#     (target / "views.py").write_text("# your views here\n", encoding="utf-8")
#     (target / "admin.py").write_text("# your admin here\n", encoding="utf-8")
#     rprint(f"[green]App scaffolded:[/] apps/{appname}")

# @app.command()
# def runserver(
#     site: str = typer.Option("current", "--site", help="Site to run (default: current)"),
#     addr: str = typer.Option("127.0.0.1:8000", "--addr", help="Bind address"),
# ):
#     """Run Django dev server for a site."""
#     ws = Path(os.getcwd()).expanduser()
#     site_dir = ws / "sites" / (site if site != "current" else (Path("current")))
#     # resolve 'current' symlink if possible
#     if site == "current" and site_dir.is_symlink():
#         site_dir = site_dir.resolve()
#     manage = site_dir / "backend" / "manage.py"
#     env = os.environ.copy()
#     # load .env if present
#     env_path = site_dir / ".env"
#     if env_path.exists():
#         for line in env_path.read_text(encoding="utf-8").splitlines():
#             if not line.strip() or line.strip().startswith("#"): continue
#             k, _, v = line.partition("=")
#             env[k.strip()] = v.strip()
#     py = str(venv_python(ws))
#     subprocess.check_call([py, str(manage), "runserver", addr], env=env)

# @app.command()
# def exec(
#     cmd: str = typer.Argument(..., help="Command to run inside venv (quote it)"),
# ):
#     """Run any command with the workspace venv on PATH."""
#     ws = Path(os.getcwd()).expanduser()
#     py = venv_python(ws)
#     if not py.exists():
#         rprint("[red]Venv missing.[/] Run: obench init")
#         raise typer.Exit(2)
#     bindir = py.parent
#     env = os.environ.copy()
#     env["PATH"] = str(bindir) + os.pathsep + env.get("PATH", "")
#     # shell=True to allow compound commands on all OS
#     subprocess.call(cmd, shell=True, env=env)

# @app.command()
# def shell():
#     """Open a shell with venv activated (new window/interactive)."""
#     ws = Path(os.getcwd()).expanduser()
#     if IS_WIN:
#         act = ws / "Activate.ps1"
#         if not act.exists():
#             write_activation_helpers(ws)
#         subprocess.call(["powershell", "-NoExit", "-File", str(act)])
#     else:
#         act = ws / "activate.sh"
#         if not act.exists():
#             write_activation_helpers(ws)
#         subprocess.call(["bash", "-i", "-c", f'source "{act}"; exec bash -i'])

# @app.command()
# def doctor():
#     """Inspect the current workspace/venv."""
#     ws = Path(os.getcwd()).expanduser()
#     py = venv_python(ws)
#     rprint(f"Workspace : {ws}")
#     if py.exists():
#         rprint(f"Venv      : [green]OK[/] -> {py}")
#         subprocess.call([str(py), "-V"])
#         subprocess.call([str(py), "-m", "pip", "list"])
#     else:
#         rprint(f"Venv      : [red]MISSING[/] -> {py}")
#         raise typer.Exit(2)
