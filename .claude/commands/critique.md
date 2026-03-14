Review the scan-to-print Python desktop app (files: `main.py`, `app.py`, `printer.py`, `scanner.py`, `settings.py`, `speedcheck.py`, `updater.py`). For each file, assess:

**Code quality**
- Dead code, unused imports, or variables
- Functions that are too long or do too many things (aim for single responsibility)
- Repeated logic that should be extracted
- Naming clarity (variables, functions, classes)

**Error handling**
- Bare `except` clauses or overly broad catches
- Missing error handling at system boundaries (file I/O, print jobs, network calls in `updater.py`, registry/settings reads)
- Error messages that expose internal details vs. user-friendly messages

**Threading and concurrency**
- Race conditions between the `pynput` keyboard listener thread and the Tkinter main thread
- Any `tkinter` widget access from non-main threads (this is unsafe)
- Use of `after()` vs. direct calls for thread-safe UI updates

**Resource management**
- File handles, printer handles, and PDF documents properly closed (context managers)
- Listener lifecycle — started/stopped correctly on app exit

**Settings and persistence**
- Input validation before saving to `settings.json`
- Graceful degradation when settings file is missing or corrupt

**Security**
- Path traversal risk: is the barcode value sanitised before being used to construct a file path?
- Is user input ever passed to a shell command?

**Windows-specific**
- Any assumptions that break when run as a PyInstaller `.exe` (e.g. `__file__`, `sys.argv[0]`, working directory)
- Correct use of `%APPDATA%` via `os.environ` or `pathlib`

**UX**
- Is the app state always visible — does the user know if auto-scan is on, which printer is selected, and whether the folder is set?
- Is feedback immediate and unambiguous after a scan (success, no file found, print error)?
- Are error messages actionable — do they tell the user what to do next, not just what went wrong?
- Are destructive or irreversible actions (e.g. clearing history) confirmed before executing?
- Is the tray icon behaviour consistent with Windows conventions (left-click to restore, right-click for menu)?
- Are controls discoverable — would a first-time user understand how to set up and use the app without a manual?
- Is the speed check flow (threshold calibration) clear enough for a non-technical operator?

Output findings grouped by file or area, severity (high / medium / low), and a short recommended fix for each. Skip style nitpicks unless they affect readability significantly.
