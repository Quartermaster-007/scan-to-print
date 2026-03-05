"""
Main application window.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from printer import get_printers, print_file
from scanner import BarcodeScanner


class ScanToPrintApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Scan to Print")
        self.root.resizable(False, False)

        self.folder_path = tk.StringVar()
        self.selected_printer = tk.StringVar()
        self.status_text = tk.StringVar(value="Ready. Scan a barcode to print.")

        self._build_ui()
        self.scanner = BarcodeScanner(self.root, self._on_barcode)

    def _build_ui(self):
        pad = {"padx": 10, "pady": 5}

        # --- Folder selection ---
        folder_frame = ttk.LabelFrame(self.root, text="1. Select folder")
        folder_frame.grid(row=0, column=0, sticky="ew", **pad)

        ttk.Entry(folder_frame, textvariable=self.folder_path, width=45).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(folder_frame, text="Browse...", command=self._browse_folder).grid(row=0, column=1, padx=5)

        # --- Printer selection ---
        printer_frame = ttk.LabelFrame(self.root, text="2. Select printer")
        printer_frame.grid(row=1, column=0, sticky="ew", **pad)

        printers = get_printers()
        self.printer_combo = ttk.Combobox(printer_frame, textvariable=self.selected_printer,
                                          values=printers, state="readonly", width=50)
        self.printer_combo.grid(row=0, column=0, padx=5, pady=5)
        if printers:
            self.printer_combo.current(0)

        # --- Scan area ---
        scan_frame = ttk.LabelFrame(self.root, text="3. Scan barcode")
        scan_frame.grid(row=2, column=0, sticky="ew", **pad)

        self.barcode_entry = ttk.Entry(scan_frame, width=30, font=("Courier", 14))
        self.barcode_entry.grid(row=0, column=0, padx=5, pady=10)
        self.barcode_entry.focus_set()
        ttk.Label(scan_frame, text="(scan or type + Enter)").grid(row=0, column=1, padx=5)

        # --- Status bar ---
        ttk.Label(self.root, textvariable=self.status_text, relief="sunken",
                  anchor="w").grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))

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

        import os
        matches = [f for f in os.listdir(folder)
                   if os.path.splitext(f)[0] == barcode]

        if not matches:
            self.status_text.set(f"No file found for barcode: {barcode}")
            return

        if len(matches) > 1:
            # Let user pick which file to print
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
