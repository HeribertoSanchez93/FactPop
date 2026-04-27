from __future__ import annotations

import logging
import threading
import time

from dotenv import load_dotenv

from factpop.app.bootstrap import bootstrap, shutdown
from factpop.app.lifecycle import instance_lock
from factpop.shared.logging_config import setup_logging
from factpop.shared.storage.tinydb_factory import close_db, get_db, init_db

logger = logging.getLogger(__name__)

_icon_ref = None


def _build_tray_icon(stop_event: threading.Event):
    """Build the pystray tray icon with menu items.

    Runs via run_detached() so pystray's Win32 message loop is in a background
    thread and the main thread stays free to catch KeyboardInterrupt.
    """
    import pystray
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (64, 64), color="#89b4fa")
    draw = ImageDraw.Draw(img)
    draw.rectangle([16, 16, 48, 48], fill="#1e1e2e")

    def on_show_last_fact(_icon, _item):
        from factpop.features.history.repository import TinyDBFactHistoryRepository
        from factpop.features.history.service import FactHistoryService
        from factpop.features.notifications.tk_popup import TkPopupDispatcher

        db = get_db()
        history_svc = FactHistoryService(
            TinyDBFactHistoryRepository(db.table("fact_history"))
        )
        recent = history_svc.get_recent(limit=1)
        if not recent:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo("FactPop", "No facts generated yet.")
            root.destroy()
            return
        record = recent[0]
        dispatcher = TkPopupDispatcher()
        dispatcher.show_fact(
            record,
            on_save=lambda: history_svc.mark_saved(record.id),
            on_show_another=lambda: None,
        )

    def on_open_settings(_icon, _item):
        from factpop.features.settings.tk_settings import open_settings_window
        open_settings_window()

    def on_quit(icon, _item):
        icon.stop()
        stop_event.set()  # wake the main thread so it exits the wait loop

    menu = pystray.Menu(
        pystray.MenuItem("Show Last Fact", on_show_last_fact),
        pystray.MenuItem("Open Settings", on_open_settings),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", on_quit),
    )
    return pystray.Icon("FactPop", img, "FactPop", menu)


def main() -> None:
    load_dotenv()
    setup_logging()
    with instance_lock():
        init_db()
        bootstrap()
        logger.info("FactPop started.")

        _stop_event = threading.Event()

        try:
            global _icon_ref
            _icon_ref = _build_tray_icon(_stop_event)
            logger.info("System tray icon active. Right-click the tray to interact. Press Ctrl+C to stop.")
            _icon_ref.run_detached()  # pystray message loop runs in a background thread
            try:
                while not _stop_event.is_set():
                    time.sleep(0.1)  # Python sleep — interrupted by KeyboardInterrupt on Ctrl+C
            except KeyboardInterrupt:
                logger.info("Ctrl+C received — stopping FactPop.")
                _icon_ref.stop()
        except Exception as exc:
            logger.error("Tray icon failed (%s) — falling back to console mode.", exc)
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
        finally:
            shutdown()
            close_db()
            logger.info("FactPop stopped.")


if __name__ == "__main__":
    main()
