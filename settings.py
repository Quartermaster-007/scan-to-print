"""
Persistent settings stored in %APPDATA%/ScanToPrint/settings.json.
"""
import json
import os

_APPDATA = os.environ.get("APPDATA", os.path.expanduser("~"))
_SETTINGS_DIR = os.path.join(_APPDATA, "ScanToPrint")
_SETTINGS_FILE = os.path.join(_SETTINGS_DIR, "settings.json")

_DEFAULTS = {
    "workspace": {
        "folder": "",
        "printer": "",
    },
    "ui": {
        "window_width": 0,
        "window_height": 0,
        "language": "en",
    },
    "scanner": {
        "auto_scan": True,
        "threshold_ms": 100,
    },
    "updates": {
        "channel": "stable",
    },
    "prefix": {
        "enabled": False,
        "language": "EN",
        "recent": [],
    },
}


def _deep_merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def _validate(s: dict) -> dict:
    """Clamp/correct settings values to valid ranges."""
    sc = s.get("scanner", {})
    try:
        sc["threshold_ms"] = max(1, int(sc.get("threshold_ms", 100)))
    except (TypeError, ValueError):
        sc["threshold_ms"] = 100

    ui = s.get("ui", {})
    for key in ("window_width", "window_height"):
        try:
            ui[key] = max(0, int(ui.get(key, 0)))
        except (TypeError, ValueError):
            ui[key] = 0
    if not isinstance(ui.get("language"), str) or not ui["language"]:
        ui["language"] = "en"

    up = s.get("updates", {})
    if up.get("channel") not in ("stable", "prerelease"):
        up["channel"] = "stable"

    return s


def load() -> dict:
    """Return settings dict, falling back to defaults for missing keys."""
    try:
        with open(_SETTINGS_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    return _validate(_deep_merge(_DEFAULTS, data))


def save(s: dict) -> None:
    """Persist settings dict to disk."""
    os.makedirs(_SETTINGS_DIR, exist_ok=True)
    with open(_SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=2)


def get_path() -> str:
    """Return the absolute path to the settings file."""
    return _SETTINGS_FILE
