"""
Main application window.
"""
import os
import tkinter as tk
import webbrowser
from tkinter import ttk, filedialog, messagebox

import settings
import updater
from version import __version__
from printer import get_printers, get_default_printer, print_file
from scanner import BarcodeScanner
from speedcheck import SpeedcheckWindow

GITHUB_URL = "https://github.com/Quartermaster-007/scan-to-print"


class ScanToPrintApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"Scan to Print — {__version__}")
        self.root.resizable(True, True)

        self._settings = settings.load()

        self.folder_path = tk.StringVar(value=self._settings["workspace"]["folder"])
        self.selected_printer = tk.StringVar()
        self.status_text = tk.StringVar(value="Ready. Scan a barcode to print.")
        self._update_channel = tk.StringVar(value=self._settings["updates"]["channel"])

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

        # Save settings on close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Persist folder/printer whenever they change
        self.folder_path.trace_add("write", self._on_folder_changed)
        self.selected_printer.trace_add("write", self._on_printer_changed)

        # Startup update check (2s delay so window is rendered first)
        self.root.after(
            2000, updater.check_for_updates,
            self.root, __version__, self._settings["updates"]["channel"],
        )

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build_menu(self):
        menubar = tk.Menu(self.root)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)

        prefs_menu = tk.Menu(file_menu, tearoff=0)
        prefs_menu.add_command(label="Open settings file...", command=self._open_settings_file)
        prefs_menu.add_separator()
        channel_menu = tk.Menu(prefs_menu, tearoff=0)
        channel_menu.add_radiobutton(
            label="Stable releases",
            variable=self._update_channel,
            value="stable",
            command=self._on_channel_changed,
        )
        channel_menu.add_radiobutton(
            label="Pre-releases",
            variable=self._update_channel,
            value="prerelease",
            command=self._on_channel_changed,
        )
        prefs_menu.add_cascade(label="Update channel", menu=channel_menu)

        file_menu.add_cascade(label="Preferences", menu=prefs_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        menubar.add_cascade(label="File", menu=file_menu)

        # Scanner menu
        self._scanner_menu = tk.Menu(menubar, tearoff=0)
        self._scanner_menu.add_command(label="Pause auto-scan", command=self._toggle_scanner)
        self._scanner_menu.add_separator()
        self._scanner_menu.add_command(label="Speed check...", command=self._open_speedcheck)
        menubar.add_cascade(label="Scanner", menu=self._scanner_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Check for updates", command=self._check_for_updates_manual)
        help_menu.add_separator()
        help_menu.add_command(label="About Scan to Print", command=self._open_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def _build_ui(self):
        pad = {"padx": 10, "pady": 5}
        self.root.columnconfigure(0, weight=1)

        # --- Folder selection ---
        folder_frame = ttk.LabelFrame(self.root, text="1. Select folder")
        folder_frame.grid(row=0, column=0, sticky="ew", **pad)
        folder_frame.columnconfigure(0, weight=1)

        ttk.Entry(folder_frame, textvariable=self.folder_path, width=45).grid(
            row=0, column=0, padx=5, pady=5, sticky="ew"
        )
        ttk.Button(folder_frame, text="Browse...", command=self._browse_folder).grid(
            row=0, column=1, padx=5
        )

        # --- Printer selection ---
        printer_frame = ttk.LabelFrame(self.root, text="2. Select printer")
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

        # --- Scan area ---
        scan_frame = ttk.LabelFrame(self.root, text="3. Scan barcode")
        scan_frame.grid(row=2, column=0, sticky="ew", **pad)
        scan_frame.columnconfigure(0, weight=1)

        self.barcode_entry = ttk.Entry(scan_frame, font=("Courier", 14))
        self.barcode_entry.grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        self._scan_indicator = tk.Label(scan_frame, text="●", font=("TkDefaultFont", 14), fg="#22c55e")
        self._scan_indicator.grid(row=0, column=1, padx=(6, 2))
        tk.Label(scan_frame, text="Auto-scan").grid(row=0, column=2, padx=(0, 8))

        # --- Status bar ---
        ttk.Label(self.root, textvariable=self.status_text, relief="sunken", anchor="w").grid(
            row=3, column=0, sticky="ew", padx=10, pady=(0, 10)
        )

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
            },
            "scanner": {
                "auto_scan": not self.scanner.paused,
                "threshold_ms": self.scanner.threshold_ms,
            },
            "updates": {
                "channel": self._update_channel.get(),
            },
        })

    def _on_folder_changed(self, *_):
        self._save_settings()

    def _on_printer_changed(self, *_):
        self._save_settings()

    def _on_channel_changed(self):
        self._save_settings()

    def _on_close(self):
        self.scanner.stop()
        self._save_settings()
        self.root.destroy()

    def _open_settings_file(self):
        path = settings.get_path()
        if not os.path.exists(path):
            settings.save(settings.load())
        os.startfile(path)

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

        SpeedcheckWindow(self.root, self.scanner.threshold_ms, on_apply)

    def _update_scan_indicator(self):
        if self.scanner.paused:
            self._scan_indicator.config(fg="#9ca3af")
            self._scanner_menu.entryconfig(0, label="Resume auto-scan")
        else:
            self._scan_indicator.config(fg="#22c55e")
            self._scanner_menu.entryconfig(0, label="Pause auto-scan")

    def _toggle_scanner(self):
        self.scanner.toggle()
        self._update_scan_indicator()
        self._save_settings()

    def _on_manual_entry(self, *_):
        value = self.barcode_entry.get().strip()
        if value:
            self.barcode_entry.delete(0, "end")
            self._on_barcode(value)

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
        dlg.title("About Scan to Print")
        dlg.resizable(False, False)
        dlg.grab_set()

        tk.Label(dlg, text="Scan to Print", font=("TkDefaultFont", 14, "bold")).pack(pady=(20, 4))
        tk.Label(dlg, text=f"Version {__version__}").pack()
        tk.Label(dlg, text="Scan a barcode → print the file").pack(pady=(4, 12))

        link = tk.Label(dlg, text="github.com/Quartermaster-007/scan-to-print",
                        fg="blue", cursor="hand2")
        link.pack()
        link.bind("<Button-1>", lambda _: webbrowser.open(GITHUB_URL))

        tk.Label(dlg, text="MIT License").pack(pady=(12, 16))

        btn_frame = tk.Frame(dlg)
        btn_frame.pack(pady=(0, 16))
        ttk.Button(btn_frame, text="Check for updates", command=lambda: [
            dlg.destroy(),
            self._check_for_updates_manual(),
        ]).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Close", command=dlg.destroy).pack(side="left", padx=6)

    def _on_barcode(self, barcode):
        self.status_text.set(f"Barcode received: {barcode}")
        folder = self.folder_path.get()
        printer = self.selected_printer.get()

        if not folder:
            messagebox.showwarning("No folder", "Please select a folder first.")
            return
        if not printer:
            messagebox.showwarning("No printer", "Please select a printer first.")
            return

        matches = [f for f in os.listdir(folder) if os.path.splitext(f)[0] == barcode]

        if not matches:
            self.status_text.set(f"No file found for barcode: {barcode}")
            return

        if len(matches) > 1:
            choice = self._pick_file(matches)
            if not choice:
                return
            file_to_print = os.path.join(folder, choice)
        else:
            file_to_print = os.path.join(folder, matches[0])

        self.status_text.set(f"Printing: {os.path.basename(file_to_print)} on {printer}...")
        try:
            print_file(file_to_print, printer)
            self.status_text.set(f"Sent to printer: {os.path.basename(file_to_print)}")
        except Exception as e:
            messagebox.showerror("Print error", str(e))
            self.status_text.set("Print failed.")

    def _pick_file(self, files):
        dialog = tk.Toplevel(self.root)
        dialog.title("Multiple files found")
        dialog.grab_set()
        chosen = tk.StringVar()

        ttk.Label(dialog, text="Multiple files match. Select one:").pack(padx=10, pady=5)
        lb = tk.Listbox(dialog, listvariable=tk.StringVar(value=files), height=6, width=40)
        lb.pack(padx=10, pady=5)
        lb.selection_set(0)

        def confirm():
            sel = lb.curselection()
            if sel:
                chosen.set(files[sel[0]])
            dialog.destroy()

        ttk.Button(dialog, text="Print this one", command=confirm).pack(pady=5)
        self.root.wait_window(dialog)
        return chosen.get()

    def run(self):
        self.root.mainloop()
