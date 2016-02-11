import os
import sys
from setuptools import setup
if sys.platform == 'darwin':
    import py2app
elif sys.platform == 'win32':
    import py2exe

APP = ['gc_jm.py']
INCLUDES = ['sys', 'subprocess']
OPTIONS = {'argv_emulation': True,
           'iconfile' : 'icon/Icon1.icns',
           'plist': {'CFBundleGetInfoString': 'GCJM',
                     'CFBundleIdentifier': 'edu.uiowa.robertpiper.deepn.gcjm',
                     'CFBundleShortVersionString': '1.1',
                     'CFBundleName': 'GCJM',
                     'CFBundleVersion': '11',
                     'NSHumanReadableCopyright': '(c) 2016 Venkatramanan Krishnamani, Robert C. Piper, Mark Stammnes'},
           'includes': INCLUDES,
           'excludes': ['PyQt4.QtDesigner', 'PyQt4.QtNetwork', 'PyQt4.QtOpenGL', 'PyQt4.QtScript', 'PyQt4.QtSql', 'PyQt4.QtTest', 'PyQt4.QtWebKit', 'PyQt4.QtXml', 'PyQt4.phonon'],
           }

if sys.platform == 'darwin':
    setup(
        app=APP,
        name='GCJM',
        options={'py2app': OPTIONS},
        setup_requires=['py2app'],
        author='Venkatramanan Krishnamani, Robert C. Piper, Mark Stammnes',
        data_files=[],
    )
elif sys.platform == 'win32':
    origIsSystemDLL = py2exe.build_exe.isSystemDLL
    def isSystemDLL(pathname):
            if os.path.basename(pathname).lower() in ("msvcp71.dll", "dwmapi.dll", "'msvcp90.dll'"):
                    return 0
            return origIsSystemDLL(pathname)
    py2exe.build_exe.isSystemDLL = isSystemDLL
    setup(
        version='1.1',
        description='GCJM',
        author='Venkatramanan Krishnamani, Robert C. Piper, Mark Stammnes',
        windows=[{"script":'gc_jm.py',
                   "icon_resources": [(1, "icon/Icon1.ico")],
                   "dest_base":"GCJM"
                }],
        data_files=[],
        options={"py2exe": {'includes': INCLUDES,
                            "optimize": 2,
                            "compressed": 2,
                            "bundle_files": 1,
                            "dist_dir": "dist\GCJM"
                            }}
    )