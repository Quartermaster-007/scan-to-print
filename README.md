# scan-to-print

Windows desktop app: scan a barcode with a USB scanner and automatically print the matching file from a selected folder.

## Requirements

- Windows (printing relies on the Windows shell and `pywin32`)
- Python 3.x
- Dependencies:

```
pip install -r requirements.txt
```

`requirements.txt` installs:
- `pywin32` — Windows printer API
- `pyinstaller` — for building a standalone `.exe`

## Running the app

```
python main.py
```

## Usage

1. **Select folder** — choose the folder containing your files. Files must be named after their barcode value (e.g. `12345678.pdf`, `ABC-999.pdf`).
2. **Select printer** — pick from the list of installed Windows printers.
3. **Scan** — point your USB barcode scanner at a barcode. The scanner types the value and presses Enter, which triggers the print job automatically. You can also type a value manually and press Enter.

If multiple files in the folder share the same barcode name (different extensions), a dialog will appear to let you choose which one to print.

## Project structure

```
scan-to-print/
  main.py            # Entry point — run this to launch the app
  app.py             # Main Tkinter window and UI logic
  printer.py         # Printer enumeration and print job (pywin32 + ShellExecute)
  scanner.py         # Barcode input handling (Enter key binding)
  requirements.txt   # Python dependencies
  ScanToPrint.spec   # PyInstaller build spec
  images/            # App icons
```

## Building a standalone .exe

```
pyinstaller ScanToPrint.spec
```

The output will be in the `dist/` folder as `ScanToPrint.exe`. It can be run on Windows machines without Python installed.

## Notes

- The app prints directly to the selected printer via `pypdfium2` (PDF) and `Pillow` (images) + `win32print`, without changing the Windows system default printer.
- A global keyboard listener captures barcode scanner input even when the app is minimised to the system tray.
