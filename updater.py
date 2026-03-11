"""
GitHub release update checker.
"""
import threading
import webbrowser
from tkinter import messagebox

import requests

GITHUB_REPO = "Quartermaster-007/scan-to-print"
_API_STABLE = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
_API_ALL = f"https://api.github.com/repos/{GITHUB_REPO}/releases"


def _parse_version(tag: str) -> tuple:
    """'2026.03.11.1' → (2026, 3, 11, 1) padded to 4 elements. Never raises."""
    try:
        parts = [int(x) for x in tag.lstrip("v").split(".")]
        parts += [0] * (4 - len(parts))
        return tuple(parts[:4])
    except Exception:
        return (0, 0, 0, 0)


def _fetch_latest(channel: str) -> dict | None:
    """Return {"tag": str, "url": str} for the latest release, or None on error."""
    try:
        headers = {"Accept": "application/vnd.github+json"}
        if channel == "prerelease":
            resp = requests.get(_API_ALL, headers=headers, timeout=10)
            resp.raise_for_status()
            releases = [r for r in resp.json() if not r.get("draft")]
            if not releases:
                return None
            latest = max(releases, key=lambda r: _parse_version(r["tag_name"]))
        else:
            resp = requests.get(_API_STABLE, headers=headers, timeout=10)
            resp.raise_for_status()
            latest = resp.json()
            if latest.get("draft"):
                return None

        return {
            "tag": latest["tag_name"],
            "url": latest["html_url"],
        }
    except Exception:
        return None


def _show_update_dialog(tag: str, url: str) -> None:
    answer = messagebox.askyesno(
        "Update available",
        f"Version {tag} is available.\n\nOpen the download page now?",
    )
    if answer:
        webbrowser.open(url)


def _show_up_to_date_dialog() -> None:
    messagebox.showinfo("No updates", "You are up to date.")


def check_for_updates(
    root,
    current_version: str,
    channel: str,
    *,
    silent: bool = True,
) -> None:
    """
    Check for updates in a daemon thread.

    silent=True  — only show a dialog if a newer version is found (startup check).
    silent=False — also show "up to date" if nothing newer found (manual check).
    """
    def _run():
        result = _fetch_latest(channel)
        if result is None:
            return

        if _parse_version(result["tag"]) > _parse_version(current_version):
            root.after(0, _show_update_dialog, result["tag"], result["url"])
        elif not silent:
            root.after(0, _show_up_to_date_dialog)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
