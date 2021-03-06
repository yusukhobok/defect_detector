block_cipher = None

added_files = [( 'data', 'data' ),]

hidden_imports = ['scipy._lib.messagestream', '_gammaln', 'pandas._libs.tslibs.timedeltas', 'pandas._libs.tslibs.np_datetime',
'pandas._libs.tslibs.ccalendar', 'pandas._libs.tslibs.conversion', 'pandas._libs.tslibs.fields', 'pandas._libs.tslibs.frequencies',
'pandas._libs.tslibs.nattype', 'pandas._libs.tslibs.offsets', 'pandas._libs.tslibs.parsing', 'pandas._libs.tslibs.period',
'pandas._libs.tslibs.resolution', 'pandas._libs.tslibs.strptime', 'pandas._libs.tslibs.timestamps', 'pandas._libs.tslibs.timezones',
'pandas._libs.algos',
'pandas._libs.groupby',
'pandas._libs.hashing',
'pandas._libs.hashtable',
'pandas._libs.index',
'pandas._libs.indexing',
'pandas._libs.internals',
'pandas._libs.interval',
'pandas._libs.join',
'pandas._libs.json',
'pandas._libs.lib',
'pandas._libs.missing',
'pandas._libs.ops',
'pandas._libs.parsers',
'pandas._libs.properties',
'pandas._libs.reduction',
'pandas._libs.reshape',
'pandas._libs.skiplist',
'pandas._libs.sparse',
'pandas._libs.testing',
'pandas._libs.tslib',
'pandas._libs.window',
'pandas._libs.writers',
'skimage.io._plugins',
'PyInstaller.hooks.hook-encodings.py']

a_defect_defector = Analysis(['main_logic.py'],
                       pathex=[''],
                       binaries=[],
                       datas=added_files,
                       hiddenimports=hidden_imports,
                       hookspath=[],
                       runtime_hooks=[],
                       excludes=[],
                       win_no_prefer_redirects=False,
                       win_private_assemblies=False,
                       cipher=block_cipher)
					   
pyz_defect_defector = PYZ(a_defect_defector.pure, a_defect_defector.zipped_data, cipher=block_cipher)
exe_defect_defector = EXE(pyz_defect_defector,
                    a_defect_defector.scripts,
                    exclude_binaries=True,
                    name='defect_detector',
                    debug=False,
                    strip=False,
                    upx=True,
                    console=True,
                    icon = "icons\\georeader.ico")
coll_defect_defector = COLLECT(exe_defect_defector,
                         a_defect_defector.binaries,
                         a_defect_defector.zipfiles,
                         a_defect_defector.datas,
                         strip=False,
                         upx=True,
                         name='defect_detector')