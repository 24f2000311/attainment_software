from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect hidden imports and data files
hidden_imports = []
hidden_imports += collect_submodules('pandas')
hidden_imports += collect_submodules('openpyxl')
hidden_imports += collect_submodules('reportlab')
hidden_imports += ['et_xmlfile']

# Collect data files (especially for reportlab/fonts)
datas = [('templates', 'templates'), ('static', 'static')]
datas += collect_data_files('reportlab')
datas += collect_data_files('openpyxl')

a = Analysis(
    ['desktop_app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
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
    name='Attainment_Software_System',
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
    icon=['static\\icons\\app_icon.ico'],
)
