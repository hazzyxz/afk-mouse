# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path


ICON_MAC = Path("afk-mouse.icns")
ICON_WIN = Path("afk-mouse.ico")

if sys.platform == "darwin":
    exe_icon = [str(ICON_MAC)]
elif sys.platform == "win32" and ICON_WIN.exists():
    exe_icon = [str(ICON_WIN)]
else:
    exe_icon = []

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='AFK Mouse',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=exe_icon,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AFK Mouse',
)
if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name='AFK Mouse.app',
        icon=str(ICON_MAC),
        bundle_identifier=None,
    )
