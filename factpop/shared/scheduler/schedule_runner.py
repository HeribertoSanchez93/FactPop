from __future__ import annotations

import logging
import threading
import time
from datetime import datetime
from typing import Callable

import schedule

logger = logging.getLogger(__name__)


class ScheduleRunner:
    """Wraps the `schedule` library with a daemon thread.

    - add_daily: registers a recurring job at HH:MM every day.
    - add_once_at: registers a one-shot job at a specific datetime.
    - start: launches the background thread that runs pending jobs every second.
    - stop: signals the thread to exit and waits for it to finish.
    """

    def __init__(self) -> None:
        self._scheduler = schedule.Scheduler()
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def add_daily(self, time_str: str, callback: Callable, job_id: str = "") -> None:
        self._scheduler.every().day.at(time_str).do(callback).tag(job_id or time_str)

    def add_once_at(self, run_at: datetime, callback: Callable, job_id: str = "") -> None:
        tag = job_id or f"once-{run_at.isoformat()}"

        def _one_shot():
            if datetime.now() >= run_at:
                callback()
                return schedule.CancelJob
            return None

        self._scheduler.every(30).seconds.do(_one_shot).tag(tag)

    def clear_all(self) -> None:
        self._scheduler.clear()

    def start(self) -> None:
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="FactPopScheduler")
        self._thread.start()
        logger.info("Scheduler thread started.")

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5)
        logger.info("Scheduler thread stopped.")

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            self._scheduler.run_pending()
            time.sleep(1)
