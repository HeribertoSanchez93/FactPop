from __future__ import annotations

import typer

from factpop.app.auto_start import (
    install_auto_start,
    is_auto_start_configured,
    remove_auto_start,
)

app = typer.Typer(help="Manage Windows auto-start on login.")


@app.command("install")
def install() -> None:
    """Create a startup script so FactPop launches on Windows login."""
    if is_auto_start_configured():
        typer.echo("Auto-start is already configured.")
        return
    script = install_auto_start()
    typer.echo(f"OK: Auto-start installed at {script}")


@app.command("remove")
def remove() -> None:
    """Remove the Windows startup script."""
    if remove_auto_start():
        typer.echo("OK: Auto-start removed.")
    else:
        typer.echo("Auto-start was not configured.")


@app.command("status")
def autostart_status() -> None:
    """Check whether auto-start is configured."""
    configured = is_auto_start_configured()
    label = "configured" if configured else "not configured"
    typer.echo(f"Auto-start: {label}")
