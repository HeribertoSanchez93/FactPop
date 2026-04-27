"""Tests for the auto-start utility (pure logic — no OS calls)."""
from pathlib import Path
from unittest.mock import patch

import pytest

from factpop.app.auto_start import (
    build_startup_script_content,
    get_startup_script_path,
    is_auto_start_configured,
)


# ── get_startup_script_path ─────────────────────────────────────────────────

def test_startup_script_path_is_inside_startup_folder(tmp_path: Path) -> None:
    with patch("factpop.app.auto_start._startup_folder", return_value=tmp_path):
        path = get_startup_script_path()
    assert path.parent == tmp_path


def test_startup_script_has_vbs_extension(tmp_path: Path) -> None:
    with patch("factpop.app.auto_start._startup_folder", return_value=tmp_path):
        path = get_startup_script_path()
    assert path.suffix == ".vbs"


def test_startup_script_filename_contains_factpop(tmp_path: Path) -> None:
    with patch("factpop.app.auto_start._startup_folder", return_value=tmp_path):
        path = get_startup_script_path()
    assert "factpop" in path.name.lower() or "FactPop" in path.name


# ── build_startup_script_content ────────────────────────────────────────────

def test_script_content_contains_python_executable() -> None:
    python_exe = Path(r"C:\project\.venv\Scripts\pythonw.exe")
    project_dir = Path(r"C:\project")
    content = build_startup_script_content(python_exe, project_dir)
    assert "pythonw.exe" in content


def test_script_content_contains_factpop_module() -> None:
    python_exe = Path(r"C:\project\.venv\Scripts\pythonw.exe")
    project_dir = Path(r"C:\project")
    content = build_startup_script_content(python_exe, project_dir)
    assert "factpop" in content.lower()


def test_script_content_runs_hidden_no_console_window() -> None:
    python_exe = Path(r"C:\project\.venv\Scripts\pythonw.exe")
    project_dir = Path(r"C:\project")
    content = build_startup_script_content(python_exe, project_dir)
    # VBS script should use WindowStyle 0 (hidden) or similar
    assert "0" in content or "hidden" in content.lower() or "vbHide" in content


def test_script_content_sets_working_directory() -> None:
    python_exe = Path(r"C:\project\.venv\Scripts\pythonw.exe")
    project_dir = Path(r"C:\project")
    content = build_startup_script_content(python_exe, project_dir)
    assert r"C:\project" in content


# ── is_auto_start_configured ─────────────────────────────────────────────────

def test_auto_start_not_configured_when_script_missing(tmp_path: Path) -> None:
    with patch("factpop.app.auto_start._startup_folder", return_value=tmp_path):
        assert is_auto_start_configured() is False


def test_auto_start_configured_when_script_exists(tmp_path: Path) -> None:
    with patch("factpop.app.auto_start._startup_folder", return_value=tmp_path):
        script = get_startup_script_path()
        script.write_text("dummy content")
        assert is_auto_start_configured() is True
