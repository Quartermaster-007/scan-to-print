"""
Combined Language / Prefix window.

Left panel  — UI language selection (radio buttons).
Right panel — Language prefix feature: enable toggle + prefix language selection.

`focus_side` ("ui" or "prefix") determines which panel is highlighted when
the window opens (both are always visible).
"""
import tkinter as tk
from tkinter import ttk

import i18n

AVAILABLE_LANGUAGES = [
    ("English", "en"),
    ("Nederlands", "nl"),
]

AVAILABLE_PREFIX_LANGUAGES = [
    ("Bulgarian", "BG"),
    ("Catalan", "CA"),
    ("Croatian", "HR"),
    ("Czech", "CS"),
    ("Danish", "DA"),
    ("Dutch", "NL"),
    ("English", "EN"),
    ("Finnish", "FI"),
    ("French", "FR"),
    ("German", "DE"),
    ("Greek", "EL"),
    ("Hungarian", "HU"),
    ("Italian", "IT"),
    ("Norwegian", "NO"),
    ("Polish", "PL"),
    ("Portuguese", "PT"),
    ("Romanian", "RO"),
    ("Russian", "RU"),
    ("Slovak", "SK"),
    ("Slovenian", "SL"),
    ("Spanish", "ES"),
    ("Swedish", "SV"),
    ("Turkish", "TR"),
    ("Ukrainian", "UK"),
]


class LanguageWindow:
    def __init__(
        self,
        parent,
        current_lang: str,
        on_apply_ui,
        current_prefix_lang: str,
        prefix_enabled: bool,
        on_apply_prefix,
        focus_side: str = "ui",
    ):
        self._on_apply_ui = on_apply_ui
        self._on_apply_prefix = on_apply_prefix

        self._win = tk.Toplevel(parent)
        self._win.title(i18n.t("lang_window_title"))
        self._win.resizable(False, False)
        self._win.transient(parent)
        self._win.grab_set()

        self._selected_ui = tk.StringVar(value=current_lang)
        self._prefix_enabled_var = tk.BooleanVar(value=prefix_enabled)
        self._selected_prefix = tk.StringVar(value=current_prefix_lang)

        self._build_ui(focus_side)

    def _build_ui(self, focus_side: str):
        container = ttk.Frame(self._win)
        container.pack(fill="both", expand=True, padx=12, pady=(12, 4))

        # --- Left panel: UI language ---
        ui_frame = ttk.LabelFrame(container, text=i18n.t("lang_window_ui_label"))
        ui_frame.pack(side="left", fill="y", padx=(0, 8), anchor="n")

        for label, code in AVAILABLE_LANGUAGES:
            ttk.Radiobutton(
                ui_frame, text=label, variable=self._selected_ui, value=code
            ).pack(anchor="w", padx=12, pady=2)

        # --- Right panel: prefix feature ---
        prefix_frame = ttk.LabelFrame(container, text=i18n.t("prefix_window_title"))
        prefix_frame.pack(side="left", fill="y", anchor="n")

        ttk.Checkbutton(
            prefix_frame,
            text=i18n.t("prefix_window_enable"),
            variable=self._prefix_enabled_var,
            command=self._on_toggle_prefix,
        ).pack(anchor="w", padx=12, pady=(8, 4))

        ttk.Separator(prefix_frame, orient="horizontal").pack(fill="x", padx=12, pady=4)

        self._prefix_lang_label = ttk.Label(
            prefix_frame, text=i18n.t("prefix_window_lang_label")
        )
        self._prefix_lang_label.pack(anchor="w", padx=12, pady=(4, 2))

        self._prefix_radio_frame = ttk.Frame(prefix_frame)
        self._prefix_radio_frame.pack(anchor="w", padx=12, pady=(0, 8))

        for label, code in AVAILABLE_PREFIX_LANGUAGES:
            ttk.Radiobutton(
                self._prefix_radio_frame,
                text=f"{label} ({code})",
                variable=self._selected_prefix,
                value=code,
            ).pack(anchor="w", pady=2)

        self._on_toggle_prefix()  # set initial enabled/disabled state

        # --- Buttons ---
        btn_frame = ttk.Frame(self._win)
        btn_frame.pack(pady=(8, 16))
        ttk.Button(btn_frame, text=i18n.t("btn_apply"), command=self._apply).pack(
            side="left", padx=6
        )
        ttk.Button(btn_frame, text=i18n.t("btn_cancel"), command=self._win.destroy).pack(
            side="left", padx=6
        )

    def _on_toggle_prefix(self):
        state = "normal" if self._prefix_enabled_var.get() else "disabled"
        for child in self._prefix_radio_frame.winfo_children():
            child.config(state=state)
        self._prefix_lang_label.config(state=state)

    def _apply(self):
        self._on_apply_ui(self._selected_ui.get())
        self._on_apply_prefix(self._prefix_enabled_var.get(), self._selected_prefix.get())
        self._win.destroy()
