"""
Build script — outputs all builds as ScanToPrint.exe, separated by folder.

Output location:
    main branch  →  dist/ScanToPrint.exe
    other branch →  dist/<branch>/ScanToPrint.exe

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

outdir = "dist" if branch == "main" else f"dist/{branch}"
os.makedirs(outdir, exist_ok=True)

subprocess.run(
    [
        sys.executable, "-m", "PyInstaller",
        "ScanToPrint.spec",
        "--noconfirm",
        f"--distpath={outdir}",
    ],
    check=True,
)

print(f"\nOutput: {outdir}/ScanToPrint.exe")
