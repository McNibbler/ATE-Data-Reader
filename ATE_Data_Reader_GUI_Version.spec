# -*- mode: python -*-

block_cipher = None


a = Analysis(['ATE_Data_Reader_GUI_Version.py'],
             pathex=['C:\\Users\\tkaunzin\\Desktop\\github 2\\public-projects\\Python\\ATE Data Reader'],
             binaries=[],
             datas=[],
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
          name='ATE_Data_Reader_GUI_Version',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )
