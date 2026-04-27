from __future__ import annotations

import tkinter as tk
from typing import Callable

from factpop.features.quizzes.models import Quiz

_BG = "#1e1e2e"
_FG = "#cdd6f4"
_BTN_SUBMIT = "#a6e3a1"
_BTN_SKIP = "#6c7086"
_FONT = ("Segoe UI", 10)
_FONT_BOLD = ("Segoe UI", 11, "bold")
_FONT_CODE = ("Consolas", 9)


class TkQuizDispatcher:
    """Shows a tkinter quiz popup — manual QA only (no automated tests)."""

    def show_quiz(
        self,
        quiz: Quiz,
        on_submit: Callable[[int], None],
        on_skip: Callable[[], None],
    ) -> None:
        submitted_index: list[int | None] = [None]
        skipped = [False]

        root = tk.Tk()
        root.withdraw()

        popup = tk.Toplevel(root)
        popup.title("FactPop — Quiz")
        popup.configure(bg=_BG)
        popup.resizable(False, False)
        popup.attributes("-topmost", True)

        # Context: source fact
        tk.Label(
            popup, text=f"[{quiz.source_fact.topic}] — Review",
            font=_FONT_BOLD, bg=_BG, fg="#89dceb", anchor="w",
        ).pack(fill="x", padx=14, pady=(12, 2))

        tk.Label(
            popup, text=quiz.source_fact.text,
            font=_FONT_CODE, bg="#313244", fg="#a6adc8",
            wraplength=360, justify="left", anchor="w",
        ).pack(fill="x", padx=14, pady=(0, 8))

        # Question
        tk.Label(
            popup, text=quiz.question,
            font=_FONT, bg=_BG, fg=_FG,
            wraplength=360, justify="left", anchor="w",
        ).pack(fill="x", padx=14, pady=(0, 6))

        # Radio buttons for options
        selected_var = tk.IntVar(value=-1)
        for i, option in enumerate(quiz.options):
            tk.Radiobutton(
                popup, text=f"{chr(65 + i)}.  {option}",
                variable=selected_var, value=i,
                bg=_BG, fg=_FG, selectcolor="#313244",
                activebackground=_BG, activeforeground=_FG,
                font=_FONT, anchor="w",
            ).pack(fill="x", padx=20, pady=1)

        tk.Frame(popup, height=1, bg="#45475a").pack(fill="x", padx=8, pady=(8, 4))

        btn_frame = tk.Frame(popup, bg=_BG)
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        def _submit() -> None:
            idx = selected_var.get()
            if idx == -1:
                return  # nothing selected yet
            submitted_index[0] = idx
            popup.destroy()
            root.quit()

        def _skip() -> None:
            skipped[0] = True
            popup.destroy()
            root.quit()

        tk.Button(btn_frame, text="Submit", font=_FONT,
                  bg=_BTN_SUBMIT, fg="#1e1e2e", relief="flat", cursor="hand2",
                  command=_submit).pack(side="left", padx=(0, 6))
        tk.Button(btn_frame, text="Skip", font=_FONT,
                  bg=_BTN_SKIP, fg=_FG, relief="flat", cursor="hand2",
                  command=_skip).pack(side="left")

        popup.protocol("WM_DELETE_WINDOW", _skip)

        popup.update_idletasks()
        w, h = popup.winfo_reqwidth(), popup.winfo_reqheight()
        sw, sh = popup.winfo_screenwidth(), popup.winfo_screenheight()
        popup.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

        root.mainloop()
        root.destroy()

        if submitted_index[0] is not None:
            on_submit(submitted_index[0])
        elif skipped[0]:
            on_skip()
