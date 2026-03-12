"""
Language selection window.

Shows a list of available UI languages as radio buttons.
Calls on_apply(lang_code) when the user confirms their choice.
"""
import tkinter as tk
from tkinter import ttk

import i18n

AVAILABLE_LANGUAGES = [
    ("English", "en"),
    ("Nederlands", "nl"),
]


class LanguageWindow:
    def __init__(self, parent, current_lang: str, on_apply):
        self._on_apply = on_apply

        self._win = tk.Toplevel(parent)
        self._win.title(i18n.t("lang_window_title"))
        self._win.resizable(False, False)
        self._win.transient(parent)
        self._win.grab_set()

        self._selected = tk.StringVar(value=current_lang)
        self._build_ui()

    def _build_ui(self):
        ttk.Label(self._win, text=i18n.t("lang_window_label")).pack(
            padx=20, pady=(16, 8), anchor="w"
        )

        for label, code in AVAILABLE_LANGUAGES:
            ttk.Radiobutton(
                self._win, text=label, variable=self._selected, value=code
            ).pack(anchor="w", padx=32, pady=2)

        btn_frame = ttk.Frame(self._win)
        btn_frame.pack(pady=(16, 16))
        ttk.Button(btn_frame, text=i18n.t("btn_apply"), command=self._apply).pack(
            side="left", padx=6
        )
        ttk.Button(btn_frame, text=i18n.t("btn_cancel"), command=self._win.destroy).pack(
            side="left", padx=6
        )

    def _apply(self):
        self._on_apply(self._selected.get())
        self._win.destroy()
