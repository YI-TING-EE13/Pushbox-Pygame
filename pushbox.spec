# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/pushbox/assets', 'assets'),
    ],
    hiddenimports=[
        'src',
        'src.pushbox',
        'src.pushbox.controllers.game_controller',
        'src.pushbox.models.game_state',
        'src.pushbox.models.level',
        'src.pushbox.models.save_manager',
        'src.pushbox.models.solver',
        'src.pushbox.utils.audio',
        'src.pushbox.utils.config',
        'src.pushbox.utils.constants',
        'src.pushbox.utils.paths',
        'src.pushbox.views.level_editor',
        'src.pushbox.views.renderer',
        'src.pushbox.views.ui_components',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Pushbox-Pygame',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='src/pushbox/assets/icon/pushbox.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Pushbox-Pygame',
)
