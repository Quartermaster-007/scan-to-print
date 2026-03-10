"""
Build script — outputs ScanToPrint.exe to dist/<branch>/ so builds
from different branches don't overwrite each other.

Usage:  python build.py
"""
import subprocess
import sys


def current_branch():
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True
    )
    # Sanitise for use as a directory name
    return result.stdout.strip().replace("/", "-")


branch = current_branch()
print(f"Building branch: {branch}")

subprocess.run(
    [
        sys.executable, "-m", "PyInstaller",
        "ScanToPrint.spec",
        "--noconfirm",
        f"--distpath=dist/{branch}",
    ],
    check=True,
)

print(f"\nOutput: dist/{branch}/ScanToPrint.exe")
