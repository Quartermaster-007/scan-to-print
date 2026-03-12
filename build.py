"""
Build script — outputs all builds to dist/ with a name that encodes
the version and branch for non-main builds.

Output name format:
    main branch  →  ScanToPrint.exe
    other branch →  ScanToPrint <version> <branch>.exe

Usage:
    python build.py                        # stamps version as 9999.0.0 (dev sentinel)
    python build.py --version 2026.03.11   # stamps a specific version
    python build.py --clean-tray           # wipe Windows tray icon history and exit
"""
import argparse
import os
import subprocess
import sys


def current_branch():
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True,
    )
    return result.stdout.strip().replace("/", "-")


def clean_tray_history():
    """
    Delete IconStreams and PastIconsStream from the registry.

    These binary blobs store every tray icon Windows has ever seen.
    There is no documented way to remove a single app's entry, so the
    entire history is cleared.  Windows rebuilds it automatically on
    the next Explorer restart.

    NOTE: this affects ALL apps, not just ScanToPrint.
    """
    import winreg
    key_path = (
        r"Software\Classes\Local Settings\Software\Microsoft"
        r"\Windows\CurrentVersion\TrayNotify"
    )
    deleted = []
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, key_path, access=winreg.KEY_SET_VALUE
        ) as key:
            for value in ("IconStreams", "PastIconsStream"):
                try:
                    winreg.DeleteValue(key, value)
                    deleted.append(value)
                except FileNotFoundError:
                    pass  # already absent
    except FileNotFoundError:
        print("TrayNotify registry key not found — nothing to clean.")
        return

    if deleted:
        print(f"Deleted: {', '.join(deleted)}")
        print("Restart Windows Explorer (or reboot) to apply the change.")
    else:
        print("Nothing to delete — tray history was already empty.")


parser = argparse.ArgumentParser()
parser.add_argument("--version", default="9999.0.0", help="Version string to stamp into version.py")
parser.add_argument("--clean-tray", action="store_true", help="Wipe Windows tray icon history and exit")
args = parser.parse_args()

if args.clean_tray:
    clean_tray_history()
    sys.exit(0)

# Stamp version.py so the built exe doesn't trigger the updater
with open("version.py", "w", encoding="utf-8") as f:
    f.write(f'# This file is overwritten by CI at build time.\n__version__ = "{args.version}"\n')

print(f"Stamped version: {args.version}")

branch = current_branch()
print(f"Building branch: {branch}")

subprocess.run(
    [
        sys.executable, "-m", "PyInstaller",
        "ScanToPrint.spec",
        "--noconfirm",
        "--distpath=dist",
    ],
    check=True,
)

if branch == "main":
    exe_name = "ScanToPrint"
else:
    exe_name = f"ScanToPrint {args.version} {branch}"
    os.replace("dist/ScanToPrint.exe", f"dist/{exe_name}.exe")

print(f"\nOutput: dist/{exe_name}.exe")
