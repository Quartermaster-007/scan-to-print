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
- **win32print / win32api** — printer enumeration (`pip install pywin32`)
- **pypdfium2** — PDF rendering and printing to a named printer without changing system default
- **Pillow** — image (PNG, JPG) rendering and printing to a named printer
- **pynput** — global keyboard listener for barcode input (works when app is minimised to tray)
- **pystray** — Windows system tray icon and right-click menu
- **requests** — GitHub releases API for update checks
- USB barcode scanners appear as keyboard input — no special driver needed

## Project structure
```
scan-to-print/
  main.py            # Entry point, launches the GUI
  app.py             # Main application window (Tkinter)
  printer.py         # Printer listing and print job logic
  scanner.py         # Barcode input handling (keyboard listener)
  settings.py        # Read/write settings.json in %APPDATA%
  updater.py         # GitHub release check on startup
  locales/           # UI string translations (en.json, nl.json, …)
  CLAUDE.md          # This file — project briefing for Claude
  FEATURES.md        # Feature planning and implementation notes
  LICENSE            # MIT
  requirements.txt   # Python dependencies
  ScanToPrint.spec   # PyInstaller build spec (produces ScanToPrint.exe)
  images/            # App icons (scan-to-print.ico, scan-to-print.png)
```

## Key decisions
- Files in the source folder must be named exactly as the barcode value (any extension)
- If multiple files match a barcode (different extensions), show a dialog to pick one
- The app should be runnable as a `.exe` via PyInstaller for distribution on Windows machines without Python
- Printing targets a named printer directly via `pypdfium2` / `Pillow` + `win32print` — `SetDefaultPrinter` is never called
- Global barcode input is captured via `pynput` using timing-based detection (~50ms threshold) so the app works when minimised to the system tray
- Settings are persisted in `%APPDATA%\ScanToPrint\settings.json`
- UI language strings live in `locales/<lang>.json`; English is the fallback
- Language prefix feature prepends an ISO 3166-1 alpha-2 code with a hyphen (e.g. `EN-12345678.*`)
- Versioning format: `yyyy.mm.dd`; update check calls the GitHub releases API on startup

## Status
- [x] Project scaffolded
- [x] GUI layout done
- [x] Printer selection working
- [x] Barcode input working (focus-based)
- [x] Print job working (ShellExecute — to be replaced by pypdfium2/Pillow in Feature 9)
- [ ] Persistent settings (#3)
- [ ] Auto scan-to-print / global keyboard hook (#10)
- [ ] GitHub update check (#13)
- [ ] UI language selection (#11)
- [ ] Print history / log (#1)
- [ ] Failure sound feedback (#2)
- [ ] Improved printer targeting — pypdfium2 + Pillow (#9)
- [ ] Print copies input (#5)
- [ ] System tray (#7)
- [ ] Language prefix (#12)
- [ ] Packaged as .exe
