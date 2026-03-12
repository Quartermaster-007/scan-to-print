"""
Build script — outputs all builds to dist/ with a name that encodes
the version and branch for non-main builds.

Output name format:
    main branch  →  ScanToPrint.exe
    other branch →  ScanToPrint <version> <branch>.exe

Usage:
    python build.py                        # stamps version as 9999.0.0 (dev sentinel)
    python build.py --version 2026.03.11   # stamps a specific version
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
