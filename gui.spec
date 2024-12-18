# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['adb_auto_player\\eel_main.py'],
    pathex=['adb_auto_player'],
    binaries=[],
    datas=[
        ('pyproject.toml', '.'),
        ('adb_auto_player\\frontend\\build', '.\\frontend\\build')
    ],
    hiddenimports=[
        'adb_auto_player.plugin',
        'bottle_websocket',
        '_socket',
        'unicodedata',
        'eel'
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
    [],
    exclude_binaries=True,
    name='AdbAutoPlayer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['koko.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AdbAutoPlayer',
)
