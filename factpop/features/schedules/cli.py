from __future__ import annotations

from typing import Optional

import typer

from factpop.features.schedules.errors import (
    InvalidTimeFormatError,
    TimeAlreadyExistsError,
    TimeNotFoundError,
)
from factpop.features.schedules.service import ScheduleService
from factpop.features.settings.repository import TinyDBSettingsRepository
from factpop.features.settings.service import SettingsService
from factpop.shared.storage.tinydb_factory import get_db

app = typer.Typer(help="Manage popup schedule.")
random_app = typer.Typer(help="Manage random-interval mode.")
app.add_typer(random_app, name="random")


def _service() -> ScheduleService:
    db = get_db()
    settings = SettingsService(TinyDBSettingsRepository(db.table("app_config")))
    return ScheduleService(settings)


@app.command("add")
def add(time: str = typer.Argument(..., help="Time in HH:MM format (24h)")) -> None:
    """Add a specific daily popup time."""
    try:
        _service().add_time(time)
        typer.echo(f"OK: Time '{time}' added to schedule.")
    except (InvalidTimeFormatError, TimeAlreadyExistsError) as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)


@app.command("remove")
def remove(time: str = typer.Argument(..., help="Time in HH:MM format")) -> None:
    """Remove a specific daily popup time."""
    try:
        _service().remove_time(time)
        typer.echo(f"OK: Time '{time}' removed from schedule.")
    except TimeNotFoundError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)


@app.command("list")
def list_times() -> None:
    """Show all configured popup times."""
    times = _service().list_times()
    config = _service().get_random_config()
    if not times and not config.enabled:
        typer.echo("No schedule configured. Use 'schedules add HH:MM' or 'schedules random enable'.")
        return
    if times:
        typer.echo("Specific times:")
        for t in times:
            typer.echo(f"  {t}")
    if config.enabled:
        typer.echo(
            f"Random mode: ON  ({config.start} - {config.end}, max {config.max_per_day}/day)"
        )
    else:
        typer.echo("Random mode: OFF")


@random_app.command("enable")
def random_enable(
    start: str = typer.Option("08:00", help="Window start time (HH:MM)"),
    end: str = typer.Option("22:00", help="Window end time (HH:MM)"),
    max: int = typer.Option(3, help="Max popups per day"),
) -> None:
    """Enable random-interval popup mode."""
    try:
        _service().enable_random(start=start, end=end, max_per_day=max)
        typer.echo(f"OK: Random mode enabled ({start} - {end}, max {max}/day).")
    except InvalidTimeFormatError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)


@random_app.command("disable")
def random_disable() -> None:
    """Disable random-interval popup mode."""
    _service().disable_random()
    typer.echo("OK: Random mode disabled.")
