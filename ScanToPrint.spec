# -*- mode: python ; coding: utf-8 -*-
import os as _os
import sys as _sys

# Bundle VC++ runtime DLLs so python3XX.dll can load on machines that don't
# have the Visual C++ Redistributable installed system-wide.
_python_dir = _os.path.dirname(_sys.executable)
_vc_binaries = [
    (_os.path.join(_python_dir, dll), '.')
    for dll in ('vcruntime140.dll', 'vcruntime140_1.dll')
    if _os.path.exists(_os.path.join(_python_dir, dll))
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=_vc_binaries,
    datas=[
        ('images/scan-to-print.ico', 'images'),
        ('images/scan-to-print.png', 'images'),
        ('locales', 'locales'),
    ],
    hiddenimports=[
        'win32print',
        'win32api',
        'win32con',
        'pynput',
        'pynput.keyboard._win32',
        'pynput.mouse._win32',
        'requests',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ScanToPrint',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='images/scan-to-print.ico',
    version='file_version_info.py',
)
