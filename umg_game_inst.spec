# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['umg_game_inst.py'],
             pathex=['C:\\Projects\\umg_squad_creator'],
             binaries=[],
             datas=[('C:\\Users\\asmialek\\AppData\\Local\\Programs\\Python\\Python38-32\\Lib\\site-packages\\pygame_gui\\data', '.\\pygame_gui\\data'),
                    ('C:\\Projects\\umg_squad_creator\\umg_game', '.\\umg_game'),
                    ('C:\\Projects\\umg_squad_creator\\umg_shared', '.\\umg_shared'),
                    ('C:\\Projects\\umg_squad_creator\\squads', '.\\squads'),
                    ('C:\\Projects\\umg_squad_creator\\umg_factory', '.\\umg_factory')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='umg_game_inst',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='umg_game_inst')
