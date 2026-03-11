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
- `pypdfium2` — PDF rendering and printing (planned — Feature #9)
- `Pillow` — image printing (planned — Feature #9)
- `pystray` — system tray icon (planned — Feature #7)
- `requests` — GitHub update check and in-app self-update
- `pyinstaller` — for building a standalone `.exe`

## Running the app

```
python main.py
```

## Usage

1. **Select folder** — choose the folder containing your files. Files must be named after their barcode value (e.g. `12345678.pdf`, `ABC-999.pdf`).
2. **Select printer** — pick from the list of installed Windows printers. The last used printer is pre-selected on startup; falls back to the Windows default printer.
3. **Scan** — point your USB barcode scanner at a barcode. The global listener detects scanner input automatically — no need to click the app first.

You can also type a barcode manually in the entry box and press Enter.

If multiple files share the same barcode name (different extensions), a dialog lets you choose which to print.

Settings (folder, printer, window size, auto-scan state, scanner threshold) are saved automatically to `%APPDATA%\ScanToPrint\settings.json`.

## Scanner menu

| Item | Description |
|------|-------------|
| Pause / Resume auto-scan | Temporarily disables the global listener |
| Speed check… | Measures your scanner's inter-key timing and sets the detection threshold automatically |

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
  main.py            # Entry point — run this to launch the app
  app.py             # Main Tkinter window and UI logic
  printer.py         # Printer enumeration and print job (pywin32)
  scanner.py         # Global pynput keyboard listener (timing-based detection)
  settings.py        # Persistent settings in %APPDATA%/ScanToPrint/settings.json
  speedcheck.py      # Scanner speed check window
  updater.py         # GitHub release check and in-app self-update
  version.py         # __version__ placeholder, overwritten by CI at build time
  build.py           # Branch-aware build script (dist/<branch>/ScanToPrint.exe)
  test_scan.py       # Simulates USB scanner input for testing without hardware
  requirements.txt   # Python dependencies
  ScanToPrint.spec   # PyInstaller build spec
  images/            # App icons
```

## Building a standalone .exe

```
python build.py
```

Output: `dist/<branch>/ScanToPrint.exe` — runs on Windows without Python installed.

## Testing without a scanner

```
python test_scan.py 12345678
```

Injects a barcode at scanner speed after a 3-second delay (time to switch focus).

## Notes

- The global keyboard listener detects scanner input by timing: all characters must arrive within the configured threshold (default 100ms). Human typing is slower and is ignored.
- The app prints directly to the selected printer via `pywin32`; it does not change the Windows system default printer.
- Settings are saved to `%APPDATA%\ScanToPrint\settings.json`. Use **File → Preferences → Open settings file…** to inspect or edit them.
