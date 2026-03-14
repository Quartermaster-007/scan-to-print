# scan-to-print

Windows desktop app: scan a barcode with a USB scanner and automatically print the matching file from a selected folder.

## Requirements

- Windows (printing relies on `pywin32`)
- Python 3.x
- Dependencies:

```
pip install -r requirements.txt
```

`requirements.txt` installs:
- `pywin32` — Windows printer API
- `pynput` — global keyboard listener for barcode input
- `pypdfium2` — PDF rendering and direct printing
- `Pillow` — image rendering and direct printing
- `pystray` — system tray icon and right-click menu
- `requests` — GitHub update check and in-app self-update
- `pyinstaller` — for building a standalone `.exe`

## Running the app

```
python main.py
```

## Usage

1. **Select folder** — choose the folder containing your files. Files must be named after their barcode value (e.g. `12345678.pdf`, `ABC-999.pdf`).
2. **Select printer** — pick from the list of installed Windows printers. The last used printer is pre-selected on startup; falls back to the Windows default printer.
3. **Print settings** — set the number of copies (resets to 1 after each print). Use **Printer settings…** to configure paper, tray, orientation, and other driver options via the Windows native dialog.
4. **Scan** — point your USB barcode scanner at a barcode. The global listener detects scanner input automatically — no need to click the app first.

You can also type a barcode manually in the entry box and press Enter.

If multiple files share the same barcode name (different extensions), a dialog lets you choose which to print.

Settings (folder, printer, language, window size, auto-scan state, scanner threshold) are saved automatically to `%APPDATA%\ScanToPrint\settings.json`.

## System tray

Minimising the window hides the app from the taskbar and moves it to the Windows system tray. The tray icon shows the current auto-scan state (green dot = active, grey dot = paused).

Right-click the tray icon for quick actions:

| Item | Description |
|------|-------------|
| Restore | Opens the main window |
| Pause / Resume auto-scan | Toggles the global barcode listener |
| Recent prefix languages | Switch the active language prefix (shown when prefix feature is enabled) |
| Exit | Quits the app |

## Scanner menu

| Item | Description |
|------|-------------|
| Pause / Resume auto-scan | Temporarily disables the global listener |
| Speed check… | Measures your scanner's inter-key timing and sets the detection threshold automatically |

## Language

The UI language is configurable under **File → Preferences → Language…**. English and Dutch are included. The selected language is saved to `settings.json` and restored on next launch.

## Language prefix

Enable the language prefix feature under **Prefix → Language prefix…**. When enabled, an ISO 3166-1 alpha-2 country code is prepended to every scanned barcode before file lookup — e.g. barcode `12345678` with prefix `EN` looks for `EN-12345678.*` in the folder.

A dropdown appears in the scan area for quick prefix switching. The last five used prefix languages are saved to `settings.json` and accessible from the tray right-click menu.

## Updates

The app checks for a new version on startup. If one is available, a dialog offers:

- **Update now** — downloads the new `.exe` in the background and replaces the current one automatically after exit (only available when running as a built `.exe`)
- **Download manually** — opens the GitHub release page in the browser
- **Later** — dismisses until next startup

You can also trigger a manual check via **Help → Check for updates**.

The update channel (**Stable releases** or **Pre-releases**) is configurable under **File → Preferences → Update channel**.

## Project structure

```
scan-to-print/
  main.py                # Entry point — run this to launch the app
  app.py                 # Main Tkinter window and UI logic
  printer.py             # Printer enumeration and print job (pywin32 + pypdfium2 + Pillow)
  scanner.py             # Global pynput keyboard listener (timing-based detection)
  settings.py            # Persistent settings in %APPDATA%/ScanToPrint/settings.json
  speedcheck.py          # Scanner speed check window
  updater.py             # GitHub release check and in-app self-update
  i18n.py                # Internationalisation — loads strings from locales/<lang>.json
  language_window.py     # Language selection dialog (UI language + language prefix)
  tray.py                # System tray icon and right-click menu
  file_version_info.py   # Windows version resource embedded in the exe
  locales/               # UI string translations (en.json, nl.json)
  version.py             # __version__ placeholder, overwritten by CI at build time
  build.py               # Build script — outputs to dist/ with version+branch in the exe name
  test_scan.py           # Simulates USB scanner input for testing without hardware
  requirements.txt       # Python dependencies
  ScanToPrint.spec       # PyInstaller build spec
  images/                # App icons
```

## Building a standalone .exe

```
python build.py
```

Output: `dist/ScanToPrint.exe` (main branch) or `dist/ScanToPrint <version> <branch>.exe` (other branches) — runs on Windows without Python installed.

## Testing without a scanner

```
python test_scan.py 12345678
```

Injects a barcode at scanner speed after a 3-second delay (time to switch focus).

## Notes

- The global keyboard listener detects scanner input by timing: all characters must arrive within the configured threshold (default 100ms). Human typing is slower and is ignored.
- The app prints directly to the selected printer via `pywin32`; it does not change the Windows system default printer.
- Settings are saved to `%APPDATA%\ScanToPrint\settings.json`. Use **File → Preferences → Open settings file…** to inspect or edit them.
