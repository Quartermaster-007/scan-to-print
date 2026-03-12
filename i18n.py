"""
Internationalisation — loads locale strings from locales/<lang>.json.

Usage:
    import i18n
    i18n.load("nl")
    label = i18n.t("btn_browse")                  # simple key
    msg   = i18n.t("status_printing", file="x.pdf", printer="HP")  # with placeholders
"""
import json
import os

_BASE = os.path.join(os.path.dirname(__file__), "locales")

_lang: dict = {}
_fallback: dict = {}


def _load_file(code: str) -> dict:
    path = os.path.join(_BASE, f"{code}.json")
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def load(lang_code: str = "en") -> None:
    """Load the requested language, keeping English as fallback."""
    global _lang, _fallback
    _fallback = _load_file("en")
    _lang = _load_file(lang_code) if lang_code != "en" else {}


def t(key: str, **kwargs) -> str:
    """Return the translated string for *key*, with optional format placeholders."""
    text = _lang.get(key) or _fallback.get(key, key)
    return text.format(**kwargs) if kwargs else text
