import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from config import load_config, save_config
from csv_handler import load_csv
from printer import find_compatible_printers, print_image
from sounds import play_success, play_error


class scanToPrint:
    def __init__(self, root):
        self.root = root
        self.root.title("scan-to-print")

        self.records = {}
        self.csv_path = ""
        self.printer_name = ""

        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        tk.Label(self.root, text="CSV File:").grid(row=0, column=0, sticky='e')
        self.csv_button = tk.Button(self.root, text="Select CSV", command=self.select_csv)
        self.csv_button.grid(row=0, column=1, sticky='w')

        tk.Label(self.root, text="Printer:").grid(row=1, column=0, sticky='e')
        self.printer_button = tk.Button(self.root, text="Select Printer", command=self.select_printer)
        self.printer_button.grid(row=1, column=1, sticky='w')

        tk.Label(self.root, text="Barcode:").grid(row=2, column=0, sticky='e')
        self.barcode_entry = tk.Entry(self.root, width=30)
        self.barcode_entry.grid(row=2, column=1, sticky='w')
        self.barcode_entry.bind("<Return>", self.print_from_entry)

        self.print_button = tk.Button(self.root, text="Print", command=self.print_from_entry)
        self.print_button.grid(row=3, column=0)
        self.reload_button = tk.Button(self.root, text="Reload CSV", command=self.reload_csv)
        self.reload_button.grid(row=3, column=1)
        self.change_printer_button = tk.Button(self.root, text="Change Printer", command=self.select_printer)
        self.change_printer_button.grid(row=4, column=0)
        self.exit_button = tk.Button(self.root, text="Exit", command=self.root.quit)
        self.exit_button.grid(row=4, column=1)

        self.log_box = tk.Text(self.root, height=10, width=60, state='disabled')
        self.log_box.grid(row=5, column=0, columnspan=2, pady=10)

    def log(self, msg):
        self.log_box.config(state='normal')
        self.log_box.insert(tk.END, msg + "\n")
        self.log_box.see(tk.END)
        self.log_box.config(state='disabled')

    def load_config(self):
        config = load_config()
        if 'CSV_FILE' in config and config['CSV_FILE']:
            use = messagebox.askyesno("Use Saved CSV", f"Use last CSV file?\n{config['CSV_FILE']}")
            if use:
                self.csv_path = config['CSV_FILE']
                self.load_csv()
        if 'PRINTER' in config and config['PRINTER']:
            use = messagebox.askyesno("Use Saved Printer", f"Use last printer?\n{config['PRINTER']}")
            if use:
                self.printer_name = config['PRINTER']
                self.log(f"Using saved printer: {self.printer_name}")

    def save_config(self):
        save_config(self.csv_path, self.printer_name)

    def select_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if path:
            self.csv_path = path
            self.load_csv()
            self.save_config()

    def load_csv(self):
        try:
            self.records = load_csv(self.csv_path)
            self.log(f"[Loaded] {len(self.records)} barcode records from CSV.")
        except Exception as e:
            self.log(f"[Error] Failed to load CSV: {e}")
            play_error()

    def reload_csv(self):
        if self.csv_path:
            self.load_csv()
        else:
            self.select_csv()

    def select_printer(self):
        compatible = find_compatible_printers()
        if not compatible:
            messagebox.showerror("No Printers Found", "No supported printers found.")
            play_error()
            return

        selection = simpledialog.askstring(
            "Select Printer",
            "Available Printers:\n" + "\n".join(f"{i+1}. {p}" for i, p in enumerate(compatible)) + "\n\nEnter number:")
        if selection and selection.isdigit():
            idx = int(selection) - 1
            if 0 <= idx < len(compatible):
                self.printer_name = compatible[idx]
                self.log(f"[Printer] Selected: {self.printer_name}")
                self.save_config()
            else:
                self.log("[Error] Invalid printer selection.")
                play_error()

    def print_from_entry(self, event=None):
        barcode = self.barcode_entry.get().strip()
        self.barcode_entry.delete(0, tk.END)
        if not barcode:
            return
        if barcode in self.records:
            image_path = self.records[barcode]
            try:
                print_image(self.printer_name, image_path)
                self.log(f"[Printed] {image_path}")
                play_success()
            except Exception as e:
                self.log(f"[Error] Failed to print: {e}")
                play_error()
        else:
            self.log(f"[Warning] No match found for barcode: {barcode}")
            play_error()
