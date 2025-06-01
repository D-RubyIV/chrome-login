# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


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
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
# Pyarmor patch start:

srcpath = ''
obfpath = 'obfdist'

def apply_pyarmor_patch(srcpath, obfpath):

    from PyInstaller.compat import is_win, is_cygwin
    extname = 'pyarmor_runtime' + ('.pyd' if is_win or is_cygwin else '.so')

    from glob import glob
    rtpkg = glob(os.path.join(obfpath, '*', extname))
    if len(rtpkg) != 1:
        raise RuntimeError('No runtime package found')
    rtpkg = os.path.basename(os.path.dirname(rtpkg[0]))

    extpath = os.path.join(rtpkg, extname)

    if hasattr(a.pure, '_code_cache'):
        code_cache = a.pure._code_cache
    else:
        from PyInstaller.config import CONF
        code_cache = CONF['code_cache'].get(id(a.pure))

    # Make sure both of them are absolute paths
    src = os.path.normcase(os.path.abspath(srcpath))
    obf = os.path.abspath(obfpath)
    n = len(src) + 1

    count = 0
    for i in range(len(a.scripts)):
        if os.path.normcase(a.scripts[i][1]).startswith(src):
            x = os.path.join(obf, a.scripts[i][1][n:])
            if os.path.exists(x):
                a.scripts[i] = a.scripts[i][0], x, a.scripts[i][2]
                count += 1
    if count == 0:
        raise RuntimeError('No obfuscated script found')

    for i in range(len(a.pure)):
        if os.path.normcase(a.pure[i][1]).startswith(src):
            x = os.path.join(obf, a.pure[i][1][n:])
            if os.path.exists(x):
                code_cache.pop(a.pure[i][0], None)
                a.pure[i] = a.pure[i][0], x, a.pure[i][2]

    a.pure.append((rtpkg, os.path.join(obf, rtpkg, '__init__.py'), 'PYMODULE'))
    a.binaries.append((extpath, os.path.join(obf, extpath), 'EXTENSION'))

apply_pyarmor_patch(srcpath, obfpath)

# Pyarmor patch end.

# Before this line
# pyz = PYZ(...)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ChromeLogin',
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
    icon=r'C:\Users\pha4h\Documents\chrome-login\browser_chrome_icon.ico'
)