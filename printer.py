"""
Printer listing and print job logic (Windows only).
"""
import os
import subprocess


def get_printers():
    """Return list of installed printer names."""
    try:
        import win32print
        printers = win32print.EnumPrinters(
            win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        )
        return [p[2] for p in printers]
    except ImportError:
        # Non-Windows fallback (for development)
        return ["(pywin32 not installed — Windows only)"]


def get_default_printer() -> str:
    """Return the Windows default printer name, or empty string if unavailable."""
    try:
        import win32print
        return win32print.GetDefaultPrinter()
    except Exception:
        return ""


def print_file(file_path, printer_name):
    """Send a file to the specified printer using Windows ShellExecute."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        import win32api
        import win32print
        win32print.SetDefaultPrinter(printer_name)
        win32api.ShellExecute(0, "print", file_path, None, ".", 0)
    except ImportError:
        raise RuntimeError("pywin32 is required for printing. Run: pip install pywin32")
