"""
Main application window.
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import settings
from printer import get_printers, get_default_printer, print_file
from scanner import BarcodeScanner


class ScanToPrintApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Scan to Print")
        self.root.resizable(True, True)

        self._settings = settings.load()

        self.folder_path = tk.StringVar(value=self._settings.get("folder", ""))
        self.selected_printer = tk.StringVar()
        self.status_text = tk.StringVar(value="Ready. Scan a barcode to print.")

        self._build_menu()
        self._build_ui()
        self._apply_window_size()
        self._apply_printer()

        self.scanner = BarcodeScanner(self.root, self._on_barcode)

        # Manual entry: bind Enter directly on the barcode entry widget
        self.barcode_entry.bind("<Return>", self._on_manual_entry)

        # Save settings on close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Persist folder whenever it changes
        self.folder_path.trace_add("write", self._on_folder_changed)
        # Persist printer whenever it changes
        self.selected_printer.trace_add("write", self._on_printer_changed)

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open settings file", command=self._open_settings_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        menubar.add_cascade(label="File", menu=file_menu)
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

        self.barcode_entry = ttk.Entry(scan_frame, width=30, font=("Courier", 14))
        self.barcode_entry.grid(row=0, column=0, padx=5, pady=10)
        ttk.Label(scan_frame, text="(global listener active — or type + Enter)").grid(row=0, column=1, padx=5)

        # --- Status bar ---
        ttk.Label(self.root, textvariable=self.status_text, relief="sunken", anchor="w").grid(
            row=3, column=0, sticky="ew", padx=10, pady=(0, 10)
        )

    # ------------------------------------------------------------------
    # Settings helpers
    # ------------------------------------------------------------------

    def _apply_window_size(self):
        w = self._settings.get("window_width", 0)
        h = self._settings.get("window_height", 0)
        if w > 0 and h > 0:
            self.root.geometry(f"{w}x{h}")

    def _apply_printer(self):
        """Select printer: settings → Windows default → first in list."""
        printers = self.printer_combo["values"]
        if not printers:
            return

        saved = self._settings.get("printer", "")
        if saved and saved in printers:
            self.selected_printer.set(saved)
            return

        default = get_default_printer()
        if default and default in printers:
            self.selected_printer.set(default)
            return

        # Fall back to first available printer
        self.printer_combo.current(0)

    def _save_settings(self):
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        settings.save(
            {
                "folder": self.folder_path.get(),
                "printer": self.selected_printer.get(),
                "window_width": w if w > 1 else 0,
                "window_height": h if h > 1 else 0,
            }
        )

    def _on_folder_changed(self, *_):
        self._save_settings()

    def _on_printer_changed(self, *_):
        self._save_settings()

    def _on_close(self):
        self.scanner.stop()
        self._save_settings()
        self.root.destroy()

    def _open_settings_file(self):
        path = settings.get_path()
        if not os.path.exists(path):
            # Create an empty settings file so there is something to open
            settings.save(settings.load())
        os.startfile(path)

    # ------------------------------------------------------------------
    # UI actions
    # ------------------------------------------------------------------

    def _on_manual_entry(self, *_):
        value = self.barcode_entry.get().strip()
        if value:
            self.barcode_entry.delete(0, "end")
            self._on_barcode(value)

    def _browse_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_path.set(path)

    def _on_barcode(self, barcode):
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
