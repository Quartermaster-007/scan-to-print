"""
Build script — outputs ScanToPrint.exe to dist/<branch>/ so builds
from different branches don't overwrite each other.

Usage:
    python build.py                        # stamps version as 9999.0.0 (dev sentinel)
    python build.py --version 2026.03.11   # stamps a specific version
"""
import argparse
import subprocess
import sys


def current_branch():
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True,
    )
    return result.stdout.strip().replace("/", "-")


parser = argparse.ArgumentParser()
parser.add_argument("--version", default="9999.0.0", help="Version string to stamp into version.py")
args = parser.parse_args()

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
        f"--distpath=dist/{branch}",
    ],
    check=True,
)

print(f"\nOutput: dist/{branch}/ScanToPrint.exe")
