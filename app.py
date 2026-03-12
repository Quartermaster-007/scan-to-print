"""
Main application window.
"""
import os
import tkinter as tk
import webbrowser
import winsound
from tkinter import ttk, filedialog, messagebox

import i18n
import settings
import updater
from version import __version__
from printer import get_printers, get_default_printer, print_file
from scanner import BarcodeScanner
from speedcheck import SpeedcheckWindow
from language_window import LanguageWindow
from PIL import ImageTk
from tray import TrayManager, build_status_icon

GITHUB_URL = "https://github.com/Quartermaster-007/scan-to-print"



class ScanToPrintApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"Scan to Print — {__version__}")
        self.root.resizable(True, True)

        self._settings = settings.load()

        # Load language before building any UI
        self._language = self._settings["ui"]["language"]
        i18n.load(self._language)

        self.folder_path = tk.StringVar(value=self._settings["workspace"]["folder"])
        self.selected_printer = tk.StringVar()
        self.status_text = tk.StringVar(value=i18n.t("status_ready"))
        self._update_channel = tk.StringVar(value=self._settings["updates"]["channel"])
        self._copies = tk.IntVar(value=1)
        self._devmode = None
        self._log_entries = []  # preserved across language rebuilds
        self._log_text = None   # set by _build_ui
        self._minimized_to_tray = False

        # Language prefix
        self._prefix_enabled: bool = self._settings["prefix"]["enabled"]
        self._prefix_lang: str = self._settings["prefix"]["language"]
        self._prefix_recent: list = list(self._settings["prefix"]["recent"])
        self._prefix_lang_var = tk.StringVar()  # display var for scan-frame combobox
        self._prefix_combo = None  # set by _build_ui

        self._build_menu()
        self._build_ui()
        self._apply_window_size()
        self._apply_printer()

        self.scanner = BarcodeScanner(
            self.root, self._on_barcode,
            threshold_ms=self._settings["scanner"]["threshold_ms"],
        )
        if not self._settings["scanner"]["auto_scan"]:
            self._toggle_scanner()

        # Manual entry: bind Enter directly on the barcode entry widget
        self.barcode_entry.bind("<Return>", self._on_manual_entry)

        # Save settings on close; minimize goes to tray
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.bind("<Unmap>", self._on_unmap)

        # Persist folder/printer whenever they change
        self.folder_path.trace_add("write", self._on_folder_changed)
        self.selected_printer.trace_add("write", self._on_printer_changed)

        # System tray
        self._tray = TrayManager(
            self.root,
            on_restore=self._restore_from_tray,
            on_exit=self._on_close,
            on_toggle_scan=self._toggle_scanner,
            get_scan_paused=lambda: self.scanner.paused,
            get_prefix_enabled=lambda: self._prefix_enabled,
            get_recent_prefix=lambda: list(self._prefix_recent),
            get_prefix_lang=lambda: self._prefix_lang,
            on_set_prefix_lang=self._set_prefix_lang,
        )
        self._tray.start()
        self._window_icon_ref = None  # keeps ImageTk.PhotoImage alive
        self._update_window_icon()

        # Startup update check (2s delay so window is rendered first)
        self.root.after(2000, lambda: updater.check_for_updates(
            self.root, __version__, self._settings["updates"]["channel"],
        ))

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build_menu(self):
        menubar = tk.Menu(self.root)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)

        prefs_menu = tk.Menu(file_menu, tearoff=0)
        prefs_menu.add_command(
            label=i18n.t("menu_open_settings"), command=self._open_settings_file
        )
        prefs_menu.add_separator()
        channel_menu = tk.Menu(prefs_menu, tearoff=0)
        channel_menu.add_radiobutton(
            label=i18n.t("menu_stable"),
            variable=self._update_channel,
            value="stable",
            command=self._on_channel_changed,
        )
        channel_menu.add_radiobutton(
            label=i18n.t("menu_prerelease"),
            variable=self._update_channel,
            value="prerelease",
            command=self._on_channel_changed,
        )
        prefs_menu.add_cascade(label=i18n.t("menu_update_channel"), menu=channel_menu)
        prefs_menu.add_separator()
        prefs_menu.add_command(label=i18n.t("menu_language"), command=self._open_language_window)

        file_menu.add_cascade(label=i18n.t("menu_preferences"), menu=prefs_menu)
        file_menu.add_separator()
        file_menu.add_command(label=i18n.t("menu_exit"), command=self._on_close)
        menubar.add_cascade(label=i18n.t("menu_file"), menu=file_menu)

        # Scanner menu
        self._scanner_menu = tk.Menu(menubar, tearoff=0)
        self._scanner_menu.add_command(
            label=i18n.t("menu_pause_scan"), command=self._toggle_scanner
        )
        self._scanner_menu.add_separator()
        self._scanner_menu.add_command(
            label=i18n.t("menu_speed_check"), command=self._open_speedcheck
        )
        menubar.add_cascade(label=i18n.t("menu_scanner"), menu=self._scanner_menu)

        # Prefix menu
        self._prefix_menu = tk.Menu(menubar, tearoff=0)
        self._prefix_menu.add_command(
            label=i18n.t("menu_prefix_settings"), command=self._open_prefix_window
        )
        self._rebuild_prefix_recent_menu()
        menubar.add_cascade(label=i18n.t("menu_prefix"), menu=self._prefix_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(
            label=i18n.t("menu_check_updates"), command=self._check_for_updates_manual
        )
        help_menu.add_separator()
        help_menu.add_command(label=i18n.t("menu_about"), command=self._open_about)
        menubar.add_cascade(label=i18n.t("menu_help"), menu=help_menu)

        self.root.config(menu=menubar)

    def _build_ui(self):
        pad = {"padx": 10, "pady": 5}
        self.root.columnconfigure(0, weight=1)

        # --- Folder selection ---
        folder_frame = ttk.LabelFrame(self.root, text=i18n.t("frame_folder"))
        folder_frame.grid(row=0, column=0, sticky="ew", **pad)
        folder_frame.columnconfigure(0, weight=1)

        ttk.Entry(folder_frame, textvariable=self.folder_path, width=45).grid(
            row=0, column=0, padx=5, pady=5, sticky="ew"
        )
        ttk.Button(
            folder_frame, text=i18n.t("btn_browse"), command=self._browse_folder
        ).grid(row=0, column=1, padx=5)

        # --- Printer selection ---
        printer_frame = ttk.LabelFrame(self.root, text=i18n.t("frame_printer"))
        printer_frame.grid(row=1, column=0, sticky="ew", **pad)
        printer_frame.columnconfigure(0, weight=1)

        printers = get_printers()
        self.printer_combo = ttk.Combobox(
            printer_frame,
            textvariable=self.selected_printer,
            values=printers,
            state="readonly",
            width=50,
        )
        self.printer_combo.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # --- Print settings ---
        print_frame = ttk.LabelFrame(self.root, text=i18n.t("frame_print_settings"))
        print_frame.grid(row=2, column=0, sticky="ew", **pad)

        ttk.Label(print_frame, text=i18n.t("lbl_copies")).grid(
            row=0, column=0, padx=(8, 4), pady=8, sticky="w"
        )
        ttk.Spinbox(
            print_frame, from_=1, to=99, textvariable=self._copies,
            width=4, justify="center",
        ).grid(row=0, column=1, pady=8, sticky="w")
        ttk.Button(
            print_frame, text=i18n.t("btn_printer_settings"), command=self._open_printer_settings,
        ).grid(row=0, column=2, padx=(16, 8), pady=8, sticky="w")
        self._reset_settings_btn = ttk.Button(
            print_frame, text=i18n.t("btn_reset_defaults"), command=self._reset_printer_settings,
            state=tk.NORMAL if self._devmode is not None else tk.DISABLED,
        )
        self._reset_settings_btn.grid(row=0, column=3, padx=(0, 8), pady=8, sticky="w")

        # --- Scan area ---
        scan_frame = ttk.LabelFrame(self.root, text=i18n.t("frame_scan"))
        scan_frame.grid(row=3, column=0, sticky="ew", **pad)
        scan_frame.columnconfigure(2, weight=1)  # col 2 (entry) expands; cols 0-1 (combo, dash) are fixed

        # Prefix combo sits in col 0 before the entry; hidden when feature is off
        from language_window import AVAILABLE_PREFIX_LANGUAGES
        prefix_options = [f"{i18n.t(key)} ({code})" for key, code in AVAILABLE_PREFIX_LANGUAGES]
        current_display = next(
            (f"{i18n.t(key)} ({code})" for key, code in AVAILABLE_PREFIX_LANGUAGES if code == self._prefix_lang),
            prefix_options[0],
        )
        self._prefix_lang_var.set(current_display)
        self._prefix_combo = ttk.Combobox(
            scan_frame, textvariable=self._prefix_lang_var,
            values=prefix_options, state="readonly", width=16,
        )
        self._prefix_combo.bind("<<ComboboxSelected>>", self._on_prefix_lang_changed)
        self._prefix_dash = ttk.Label(scan_frame, text="-", font=("Courier", 14))
        if self._prefix_enabled:
            self._prefix_combo.grid(row=0, column=0, padx=(5, 0), pady=10)
            self._prefix_dash.grid(row=0, column=1, padx=(2, 2))

        self.barcode_entry = ttk.Entry(scan_frame, font=("Courier", 14))
        self.barcode_entry.grid(row=0, column=2, padx=(0, 5), pady=10, sticky="ew")
        self._scan_indicator = tk.Label(scan_frame, text="●", font=("TkDefaultFont", 14), fg="#22c55e", cursor="hand2")
        self._scan_indicator.grid(row=0, column=3, padx=(6, 2))
        self._scan_indicator.bind("<Button-1>", lambda _e: self._toggle_scanner())
        self._scan_label = tk.Label(scan_frame, text=i18n.t("lbl_autoscan"), cursor="hand2")
        self._scan_label.grid(row=0, column=4, padx=(0, 8))
        self._scan_label.bind("<Button-1>", lambda _e: self._toggle_scanner())

        # --- Log ---
        log_frame = ttk.LabelFrame(self.root, text=i18n.t("frame_log"))
        log_frame.grid(row=4, column=0, sticky="nsew", **pad)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.root.rowconfigure(4, weight=1)

        self._log_text = tk.Text(
            log_frame, height=8, state="disabled",
            font=("TkFixedFont", 9), wrap="none",
        )
        self._log_text.grid(row=0, column=0, sticky="nsew", padx=(4, 0), pady=4)

        log_scroll_y = ttk.Scrollbar(log_frame, orient="vertical", command=self._log_text.yview)
        log_scroll_y.grid(row=0, column=1, sticky="ns", pady=4)
        self._log_text.config(yscrollcommand=log_scroll_y.set)

        # --- Status bar ---
        ttk.Label(self.root, textvariable=self.status_text, relief="sunken", anchor="w").grid(
            row=5, column=0, sticky="ew", padx=10, pady=(0, 10)
        )

    # ------------------------------------------------------------------
    # Log
    # ------------------------------------------------------------------

    _MAX_LOG = 50

    def _log(self, message: str, error: bool = False):
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        self._log_entries.append((entry, error))
        if len(self._log_entries) > self._MAX_LOG:
            self._log_entries.pop(0)
        self._refresh_log()

    def _refresh_log(self):
        if self._log_text is None:
            return
        self._log_text.config(state="normal")
        self._log_text.delete("1.0", "end")
        for entry, error in self._log_entries:
            tag = "error" if error else "normal"
            self._log_text.insert("end", entry + "\n", tag)
        self._log_text.tag_config("error", foreground="#dc2626")
        self._log_text.config(state="disabled")
        self._log_text.see("end")

    # ------------------------------------------------------------------
    # Settings helpers
    # ------------------------------------------------------------------

    def _apply_window_size(self):
        w = self._settings["ui"]["window_width"]
        h = self._settings["ui"]["window_height"]
        if w > 0 and h > 0:
            self.root.geometry(f"{w}x{h}")

    def _apply_printer(self):
        """Select printer: settings → Windows default → first in list."""
        printers = self.printer_combo["values"]
        if not printers:
            return

        saved = self._settings["workspace"]["printer"]
        if saved and saved in printers:
            self.selected_printer.set(saved)
            return

        default = get_default_printer()
        if default and default in printers:
            self.selected_printer.set(default)
            return

        self.printer_combo.current(0)

    def _set_devmode(self, devmode):
        self._devmode = devmode
        self._reset_settings_btn.config(
            state=tk.NORMAL if devmode is not None else tk.DISABLED
        )
        self._save_settings()

    def _save_settings(self):
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        settings.save({
            "workspace": {
                "folder": self.folder_path.get(),
                "printer": self.selected_printer.get(),
            },
            "ui": {
                "window_width": w if w > 1 else 0,
                "window_height": h if h > 1 else 0,
                "language": self._language,
            },
            "scanner": {
                "auto_scan": not self.scanner.paused,
                "threshold_ms": self.scanner.threshold_ms,
            },
            "updates": {
                "channel": self._update_channel.get(),
            },
            "prefix": {
                "enabled": self._prefix_enabled,
                "language": self._prefix_lang,
                "recent": self._prefix_recent,
            },
        })

    def _on_folder_changed(self, *_):
        self._save_settings()

    def _on_printer_changed(self, *_):
        self._set_devmode(None)  # DEVMODE is printer-specific

    def _on_channel_changed(self):
        self._save_settings()

    def _on_unmap(self, event):
        """Intercept window minimise — hide to tray instead of taskbar."""
        # Only act on the root window itself, not child widgets
        if event.widget is not self.root:
            return
        if self.root.state() == "iconic":
            self._minimize_to_tray()

    def _update_window_icon(self):
        """Set the title-bar / taskbar icon to reflect the current scan state."""
        img = build_status_icon(self.scanner.paused)
        self._window_icon_ref = ImageTk.PhotoImage(img)
        self.root.iconphoto(False, self._window_icon_ref)

    def _minimize_to_tray(self):
        self._minimized_to_tray = True
        self.root.withdraw()

    def _restore_from_tray(self):
        self._minimized_to_tray = False
        self.root.deiconify()
        # Temporarily go topmost so Windows allows us to steal focus,
        # then immediately remove topmost so the window behaves normally.
        self.root.attributes("-topmost", True)
        self.root.lift()
        self.root.focus_force()
        self.root.after(100, lambda: self.root.attributes("-topmost", False))

    def _on_close(self):
        self._tray.stop()
        self.scanner.stop()
        self._save_settings()
        self.root.destroy()

    def _show_error(self, title: str, message: str):
        """Show an error: tray notification when minimised, messagebox otherwise."""
        if self._minimized_to_tray:
            self._tray.notify(title, message)
        else:
            messagebox.showwarning(title, message)

    def _open_settings_file(self):
        path = settings.get_path()
        if not os.path.exists(path):
            settings.save(settings.load())
        os.startfile(path)

    # ------------------------------------------------------------------
    # Language
    # ------------------------------------------------------------------

    def _open_language_window(self):
        self._open_combined_language_window(focus_side="ui")

    def _open_prefix_window(self):
        self._open_combined_language_window(focus_side="prefix")

    def _open_combined_language_window(self, focus_side: str = "ui"):
        def on_apply_ui(lang_code: str):
            if lang_code == self._language:
                return
            self._language = lang_code
            self._save_settings()
            i18n.load(lang_code)
            self._apply_language()

        def on_apply_prefix(enabled: bool, lang_code: str):
            changed = (enabled != self._prefix_enabled) or (lang_code != self._prefix_lang)
            self._prefix_enabled = enabled
            if lang_code != self._prefix_lang:
                self._prefix_lang = lang_code
                self._push_prefix_recent(lang_code)
            if changed:
                self._save_settings()
                self._apply_prefix_ui()

        LanguageWindow(
            self.root,
            self._language,
            on_apply_ui,
            self._prefix_lang,
            self._prefix_enabled,
            on_apply_prefix,
            focus_side=focus_side,
        )

    def _apply_language(self):
        """Rebuild all widgets in the current language."""
        for widget in self.root.winfo_children():
            widget.destroy()
        self._build_menu()
        self._build_ui()
        self._apply_printer()
        self._update_scan_indicator()
        self.barcode_entry.bind("<Return>", self._on_manual_entry)
        self._refresh_log()
        if hasattr(self, "_tray"):
            self._tray.update_menu()

    # ------------------------------------------------------------------
    # Prefix helpers
    # ------------------------------------------------------------------

    def _push_prefix_recent(self, code: str):
        """Add code to the front of the recent list (max 5, no duplicates)."""
        if code in self._prefix_recent:
            self._prefix_recent.remove(code)
        self._prefix_recent.insert(0, code)
        self._prefix_recent = self._prefix_recent[:5]

    def _on_prefix_lang_changed(self, *_):
        """Called when the scan-frame prefix combobox selection changes."""
        display = self._prefix_lang_var.get()
        code = display.split("(")[-1].rstrip(")")
        if code != self._prefix_lang:
            self._prefix_lang = code
            self._push_prefix_recent(code)
            self._save_settings()
            self._rebuild_prefix_recent_menu()
            if hasattr(self, "_tray"):
                self._tray.update_menu()

    def _apply_prefix_ui(self):
        """Show or hide the prefix combo in the scan frame after a settings change."""
        if self._prefix_combo is None:
            return
        # Update display var to match current code
        from language_window import AVAILABLE_PREFIX_LANGUAGES
        current_display = next(
            (f"{i18n.t(key)} ({code})" for key, code in AVAILABLE_PREFIX_LANGUAGES if code == self._prefix_lang),
            self._prefix_lang_var.get(),
        )
        self._prefix_lang_var.set(current_display)
        if self._prefix_enabled:
            self._prefix_combo.grid(row=0, column=0, padx=(5, 0), pady=10)
            self._prefix_dash.grid(row=0, column=1, padx=(2, 2))
        else:
            self._prefix_combo.grid_remove()
            self._prefix_dash.grid_remove()
        self._rebuild_prefix_recent_menu()
        if hasattr(self, "_tray"):
            self._tray.update_menu()

    def _rebuild_prefix_recent_menu(self):
        """Rebuild the recent-languages entries in the Prefix menu."""
        if not hasattr(self, "_prefix_menu"):
            return
        # Remove everything after the first item (Prefix settings...)
        end = self._prefix_menu.index("end")
        if end is not None and end >= 1:
            self._prefix_menu.delete(1, "end")
        if self._prefix_recent:
            self._prefix_menu.add_separator()
            from language_window import AVAILABLE_PREFIX_LANGUAGES
            lang_map = {code: i18n.t(key) for key, code in AVAILABLE_PREFIX_LANGUAGES}
            for code in self._prefix_recent:
                label = lang_map.get(code, code)
                display = f"{label} ({code})"
                self._prefix_menu.add_command(
                    label=display,
                    command=lambda c=code: self._set_prefix_lang(c),
                )

    def _set_prefix_lang(self, code: str):
        """Quick-select a prefix language from the menu or tray."""
        if code == self._prefix_lang:
            return
        self._prefix_lang = code
        self._push_prefix_recent(code)
        self._save_settings()
        self._apply_prefix_ui()

    # ------------------------------------------------------------------
    # UI actions
    # ------------------------------------------------------------------

    def _open_speedcheck(self):
        was_paused = self.scanner.paused
        if not was_paused:
            self.scanner.toggle()
            self._update_scan_indicator()

        def on_apply(threshold_ms: int):
            self.scanner.threshold_ms = threshold_ms
            if not was_paused:
                self.scanner.toggle()
                self._update_scan_indicator()
            self._save_settings()

        def on_cancel():
            if not was_paused:
                self.scanner.toggle()
                self._update_scan_indicator()

        SpeedcheckWindow(self.root, self.scanner.threshold_ms, on_apply, on_cancel)

    def _update_scan_indicator(self):
        if self.scanner.paused:
            self._scan_indicator.config(fg="#9ca3af")
            self._scanner_menu.entryconfig(0, label=i18n.t("menu_resume_scan"))
        else:
            self._scan_indicator.config(fg="#22c55e")
            self._scanner_menu.entryconfig(0, label=i18n.t("menu_pause_scan"))

    def _toggle_scanner(self):
        self.scanner.toggle()
        self._update_scan_indicator()
        self._save_settings()
        if hasattr(self, "_tray"):
            self._tray.set_scan_state(self.scanner.paused)
            self._tray.update_menu()
            self._update_window_icon()

    def _on_manual_entry(self, *_):
        value = self.barcode_entry.get().strip()
        if value:
            self.barcode_entry.delete(0, "end")
            self._on_barcode(value)

    def _open_printer_settings(self):
        printer = self.selected_printer.get()
        if not printer:
            messagebox.showwarning(
                i18n.t("dlg_no_printer_title"), i18n.t("dlg_no_printer_msg")
            )
            return
        try:
            import win32print
            import win32con
            hPrinter = win32print.OpenPrinter(printer)
            try:
                devmode = win32print.GetPrinter(hPrinter, 2)["pDevMode"]
                result = win32print.DocumentProperties(
                    self.root.winfo_id(), hPrinter, printer,
                    devmode, devmode,
                    win32con.DM_IN_BUFFER | win32con.DM_OUT_BUFFER | win32con.DM_IN_PROMPT,
                )
                if result == win32con.IDOK:
                    self._set_devmode(devmode)
            finally:
                win32print.ClosePrinter(hPrinter)
        except Exception as e:
            messagebox.showerror(i18n.t("dlg_printer_error_title"), str(e))

    def _reset_printer_settings(self):
        self._set_devmode(None)

    def _browse_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_path.set(path)

    def _check_for_updates_manual(self):
        updater.check_for_updates(
            self.root, __version__, self._update_channel.get(), silent=False,
        )

    def _open_about(self):
        dlg = tk.Toplevel(self.root)
        dlg.title(i18n.t("about_title"))
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        ttk.Label(dlg, text=i18n.t("about_app_name"), font=("TkDefaultFont", 14, "bold")).pack(pady=(20, 4))
        ttk.Label(dlg, text=f"Version {__version__}").pack()
        ttk.Label(dlg, text=i18n.t("about_tagline")).pack(pady=(4, 12))

        link = tk.Label(dlg, text="github.com/Quartermaster-007/scan-to-print",
                        fg="blue", cursor="hand2")
        link.pack()
        link.bind("<Button-1>", lambda _: webbrowser.open(GITHUB_URL))

        ttk.Label(dlg, text="MIT License").pack(pady=(12, 16))

        btn_frame = ttk.Frame(dlg)
        btn_frame.pack(pady=(0, 16))
        ttk.Button(btn_frame, text=i18n.t("btn_check_updates"), command=lambda: [
            dlg.destroy(),
            self._check_for_updates_manual(),
        ]).pack(side="left", padx=6)
        ttk.Button(btn_frame, text=i18n.t("btn_close"), command=dlg.destroy).pack(side="left", padx=6)

    def _on_barcode(self, barcode):
        # Apply language prefix if enabled
        effective_barcode = f"{self._prefix_lang}-{barcode}" if self._prefix_enabled else barcode
        self.status_text.set(i18n.t("status_barcode_received", barcode=effective_barcode))
        folder = self.folder_path.get()
        printer = self.selected_printer.get()

        if not folder:
            self._log(i18n.t("log_no_folder", barcode=effective_barcode), error=True)
            self._show_error(i18n.t("dlg_no_folder_title"), i18n.t("dlg_no_folder_msg"))
            return
        if not printer:
            self._log(i18n.t("log_no_printer", barcode=effective_barcode), error=True)
            self._show_error(i18n.t("dlg_no_printer_title"), i18n.t("dlg_no_printer_msg"))
            return

        matches = [f for f in os.listdir(folder) if os.path.splitext(f)[0] == effective_barcode]
        barcode = effective_barcode  # use prefixed value for all subsequent references

        if not matches:
            self.status_text.set(i18n.t("status_no_file", barcode=barcode))
            self._log(i18n.t("log_no_file", barcode=barcode), error=True)
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            if self._minimized_to_tray:
                self._tray.notify(
                    i18n.t("tray_notify_no_file_title"),
                    i18n.t("tray_notify_no_file_msg", barcode=barcode),
                )
            return

        if len(matches) > 1:
            choice = self._pick_file(matches)
            if not choice:
                return
            file_to_print = os.path.join(folder, choice)
        else:
            file_to_print = os.path.join(folder, matches[0])

        copies = self._copies.get()
        filename = os.path.basename(file_to_print)
        self.status_text.set(i18n.t(
            "status_printing",
            file=filename,
            printer=printer,
        ))
        try:
            print_file(file_to_print, printer, copies, self._devmode)
            self._copies.set(1)
            self.status_text.set(i18n.t("status_sent", file=filename))
            self._log(i18n.t("log_printed", barcode=barcode, file=filename, printer=printer, copies=copies))
        except Exception as e:
            self._show_error(i18n.t("dlg_printer_error_title"), str(e))
            self.status_text.set(i18n.t("status_print_failed"))
            self._log(i18n.t("log_print_failed", barcode=barcode, file=filename, error=str(e)), error=True)

    def _pick_file(self, files):
        dialog = tk.Toplevel(self.root)
        dialog.title(i18n.t("dlg_multi_title"))
        dialog.transient(self.root)
        dialog.grab_set()
        chosen = tk.StringVar()

        ttk.Label(dialog, text=i18n.t("dlg_multi_msg")).pack(padx=10, pady=5)
        lb = tk.Listbox(dialog, listvariable=tk.StringVar(value=files), height=6, width=40)
        lb.pack(padx=10, pady=5)
        lb.selection_set(0)

        def confirm():
            sel = lb.curselection()
            if sel:
                chosen.set(files[sel[0]])
            dialog.destroy()

        ttk.Button(dialog, text=i18n.t("btn_print_this"), command=confirm).pack(pady=5)
        self.root.wait_window(dialog)
        return chosen.get()

    def run(self):
        self.root.mainloop()
