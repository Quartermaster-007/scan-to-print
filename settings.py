"""
Persistent settings stored in %APPDATA%/ScanToPrint/settings.json.
"""
import json
import os

_APPDATA = os.environ.get("APPDATA", os.path.expanduser("~"))
_SETTINGS_DIR = os.path.join(_APPDATA, "ScanToPrint")
_SETTINGS_FILE = os.path.join(_SETTINGS_DIR, "settings.json")

_DEFAULTS = {
    "folder": "",
    "printer": "",
    "window_width": 0,
    "window_height": 0,
    "auto_scan": True,
    "threshold_ms": 100,
}


def load() -> dict:
    """Return settings dict, falling back to defaults for missing keys."""
    try:
        with open(_SETTINGS_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    return {**_DEFAULTS, **data}


def save(settings: dict) -> None:
    """Persist settings dict to disk."""
    os.makedirs(_SETTINGS_DIR, exist_ok=True)
    with open(_SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def get_path() -> str:
    """Return the absolute path to the settings file."""
    return _SETTINGS_FILE
