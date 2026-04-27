"""Tabbed settings window — manual QA only (tkinter, no automated tests)."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from factpop.features.history.repository import TinyDBFactHistoryRepository
from factpop.features.history.service import FactHistoryService
from factpop.features.schedules.service import ScheduleService
from factpop.features.settings.repository import TinyDBSettingsRepository
from factpop.features.settings.service import SettingsService
from factpop.features.topics.repository import TinyDBTopicRepository
from factpop.features.topics.service import TopicService
from factpop.shared.storage.tinydb_factory import get_db
from factpop.features.schedules.errors import (
    InvalidTimeFormatError, TimeAlreadyExistsError, TimeNotFoundError,
)
from factpop.features.topics.errors import (
    DuplicateTopicError, EmptyTopicNameError, TopicNotFoundError,
)

_BG = "#1e1e2e"
_FG = "#cdd6f4"
_ENTRY_BG = "#313244"
_BTN_BG = "#89b4fa"
_BTN_FG = "#1e1e2e"
_FONT = ("Segoe UI", 10)
_FONT_BOLD = ("Segoe UI", 10, "bold")


def open_settings_window() -> None:
    """Open the tabbed settings window. Blocks until closed."""
    db = get_db()
    topic_svc = TopicService(TinyDBTopicRepository(db.table("topics")))
    settings_svc = SettingsService(TinyDBSettingsRepository(db.table("app_config")))
    history_svc = FactHistoryService(TinyDBFactHistoryRepository(db.table("fact_history")))
    schedule_svc = ScheduleService(settings_svc)

    root = tk.Tk()
    root.title("FactPop — Settings")
    root.configure(bg=_BG)
    root.resizable(False, False)
    root.attributes("-topmost", True)

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=8, pady=8)

    _build_topics_tab(notebook, topic_svc)
    _build_schedule_tab(notebook, schedule_svc, settings_svc)
    _build_history_tab(notebook, history_svc)

    # Center
    root.update_idletasks()
    w, h = root.winfo_reqwidth(), root.winfo_reqheight()
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"{max(w, 480)}x{max(h, 340)}+{(sw - max(w, 480)) // 2}+{(sh - max(h, 340)) // 2}")
    root.mainloop()
    root.destroy()


def _build_topics_tab(notebook: ttk.Notebook, topic_svc: TopicService) -> None:
    frame = tk.Frame(notebook, bg=_BG)
    notebook.add(frame, text="Topics")

    listbox_frame = tk.Frame(frame, bg=_BG)
    listbox_frame.pack(fill="both", expand=True, padx=8, pady=(8, 4))

    listbox = tk.Listbox(listbox_frame, bg=_ENTRY_BG, fg=_FG, font=_FONT,
                         selectbackground="#45475a", activestyle="none", height=10)
    listbox.pack(side="left", fill="both", expand=True)
    scrollbar = tk.Scrollbar(listbox_frame, command=listbox.yview)
    scrollbar.pack(side="right", fill="y")
    listbox.configure(yscrollcommand=scrollbar.set)

    def refresh():
        listbox.delete(0, tk.END)
        for t in topic_svc.list_all():
            status = "[active]  " if t.active else "[inactive]"
            listbox.insert(tk.END, f"{status}  {t.name}")

    refresh()

    add_frame = tk.Frame(frame, bg=_BG)
    add_frame.pack(fill="x", padx=8, pady=(0, 4))
    entry = tk.Entry(add_frame, bg=_ENTRY_BG, fg=_FG, font=_FONT, insertbackground=_FG)
    entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

    def _add():
        name = entry.get().strip()
        try:
            topic_svc.create(name)
            entry.delete(0, tk.END)
            refresh()
        except (EmptyTopicNameError, DuplicateTopicError) as exc:
            messagebox.showerror("Error", str(exc), parent=notebook)

    def _toggle():
        sel = listbox.curselection()
        if not sel:
            return
        text = listbox.get(sel[0])
        name = text.split("  ", 1)[-1].strip()
        topics = topic_svc.list_all()
        topic = next((t for t in topics if t.name == name), None)
        if topic is None:
            return
        try:
            if topic.active:
                _, is_last = topic_svc.deactivate(name)
                if is_last:
                    messagebox.showwarning("Warning",
                        "No active topics remain. Popups won't fire.", parent=notebook)
            else:
                topic_svc.activate(name)
            refresh()
        except TopicNotFoundError as exc:
            messagebox.showerror("Error", str(exc), parent=notebook)

    def _delete():
        sel = listbox.curselection()
        if not sel:
            return
        text = listbox.get(sel[0])
        name = text.split("  ", 1)[-1].strip()
        if messagebox.askyesno("Confirm", f"Delete topic '{name}'?", parent=notebook):
            try:
                topic_svc.delete(name)
                refresh()
            except TopicNotFoundError as exc:
                messagebox.showerror("Error", str(exc), parent=notebook)

    btn_frame = tk.Frame(frame, bg=_BG)
    btn_frame.pack(fill="x", padx=8, pady=(0, 8))
    tk.Button(add_frame, text="Add", bg=_BTN_BG, fg=_BTN_FG, font=_FONT,
              relief="flat", command=_add).pack(side="left")
    tk.Button(btn_frame, text="Toggle Active", bg="#a6e3a1", fg=_BTN_FG, font=_FONT,
              relief="flat", command=_toggle).pack(side="left", padx=(0, 6))
    tk.Button(btn_frame, text="Delete", bg="#f38ba8", fg=_BTN_FG, font=_FONT,
              relief="flat", command=_delete).pack(side="left")


def _build_schedule_tab(notebook: ttk.Notebook, schedule_svc: ScheduleService,
                        settings_svc: SettingsService) -> None:
    frame = tk.Frame(notebook, bg=_BG)
    notebook.add(frame, text="Schedule")

    tk.Label(frame, text="Specific times (HH:MM):", font=_FONT_BOLD,
             bg=_BG, fg=_FG).pack(anchor="w", padx=10, pady=(10, 2))

    listbox = tk.Listbox(frame, bg=_ENTRY_BG, fg=_FG, font=_FONT,
                         selectbackground="#45475a", activestyle="none", height=5)
    listbox.pack(fill="x", padx=10, pady=(0, 4))

    def refresh_times():
        listbox.delete(0, tk.END)
        for t in schedule_svc.list_times():
            listbox.insert(tk.END, t)

    refresh_times()

    time_row = tk.Frame(frame, bg=_BG)
    time_row.pack(fill="x", padx=10, pady=(0, 6))
    time_entry = tk.Entry(time_row, bg=_ENTRY_BG, fg=_FG, font=_FONT,
                          insertbackground=_FG, width=8)
    time_entry.pack(side="left", padx=(0, 6))

    def _add_time():
        t = time_entry.get().strip()
        try:
            schedule_svc.add_time(t)
            time_entry.delete(0, tk.END)
            refresh_times()
        except (InvalidTimeFormatError, TimeAlreadyExistsError) as exc:
            messagebox.showerror("Error", str(exc), parent=notebook)

    def _remove_time():
        sel = listbox.curselection()
        if not sel:
            return
        t = listbox.get(sel[0])
        try:
            schedule_svc.remove_time(t)
            refresh_times()
        except TimeNotFoundError as exc:
            messagebox.showerror("Error", str(exc), parent=notebook)

    tk.Button(time_row, text="Add", bg=_BTN_BG, fg=_BTN_FG, font=_FONT,
              relief="flat", command=_add_time).pack(side="left", padx=(0, 4))
    tk.Button(time_row, text="Remove", bg="#f38ba8", fg=_BTN_FG, font=_FONT,
              relief="flat", command=_remove_time).pack(side="left")

    # Random mode
    cfg = settings_svc.get_random_config()
    random_var = tk.BooleanVar(value=cfg.enabled)

    def _toggle_random():
        if random_var.get():
            schedule_svc.enable_random()
        else:
            schedule_svc.disable_random()

    tk.Checkbutton(frame, text="Random mode (08:00 - 22:00, max 3/day)",
                   variable=random_var, command=_toggle_random,
                   bg=_BG, fg=_FG, selectcolor=_ENTRY_BG, activebackground=_BG,
                   font=_FONT).pack(anchor="w", padx=10, pady=(4, 4))

    # Quiz toggle
    quiz_var = tk.BooleanVar(value=settings_svc.is_quiz_enabled())

    def _toggle_quiz():
        settings_svc.set_quiz_enabled(quiz_var.get())

    tk.Checkbutton(frame, text="Enable quizzes",
                   variable=quiz_var, command=_toggle_quiz,
                   bg=_BG, fg=_FG, selectcolor=_ENTRY_BG, activebackground=_BG,
                   font=_FONT).pack(anchor="w", padx=10, pady=(0, 8))


def _build_history_tab(notebook: ttk.Notebook, history_svc: FactHistoryService) -> None:
    frame = tk.Frame(notebook, bg=_BG)
    notebook.add(frame, text="History")

    tk.Label(frame, text="Recent facts (most recent first):", font=_FONT_BOLD,
             bg=_BG, fg=_FG).pack(anchor="w", padx=10, pady=(10, 2))

    text_widget = tk.Text(frame, bg=_ENTRY_BG, fg=_FG, font=("Consolas", 9),
                          wrap="word", state="disabled", height=14)
    text_widget.pack(fill="both", expand=True, padx=10, pady=(0, 4))

    def refresh():
        text_widget.configure(state="normal")
        text_widget.delete("1.0", tk.END)
        records = history_svc.get_recent(limit=30)
        for r in records:
            saved = "[saved] " if r.saved else "        "
            text_widget.insert(tk.END, f"{saved}[{r.topic}] {r.shown_at[:16]}\n")
            text_widget.insert(tk.END, f"        {r.text[:80]}\n\n")
        text_widget.configure(state="disabled")

    refresh()
    tk.Button(frame, text="Refresh", bg=_BTN_BG, fg=_BTN_FG, font=_FONT,
              relief="flat", command=refresh).pack(padx=10, pady=(0, 8))
