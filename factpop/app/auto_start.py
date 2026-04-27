from __future__ import annotations

import sys
from pathlib import Path


def _startup_folder() -> Path:
    """Return the Windows Startup folder for the current user."""
    import os
    appdata = os.environ.get("APPDATA", "")
    return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def get_startup_script_path() -> Path:
    """Return the path where FactPop's startup VBS script would live."""
    return _startup_folder() / "FactPop.vbs"


def build_startup_script_content(python_exe: Path, project_dir: Path) -> str:
    """Return a VBScript that launches FactPop silently on Windows startup.

    Uses pythonw.exe (no console window) and sets the working directory
    to project_dir so .env and relative paths resolve correctly.
    """
    return (
        'Set WShell = CreateObject("WScript.Shell")\n'
        f'WShell.CurrentDirectory = "{project_dir}"\n'
        f'WShell.Run """{python_exe}"" -m factpop", 0, False\n'
        "Set WShell = Nothing\n"
    )


def is_auto_start_configured() -> bool:
    """Return True if the FactPop startup script already exists."""
    return get_startup_script_path().exists()


def install_auto_start() -> Path:
    """Write the startup VBS script. Returns the script path."""
    python_exe = Path(sys.executable).parent / "pythonw.exe"
    project_dir = Path(__file__).resolve().parents[2]
    content = build_startup_script_content(python_exe, project_dir)
    script = get_startup_script_path()
    script.write_text(content, encoding="utf-8")
    return script


def remove_auto_start() -> bool:
    """Delete the startup script. Returns True if it existed and was deleted."""
    script = get_startup_script_path()
    if script.exists():
        script.unlink()
        return True
    return False
