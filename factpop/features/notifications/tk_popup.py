from __future__ import annotations

import tkinter as tk
from typing import Callable

from factpop.features.history.models import FactRecord

_FONT_TOPIC = ("Segoe UI", 11, "bold")
_FONT_BODY = ("Segoe UI", 10)
_FONT_EXAMPLE = ("Consolas", 9)
_BG = "#1e1e2e"
_FG = "#cdd6f4"
_BTN_SAVE = "#a6e3a1"
_BTN_MORE = "#89b4fa"
_BTN_CLOSE = "#6c7086"


class TkPopupDispatcher:
    """Shows a tkinter popup window for each fact.

    Creates a fresh Tk root per call, suitable for CLI --show usage.
    The daemon / Stage 9 scheduler will use a persistent root via root.after().
    """

    def show_fact(
        self,
        record: FactRecord,
        on_save: Callable[[], None],
        on_show_another: Callable[[], None],
    ) -> None:
        show_another_requested = [False]

        root = tk.Tk()
        root.withdraw()  # hide the invisible root window

        popup = tk.Toplevel(root)
        popup.title("FactPop")
        popup.configure(bg=_BG)
        popup.resizable(False, False)
        popup.attributes("-topmost", True)

        # --- topic label ---
        tk.Label(
            popup, text=f"[{record.topic}]",
            font=_FONT_TOPIC, bg=_BG, fg="#89dceb", anchor="w",
        ).pack(fill="x", padx=14, pady=(12, 2))

        # --- fact text ---
        fact_var = tk.StringVar(value=record.text)
        tk.Label(
            popup, textvariable=fact_var,
            font=_FONT_BODY, bg=_BG, fg=_FG,
            wraplength=360, justify="left", anchor="w",
        ).pack(fill="x", padx=14, pady=(0, 6))

        # --- example (if present) ---
        if record.example:
            tk.Label(
                popup, text=record.example,
                font=_FONT_EXAMPLE, bg="#313244", fg="#a6adc8",
                wraplength=360, justify="left", anchor="w",
                relief="flat",
            ).pack(fill="x", padx=14, pady=(0, 8))

        # --- separator ---
        tk.Frame(popup, height=1, bg="#45475a").pack(fill="x", padx=8, pady=(0, 8))

        # --- action buttons ---
        btn_frame = tk.Frame(popup, bg=_BG)
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        def _on_show_another() -> None:
            show_another_requested[0] = True
            popup.destroy()
            root.quit()

        def _on_save() -> None:
            on_save()
            popup.destroy()
            root.quit()

        def _on_close() -> None:
            popup.destroy()
            root.quit()

        tk.Button(btn_frame, text="Show Another", font=_FONT_BODY,
                  bg=_BTN_MORE, fg="#1e1e2e", relief="flat", cursor="hand2",
                  command=_on_show_another).pack(side="left", padx=(0, 6))

        tk.Button(btn_frame, text="Save", font=_FONT_BODY,
                  bg=_BTN_SAVE, fg="#1e1e2e", relief="flat", cursor="hand2",
                  command=_on_save).pack(side="left", padx=(0, 6))

        tk.Button(btn_frame, text="Close", font=_FONT_BODY,
                  bg=_BTN_CLOSE, fg=_FG, relief="flat", cursor="hand2",
                  command=_on_close).pack(side="left")

        popup.protocol("WM_DELETE_WINDOW", _on_close)

        # Center the popup on screen
        popup.update_idletasks()
        w, h = popup.winfo_reqwidth(), popup.winfo_reqheight()
        sw = popup.winfo_screenwidth()
        sh = popup.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        popup.geometry(f"{w}x{h}+{x}+{y}")

        root.mainloop()
        root.destroy()

        if show_another_requested[0]:
            on_show_another()
