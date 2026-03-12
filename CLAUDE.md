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
  scanner.py         # Global pynput keyboard listener (timing-based barcode detection)
  settings.py        # Read/write settings.json in %APPDATA%/ScanToPrint/
  speedcheck.py      # Scanner speed check window (measures threshold, saves to settings)
  updater.py         # GitHub release check on startup + in-app self-update
  version.py         # __version__ placeholder, overwritten by CI at build time
  locales/           # UI string translations (en.json, nl.json, …) (planned)
  build.py           # Branch-aware build script (outputs to dist/<branch>/)
  test_scan.py       # Simulates USB scanner input for testing without hardware
  CLAUDE.md          # This file — project briefing for Claude
  FEATURES.md        # Feature planning and implementation notes
  LICENSE            # MIT
  requirements.txt   # Python dependencies
  ScanToPrint.spec   # PyInstaller build spec (produces ScanToPrint.exe)
  images/            # App icons (scan-to-print.ico, scan-to-print.png)
```

## Feature workflow
When implementing a feature:
1. **Create a feature branch** before writing any code — branch name should reflect the feature (e.g. `feature/print-copies`)
2. **Implement the feature** on that branch
3. **Update documentation** before creating a PR:
   - Mark the feature as `[x]` in the Status list in this file
   - Add implementation notes to the relevant feature section in `FEATURES.md`
4. **Create a PR** from the feature branch into `main` (squash merge only; never push directly to main)

## Key decisions
- Files in the source folder must be named exactly as the barcode value (any extension)
- If multiple files match a barcode (different extensions), show a dialog to pick one
- The app should be runnable as a `.exe` via PyInstaller for distribution on Windows machines without Python
- Printing targets a named printer directly via `pypdfium2` / `Pillow` + `win32print` — `SetDefaultPrinter` is never called
- Global barcode input is captured via `pynput` using timing-based detection (default 100ms threshold, user-calibrated via Speed check window) so the app works when minimised to the system tray
- Settings are persisted in `%APPDATA%\ScanToPrint\settings.json` as nested groups: `workspace` (folder, printer), `ui` (window_width, window_height), `scanner` (auto_scan, threshold_ms), `updates` (channel)
- UI language strings live in `locales/<lang>.json`; English is the fallback
- Language prefix feature prepends an ISO 3166-1 alpha-2 code with a hyphen (e.g. `EN-12345678.*`)
- Versioning format: `yyyy.mm.dd`; update check calls the GitHub releases API on startup
- Branch-per-feature workflow; `build.py` outputs to `dist/<branch>/ScanToPrint.exe`
- Repo: squash merge only; main branch protected (no direct push, no force push)

## Status
- [x] Project scaffolded
- [x] GUI layout done
- [x] Printer selection working
- [x] Barcode input working (focus-based, superseded)
- [x] Print job working (direct GDI via pypdfium2/Pillow — no dialog, no default-printer side effect)
- [x] Persistent settings — `settings.py`, File menu, window size, last folder/printer
- [x] Auto scan-to-print / global keyboard hook — `pynput` listener, pause toggle, speed check window
- [x] GitHub update check + in-app self-update — `updater.py`, `version.py`, `.github/workflows/release.yml`
- [ ] UI language selection
- [ ] Print history / log
- [ ] Failure sound feedback
- [x] Direct silent printing — pypdfium2 + Pillow, no dialog
- [x] Print copies input + printer options dialog
- [ ] System tray
- [ ] Language prefix
- [x] Packaged as .exe — CI builds via PyInstaller on `windows-latest`, published as GitHub Release
