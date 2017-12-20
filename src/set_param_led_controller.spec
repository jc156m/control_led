# -*- mode: python -*-

block_cipher = None


a = Analysis(['set_param_led_controller.py'],
             pathex=['C:\\cg\\WinPython-64bit-3.5.4.1Qt5\\settings\\.spyder-py3'],
             binaries=[],
             datas=[('set_le_controller.ui', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='set_param_led_controller',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )
