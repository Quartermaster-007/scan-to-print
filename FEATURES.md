# Feature Planning — scan-to-print

Fill in the details under each feature before work begins. Leave a section blank or mark it `skip` if you don't want it built.

---

## Current state

The core app is fully working:
- Folder selection, printer selection, barcode input (USB scanner or keyboard)
- Finds matching file by barcode name, disambiguates if multiple extensions exist
- Prints via Windows ShellExecute
- Persistent settings in `%APPDATA%\ScanToPrint\settings.json` ✅
- Global keyboard listener (pynput) with timing-based barcode detection ✅
- Pause/resume toggle + scanner speed check with auto-calibration ✅

---

## Print history / log

Show a record of every scan attempt (barcode scanned, file matched, printer used, result, timestamp).

**Questions to answer before building:**
- Where should the log live? Options: in-app scrollable list, a `.csv`/`.log` file written to disk, or both?
- How many entries to keep? Should old entries be pruned automatically?
- Should failed scans (no file found, print error) be logged too?
- Should the log persist between sessions (saved to disk) or reset on restart?
- Any export/clear button needed?

**Your answers:**
- Add a scrollable list in the tkinter with log messages for that current session. No need to write logs to disk.
- Keep all entries for the current session. If needed for performance/optimalization, then keep about the last 50 logs.
- Yes, the log should also inlcude any errors.
- Only keep the logs for the current session. No need to write to disk.
- No need to export.

---

## Sound / visual feedback on scan

Play a sound or flash the window when a scan succeeds or fails — useful in noisy warehouse environments where the operator can't read the screen.

**Questions to answer before building:**
- Success sound: system beep, custom `.wav` file, or no sound?
- Failure sound (no file found / print error): different sound, or just visual?
- Visual feedback: flash the status bar colour (green/red), or a full-window overlay?
- Should feedback be configurable (on/off toggle)?

**Your answers:**
- Success will result in a print, so no need to add a success sound.
- Failure sound would be useful. Use 'C:\Windows\Media\Windows Foreground.wav' that is always present on a Windows 10 and 11 machine.
- No visual feedback needed.

---

## Persistent settings ✅ Implemented

Remember the last-used folder and printer between sessions so the user doesn't have to reconfigure on every launch.

**Questions to answer before building:**
- Where to store settings? Options: `settings.json` next to the `.exe`, Windows registry, `%APPDATA%` folder.
- Should the app also remember window size/position?
- Any other state worth persisting (e.g. last selected printer, preferred scan mode)?

**Your answers:**
- Yes, implement a `settings.json`. I think it would make most sense if it is stored in the `%APPDATA%` folder.
- Include a link to the `settings.json` in the 'File' section of the menubar.

Settings to store, based on the core functionallity and not including any new features:
- Window size
- Last used folder and printer

**Implementation notes:**
- `settings.py` reads/writes `%APPDATA%\ScanToPrint\settings.json`
- Keys: `folder`, `printer`, `window_width`, `window_height`, `auto_scan`, `threshold_ms`
- Printer auto-selection order: saved → Windows default → first in list
- File menu added with "Open settings file" (opens in default editor) and "Exit"
- Window size is restored on startup; saved on close


---

## Multiple folder support

Allow the app to search across more than one folder (e.g. one folder per document type or department).

**Questions to answer before building:**
- UI: a list of folders the user can add/remove, or a single folder with a "also search subfolders" toggle?
- If a match is found in more than one folder, how should it be handled? Show a picker? Use priority order?
- Should the folder list persist between sessions?

**Your answers:**
- Currently no need to add more folders.

---

## Print copies / print options ✅ Implemented

Let the user specify how many copies to print, or choose a different paper tray/orientation.

**Questions to answer before building:**
- Is number of copies the only option needed, or also paper size, orientation, duplex?
- Should this be a global setting, or per-scan (a prompt before each print)?
- Are there specific printer capabilities you want to expose?

**Your answers:**
- The main purpose is to use this app for label printers, but regular printers is also an option. Can we use the default printer option window in Windows to configure any print settings?
- The print setting should be a global setting for that session. If there are any specifics to be saved, then sotre those in `settings.json` to be used between sessions.
- By default the app should just print 1 copy. But if needed the user should be able to adjust a copy number input, which reverts back to 1 after a successfull scan-to-print.

**Implementation notes:**
- A dedicated "3. Print settings" frame sits between printer selection and scan; scan is now "4. Scan barcode"
- **Copies** — `self._copies` (`IntVar`, default 1); `ttk.Spinbox` (range 1–99); resets to 1 after each successful print
- **Printer settings** — "Printer settings..." button opens Windows' native `DocumentProperties` dialog for the selected printer (paper, tray, orientation, duplex — whatever the driver exposes); the resulting DEVMODE is stored in `self._devmode` (session-only, not persisted)
- **Reset to defaults** — clears `self._devmode`; button is disabled when no custom settings are active; re-enabled when `DocumentProperties` is confirmed with OK
- `self._devmode` is cleared automatically when the printer selection changes (DEVMODE is printer-specific)
- `printer.py` — `print_file`, `_print_pdf`, `_print_image` each accept `copies: int = 1` and `devmode=None`; `_make_printer_dc` uses `win32gui.CreateDC("WINSPOOL", printer, devmode)` when a DEVMODE is set, otherwise falls back to `win32ui.CreatePrinterDC`
- PDF pages are pre-rendered once and the page sequence repeated N times in a single GDI job; image `Dib` is created once and drawn N times

---

## Barcode prefix / suffix filtering

Some scanners add a prefix or suffix to every scan (e.g. `]C1` for Code 128 AIM identifiers). Strip or remap these automatically.

**Questions to answer before building:**
- Do your scanners add any prefix or suffix today?
- Should stripping be automatic (detect and remove known AIM identifiers) or manual (user defines what to strip)?
- Should the app also support remapping — e.g. replace a prefix with a folder path?

**Your answers:**
- No specific prefix or suffix fitering needs to be done. We assume that the user has properly setup the barcode scanner for this usecase.

---

## System tray / minimise to tray

Allow the app to run minimised in the Windows system tray so it stays available without taking up taskbar space.

**Questions to answer before building:**
- Should closing the window hide to tray (with a tray icon to restore), or exit the app?
- Any tray right-click menu items needed (e.g. Open, Exit)?
- Should a tray notification pop up on successful print?

**Your answers:**
- Exiting the app should really close the app, but when minimizing the app, the app should not remain in the regular task bar and simply turn to the system tray.
- Include a popup message for any errors.

Right-click menu should include
- Restore app, opening the normal app UI.
- Exit app.
- Stop/resume automatic scan-to-print functionallity.
- Select any of the last 5 used languages.

---

## Auto-start on Windows login

Register the app to launch automatically when Windows starts.

**Questions to answer before building:**
- Should this be an opt-in toggle inside the app, or always on?
- Launch minimised to tray, or open the main window?
- Any specific Windows user accounts this needs to work for (single user, all users)?

**Your answers:**
- Currently no need to add suggested feature.

---

## Direct silent printing ✅ Implemented

Currently, `SetDefaultPrinter` is called before each print and `ShellExecute` is used to trigger printing, which opens the application's print dialog and temporarily changes the system default printer. The fix is to print directly to a named printer without any UI or side effects.

**Questions to answer before building:**
- Is the current side effect (temporarily changing default printer) causing any real problems in your environment?
- Do you use network printers (UNC paths like `\\server\printer`)?
- Would you want a "test print" button to verify printer connectivity?
- What file types will the app primarily print?

**Your answers:**
- Changing the default printer is not desired.
- No network printer is currently used.
- No test button, keep the app minimal as possible.
- Primary file types: **PDF** and **images (PNG, JPG)**.

The logic for selecting the printer should be:
1. Select the last used printer from `settings.json`.
2. If printer of `settings.json` is empty or not found, select the default Windows printer.
3. If the user wants to use a different printer or no default printer is set, then use a drop-down menu to select a printer and save it to `settings.json` as last used printer.

**Implementation note:** `ShellExecute` with the `"print"` verb cannot target a specific printer — it always uses the Windows system default. To print to a named printer without changing the system default, the approach will be:
- **PDF**: `pypdfium2` (Apache 2.0) renders each page to a bitmap in-process, sent to the named printer via `win32print` / GDI. No external exe, no subprocess overhead.
- **Images (PNG, JPG)**: `Pillow` opens the image and sends it to the named printer via `win32print` / GDI.
- Both are pure pip dependencies — no bundled executables, keeping the `.exe` size minimal.

**Implementation notes:**
- `printer.py` — `print_file(file_path, printer_name)` dispatches to `_print_pdf` or `_print_image` based on file extension; raises `ValueError` for unsupported types
- **PDF**: `pypdfium2` opens the document, renders each page to a bitmap at the printer's native DPI (`LOGPIXELSX / 72`), converted to RGB PIL image and drawn via `ImageWin.Dib` to a GDI printer DC
- **Images (PNG, JPG, BMP, GIF, TIFF)**: `Pillow` opens and converts to RGB, drawn the same way
- Both paths use `win32ui.CreateDC().CreatePrinterDC(printer_name)` — `SetDefaultPrinter` is never called
- Pages/images are scaled to fit the printable area (`HORZRES` × `VERTRES`) while preserving aspect ratio
- `AbortDoc` is called on any exception so the printer does not receive a partial job
- `build.py` updated to stamp `version.py` before building (default `9999.0.0`) so local dev builds never trigger the updater; `--version` flag allows overriding

---

## Auto scan-to-print ✅ Implemented

The app should monitor input from the barcode scanner and attempt to print any document that matches its input. No need to first highlight the input box and therefore also work when the app is minimized to the system tray.

**Your answers:**
- Use timing-based detection to distinguish barcode scanner input from regular keyboard typing.

**Implementation note:** Use `pynput` to install a global keyboard listener (works even when the app has no focus / is in the tray). Barcode scanners send all characters within ~50ms followed by Enter; human typing is much slower. The listener accumulates keystrokes and measures inter-key delay — if a sequence ends with Enter and all characters arrived within the threshold, it is treated as a barcode scan. Regular keyboard input is ignored. The pause/resume toggle in the tray menu (System tray feature) will enable/disable this listener.

**Implementation notes:**
- `scanner.py` — `BarcodeScanner` class wraps a `pynput.keyboard.Listener` in a daemon thread; configurable `threshold_ms` (default 100ms); `MIN_LENGTH = 3` to ignore stray Enter presses; fires callback via `root.after(0, ...)` for thread safety
- Scanner menu in menubar: "Pause / Resume auto-scan" toggle + "Speed check…"
- `●` green/grey dot indicator with "Auto-scan" label shows current state
- `speedcheck.py` — modal window that measures actual scanner inter-key timing and suggests a threshold with 50% margin (min +20ms), rounded to 10ms; Apply & Save / Reset to Default / Close
- `auto_scan` and `threshold_ms` both persisted in `settings.json`
- `test_scan.py` — injects keystrokes via `pynput.keyboard.Controller` at 20ms intervals for testing without hardware

---

## Language selection for UI

User can select the language used in the app for all the strings and logs. Include English and Dutch as options at first. In the menubar, under 'File', then 'Preferences', include a button for language selection that opens a new UI screen for selection of available languages. Save the used language to `settings.json` and use the store value whenever available.

**Implementation note:** All UI strings (labels, buttons, status messages, log entries, tray menu items) will be stored in a `locales/` dictionary (e.g. `locales/en.json`, `locales/nl.json`). English is the fallback for any untranslated string. The language screen will show a simple list with radio buttons.

---

## Language prefix

User has to enable the feature that prefixes a iso 3166-1 alpha-2 country code to the scanned barcode. That way the folder can contain multiple language versions, and the app prints the selected language version. In the menubar, under 'Prefix', include a button for language selection that opens the same UI window as Language selection for UI. The left side will show UI languages and the right side should include a toggle for the feature and a list of languages to select. If the feature is turned on, then include a new dropdown menu in the scan section to quickly select a different language. The last five selected languages are saved to `settings.json` so they can be referenced in the right-click menu of the system tray and in the menubar under 'Prefix'.

The list of languages shown should follow the format:
* English (EN)
* German (DE)
* French (FR)
* Dutch (NL)

**Your answers:**
- Filename separator: **hyphen** — e.g. barcode `12345678` with prefix `EN` looks for `EN-12345678.*` in the folder.

---

## App updates via Github ✅ Implemented

Build the Windows executable on Github and host releases on there. The app should check for new versions of the app and download that new version. Versioning should be done in the format yyyy.mm.dd.

**Your answers:**
- Check on startup; if a newer version is found, prompt the user with a dialog to download and restart. No auto-download.

**Implementation notes:**
- `version.py` — `__version__` placeholder (`"0.0.0"`), overwritten by CI at build time; imported by `app.py` for the window title and update check.
- `updater.py` — daemon thread fetches `/releases/latest` (stable channel) or `/releases` (pre-release channel); compares version tuples; shows a dialog with up to three buttons:
  - **Update now** (only when running as frozen exe AND release has a `ScanToPrint.exe` asset) — downloads to `%TEMP%`, writes a `.bat` swap script, launches it, exits; the script waits for the old process to die, copies the new exe over the old one, and relaunches.
  - **Download manually** — opens the GitHub release page in the browser.
  - **Later** — dismisses.
- `silent=True` on startup (no dialog if already up to date); `silent=False` for **Help → Check for updates** (shows "You are up to date" too).
- Settings key `updates.channel` (`"stable"` | `"prerelease"`) selectable via **File → Preferences → Update channel**.
- Window title updated to `"Scan to Print — {__version__}"`.
- **Help** menu added: "Check for updates" + "About Scan to Print" (version, GitHub link, MIT license).
- Settings restructured from flat keys to nested groups: `workspace` (folder, printer), `ui` (window_width, window_height), `scanner` (auto_scan, threshold_ms), `updates` (channel). Deep merge ensures partial overrides don't wipe sibling defaults.
- `.github/workflows/release.yml` — `windows-latest`: checkout → stamp `version.py` → pip install → PyInstaller → `softprops/action-gh-release@v2`; triggered by tag push `yyyy.mm.dd*` or `workflow_dispatch` (version string + prerelease boolean inputs).
- Version format: `yyyy.mm.dd` or `yyyy.mm.dd.N` for same-day builds; compared as numeric tuples.
- `GITHUB_TOKEN` automatic — no extra secrets needed.

---

## Priority order

Once you've filled in the features you want, list them here in the order you'd like them built:

1. Persistent settings
2. Auto scan-to-print
3. App updates via Github
4. Direct silent printing
5. Print copies / print options
6. Language selection for UI
7. Print history / log
8. Sound / visual feedback on scan
9. System tray / minimise to tray
10. Language prefix
