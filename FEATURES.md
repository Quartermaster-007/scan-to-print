# Feature Planning — scan-to-print

Fill in the details under each feature before work begins. Leave a section blank or mark it `skip` if you don't want it built.

---

## Current state

The core app is fully working:
- Folder selection, printer selection, barcode input (USB scanner or keyboard)
- Finds matching file by barcode name, disambiguates if multiple extensions exist
- Prints via Windows ShellExecute
- Persistent settings in `%APPDATA%\ScanToPrint\settings.json` (#3 ✅)
- Global keyboard listener (pynput) with timing-based barcode detection (#10 ✅)
- Pause/resume toggle + scanner speed check with auto-calibration (#10 ✅)

---

## Feature 1 — Print history / log

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

## Feature 2 — Sound / visual feedback on scan

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

## Feature 3 — Persistent settings ✅ Implemented

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

## Feature 4 — Multiple folder support

Allow the app to search across more than one folder (e.g. one folder per document type or department).

**Questions to answer before building:**
- UI: a list of folders the user can add/remove, or a single folder with a "also search subfolders" toggle?
- If a match is found in more than one folder, how should it be handled? Show a picker? Use priority order?
- Should the folder list persist between sessions?

**Your answers:**
- Currently no need to add more folders.

---

## Feature 5 — Print copies / print options

Let the user specify how many copies to print, or choose a different paper tray/orientation.

**Questions to answer before building:**
- Is number of copies the only option needed, or also paper size, orientation, duplex?
- Should this be a global setting, or per-scan (a prompt before each print)?
- Are there specific printer capabilities you want to expose?

**Your answers:**
- The main purpose is to use this app for label printers, but regular printers is also an option. Can we use the default printer option window in Windows to configure any print settings?
- The print setting should be a global setting for that session. If there are any specifics to be saved, then sotre those in `settings.json` to be used between sessions.
- By default the app should just print 1 copy. But if needed the user should be able to adjust a copy number input, which reverts back to 1 after a successfull scan-to-print.

---

## Feature 6 — Barcode prefix / suffix filtering

Some scanners add a prefix or suffix to every scan (e.g. `]C1` for Code 128 AIM identifiers). Strip or remap these automatically.

**Questions to answer before building:**
- Do your scanners add any prefix or suffix today?
- Should stripping be automatic (detect and remove known AIM identifiers) or manual (user defines what to strip)?
- Should the app also support remapping — e.g. replace a prefix with a folder path?

**Your answers:**
- No specific prefix or suffix fitering needs to be done. We assume that the user has properly setup the barcode scanner for this usecase.

---

## Feature 7 — System tray / minimise to tray

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

## Feature 8 — Auto-start on Windows login

Register the app to launch automatically when Windows starts.

**Questions to answer before building:**
- Should this be an opt-in toggle inside the app, or always on?
- Launch minimised to tray, or open the main window?
- Any specific Windows user accounts this needs to work for (single user, all users)?

**Your answers:**
- Currently no need to add suggested feature.

---

## Feature 9 — Network/shared printer support improvements

Currently, `SetDefaultPrinter` is called before each print, which is a Windows side effect. A cleaner approach would print directly to a named printer without changing the system default.

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

---

## Feature 10 — Auto scan-to-print ✅ Implemented

The app should monitor input from the barcode scanner and attempt to print any document that matches its input. No need to first highlight the input box and therefore also work when the app is minimized to the system tray.

**Your answers:**
- Use timing-based detection to distinguish barcode scanner input from regular keyboard typing.

**Implementation note:** Use `pynput` to install a global keyboard listener (works even when the app has no focus / is in the tray). Barcode scanners send all characters within ~50ms followed by Enter; human typing is much slower. The listener accumulates keystrokes and measures inter-key delay — if a sequence ends with Enter and all characters arrived within the threshold, it is treated as a barcode scan. Regular keyboard input is ignored. The pause/resume toggle in the tray menu (Feature 7) will enable/disable this listener.

**Implementation notes:**
- `scanner.py` — `BarcodeScanner` class wraps a `pynput.keyboard.Listener` in a daemon thread; configurable `threshold_ms` (default 100ms); `MIN_LENGTH = 3` to ignore stray Enter presses; fires callback via `root.after(0, ...)` for thread safety
- Scanner menu in menubar: "Pause / Resume auto-scan" toggle + "Speed check…"
- `●` green/grey dot indicator with "Auto-scan" label shows current state
- `speedcheck.py` — modal window that measures actual scanner inter-key timing and suggests a threshold with 50% margin (min +20ms), rounded to 10ms; Apply & Save / Reset to Default / Close
- `auto_scan` and `threshold_ms` both persisted in `settings.json`
- `test_scan.py` — injects keystrokes via `pynput.keyboard.Controller` at 20ms intervals for testing without hardware

---

## Feature 11 — Language selection for UI

User can select the language used in the app for all the strings and logs. Include English and Dutch as options at first. In the menubar, under 'File', then 'Preferences', include a button for language selection that opens a new UI screen for selection of available languages. Save the used language to `settings.json` and use the store value whenever available.

**Implementation note:** All UI strings (labels, buttons, status messages, log entries, tray menu items) will be stored in a `locales/` dictionary (e.g. `locales/en.json`, `locales/nl.json`). English is the fallback for any untranslated string. The language screen will show a simple list with radio buttons.

---

## Feature 12 — Language selection for prefix

User has to enable the feature that prefixes a iso 3166-1 alpha-2 country code to the scanned barcode. That way the folder can contain multiple language versions, and the app prints the selected language version. In the menubar, under 'Prefix', include a button for language selection that opens the same UI window of feature #11. The left side will show UI languages and the right side should include a toggle for the feature and a list of languages to select. If the feature is turned on, then include a new dropdown menu in the scan section to quickly select a different language. The last five selected languages are saved to `settings.json` so they can be referenced in the right-click menu of the system tray and in the menubar under 'Prefix'.

The list of languages shown should follow the format:
* English (EN)
* German (DE)
* French (FR)
* Dutch (NL)

**Your answers:**
- Filename separator: **hyphen** — e.g. barcode `12345678` with prefix `EN` looks for `EN-12345678.*` in the folder.

---

## Feature 13 — App updates via Github

Build the Windows executable on Github and host releases on there. The app should check for new versions of the app and download that new version. Versioning should be done in the format yyyy.mm.dd.

**Your answers:**
- Check on startup; if a newer version is found, prompt the user with a dialog to download and restart. No auto-download.

**Implementation note:**
- Version format: `yyyy.mm.dd` (compare lexicographically — newer = greater string).
- On startup, call the GitHub releases API (`https://api.github.com/repos/Quartermaster-007/scan-to-print/releases/latest`) to get the latest tag.
- If newer than the running version, show a dialog: "Version X.X.X is available. Download now?" — opens the release page in the browser.
- GitHub Actions workflow: build `ScanToPrint.exe` via PyInstaller on push to `main`, publish as a GitHub Release tagged `yyyy.mm.dd`.

---

## Priority order

Once you've filled in the features you want, list them here in the order you'd like them built:

1. #3 — Persistent settings
2. #10 — Auto scan-to-print
3. #13 — App updates via Github
4. #11 — Language selection for UI
5. #1 — Print history / log
6. #2 — Sound / visual feedback on scan
7. #9 — Network/shared printer support improvements
8. #5 — Print copies / print options
9. #7 — System tray / minimise to tray
10. #12 — Language selection for prefix