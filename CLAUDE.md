# scan-to-print

Windows desktop app: scan a barcode → print the matching file from a selected folder.

## What it does
1. User picks a **source folder** containing files named after barcodes (e.g. `12345678.pdf`)
2. User selects a **printer** from the list of installed Windows printers
3. User scans a **barcode** (USB scanner acts as keyboard input → types barcode + Enter)
4. App finds the file in the folder whose name matches the barcode and sends it to the printer

## Tech stack
- **Python 3.x**
- **Tkinter** — GUI (built into Python, no extra install)
- **win32print / win32api** — Windows printing (`pip install pywin32`)
- **subprocess / ShellExecute** — to open/print files via Windows
- USB barcode scanners appear as keyboard input — no special driver needed

## Project structure
```
scan-to-print/
  main.py          # Entry point, launches the GUI
  app.py           # Main application window (Tkinter)
  printer.py       # Printer listing and print job logic
  scanner.py       # Barcode input handling (keyboard listener)
  CLAUDE.md        # This file — project briefing for Claude
  requirements.txt # Python dependencies
```

## Key decisions
- Files in the source folder must be named exactly as the barcode value (any extension)
- If multiple files match a barcode (different extensions), show a dialog to pick one
- The app should be runnable as a `.exe` via PyInstaller for distribution on Windows machines without Python

## Status
- [ ] Project scaffolded (files created, not yet implemented)
- [ ] GUI layout done
- [ ] Printer selection working
- [ ] Barcode input working
- [ ] Print job working
- [ ] Packaged as .exe
