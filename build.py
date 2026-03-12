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

# Stamp file_version_info.py with the real version numbers so the exe's
# Properties > Details panel shows the correct version.
# yyyy.mm.dd[.N] → (yyyy, mm, dd, N) padded to 4 parts.
_parts = [int(x) for x in args.version.split(".")]
_parts += [0] * (4 - len(_parts))
_ver_tuple = tuple(_parts[:4])
with open("file_version_info.py", "r", encoding="utf-8") as f:
    _vinfo = f.read()
_vinfo = __import__("re").sub(
    r"filevers=\(.*?\)", f"filevers={_ver_tuple}", _vinfo
)
_vinfo = __import__("re").sub(
    r"prodvers=\(.*?\)", f"prodvers={_ver_tuple}", _vinfo
)
_ver_str = args.version
for _key in ("FileVersion", "ProductVersion"):
    _vinfo = __import__("re").sub(
        rf"StringStruct\(u'{_key}',\s*u'[^']*'\)",
        f"StringStruct(u'{_key}', u'{_ver_str}')",
        _vinfo,
    )
with open("file_version_info.py", "w", encoding="utf-8") as f:
    f.write(_vinfo)

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
