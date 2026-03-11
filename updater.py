"""
GitHub release update checker with in-app self-update for the frozen exe.
"""
import os
import subprocess
import sys
import tempfile
import threading
import webbrowser
import tkinter as tk
from tkinter import messagebox, ttk

import requests

GITHUB_REPO = "Quartermaster-007/scan-to-print"
_API_STABLE = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
_API_ALL = f"https://api.github.com/repos/{GITHUB_REPO}/releases"
_HEADERS = {"Accept": "application/vnd.github+json"}

# Only offer in-app update when running as a frozen exe
_IS_FROZEN = getattr(sys, "frozen", False)


def _parse_version(tag: str) -> tuple:
    """'2026.03.11.1' → (2026, 3, 11, 1) padded to 4 elements. Never raises."""
    try:
        parts = [int(x) for x in tag.lstrip("v").split(".")]
        parts += [0] * (4 - len(parts))
        return tuple(parts[:4])
    except Exception:
        return (0, 0, 0, 0)


def _fetch_latest(channel: str) -> dict | None:
    """
    Return {"tag": str, "url": str, "download_url": str|None} or None on any error.
    download_url is only set when running as a frozen exe and the release has a
    ScanToPrint.exe asset attached.
    """
    try:
        if channel == "prerelease":
            resp = requests.get(_API_ALL, headers=_HEADERS, timeout=10)
            resp.raise_for_status()
            releases = [r for r in resp.json() if not r.get("draft")]
            if not releases:
                return None
            latest = max(releases, key=lambda r: _parse_version(r["tag_name"]))
        else:
            resp = requests.get(_API_STABLE, headers=_HEADERS, timeout=10)
            resp.raise_for_status()
            latest = resp.json()
            if latest.get("draft"):
                return None

        download_url = None
        if _IS_FROZEN:
            for asset in latest.get("assets", []):
                if asset["name"].lower() == "scantoprint.exe":
                    download_url = asset["browser_download_url"]
                    break

        return {
            "tag": latest["tag_name"],
            "url": latest["html_url"],
            "download_url": download_url,
        }
    except Exception:
        return None


def _launch_swap_script(new_exe: str, current_exe: str) -> None:
    """Write and launch a .bat that replaces the running exe after it exits."""
    exe_dir = os.path.dirname(current_exe)
    bat = os.path.join(tempfile.gettempdir(), "stp_update.bat")
    with open(bat, "w", encoding="ascii") as f:
        f.write(
            "@echo off\n"
            ":wait\n"
            'tasklist | find /i "ScanToPrint.exe" >nul 2>&1\n'
            "if not errorlevel 1 ( timeout /t 1 /nobreak >nul & goto wait )\n"
            f'copy /y "{new_exe}" "{current_exe}"\n'
            f'start "" /D "{exe_dir}" "{current_exe}"\n'
            'del "%~f0"\n'
        )
    # Strip PyInstaller's internal env vars and stale MEI paths so the new
    # exe extracts fresh instead of reusing the (already-deleted) MEI dir.
    clean_env = os.environ.copy()
    for key in list(clean_env):
        if key.startswith(("_MEI", "_PYI")):
            del clean_env[key]
    path_parts = clean_env.get("PATH", "").split(os.pathsep)
    clean_env["PATH"] = os.pathsep.join(p for p in path_parts if "_MEI" not in p)

    subprocess.Popen(
        ["cmd", "/c", bat],
        creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP,
        env=clean_env,
    )


def _do_self_update(root: tk.Tk, download_url: str, tag: str) -> None:
    """Show a progress dialog, download the new exe, then swap and restart."""
    current_exe = sys.executable
    new_exe = os.path.join(tempfile.gettempdir(), "ScanToPrint_new.exe")

    dlg = tk.Toplevel(root)
    dlg.title("Downloading update")
    dlg.resizable(False, False)
    dlg.grab_set()
    dlg.protocol("WM_DELETE_WINDOW", lambda: None)  # block close during download

    tk.Label(dlg, text=f"Downloading version {tag}…", font=("TkDefaultFont", 10, "bold")).pack(
        padx=24, pady=(18, 8)
    )
    progress = ttk.Progressbar(dlg, length=320, mode="determinate")
    progress.pack(padx=24, pady=(0, 6))
    status_var = tk.StringVar(value="Connecting…")
    tk.Label(dlg, textvariable=status_var).pack(padx=24, pady=(0, 18))

    def _on_progress(downloaded: int, total: int) -> None:
        if total:
            progress.config(value=downloaded / total * 100)
            status_var.set(
                f"{downloaded / 1_048_576:.1f} / {total / 1_048_576:.1f} MB"
            )

    def _on_done() -> None:
        dlg.destroy()
        _launch_swap_script(new_exe, current_exe)
        os._exit(0)

    def _on_error(msg: str) -> None:
        dlg.destroy()
        messagebox.showerror(
            "Update failed",
            f"Download failed:\n{msg}\n\nPlease download the update manually.",
        )

    def _download() -> None:
        try:
            resp = requests.get(download_url, stream=True, timeout=60)
            resp.raise_for_status()
            total = int(resp.headers.get("content-length", 0))
            downloaded = 0
            with open(new_exe, "wb") as f:
                for chunk in resp.iter_content(chunk_size=65_536):
                    f.write(chunk)
                    downloaded += len(chunk)
                    root.after(0, _on_progress, downloaded, total)
            root.after(0, _on_done)
        except Exception as exc:
            root.after(0, _on_error, str(exc))

    threading.Thread(target=_download, daemon=True).start()


def _show_update_dialog(root: tk.Tk, tag: str, url: str, download_url: str | None) -> None:
    dlg = tk.Toplevel(root)
    dlg.title("Update available")
    dlg.resizable(False, False)
    dlg.grab_set()

    tk.Label(dlg, text=f"Version {tag} is available.", font=("TkDefaultFont", 11, "bold")).pack(
        padx=24, pady=(18, 6)
    )
    if download_url:
        tk.Label(dlg, text="Would you like to update now?").pack(padx=24, pady=(0, 16))
    else:
        tk.Label(dlg, text="Open the download page to install manually?").pack(padx=24, pady=(0, 16))

    btn_frame = tk.Frame(dlg)
    btn_frame.pack(pady=(0, 18))

    def update_now() -> None:
        dlg.destroy()
        _do_self_update(root, download_url, tag)

    def download_manually() -> None:
        dlg.destroy()
        webbrowser.open(url)

    if download_url:
        ttk.Button(btn_frame, text="Update now", command=update_now).pack(side="left", padx=6)
    ttk.Button(btn_frame, text="Download manually", command=download_manually).pack(side="left", padx=6)
    ttk.Button(btn_frame, text="Later", command=dlg.destroy).pack(side="left", padx=6)


def _show_up_to_date() -> None:
    messagebox.showinfo("No updates", "You are up to date.")


def check_for_updates(
    root: tk.Tk,
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
    def _run() -> None:
        result = _fetch_latest(channel)
        if result is None:
            return
        if _parse_version(result["tag"]) > _parse_version(current_version):
            root.after(
                0, _show_update_dialog,
                root, result["tag"], result["url"], result["download_url"],
            )
        elif not silent:
            root.after(0, _show_up_to_date)

    threading.Thread(target=_run, daemon=True).start()
