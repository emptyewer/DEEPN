
from setuptools import setup

APP = ['gc_jm.py']
OPTIONS = {'argv_emulation': True,
           'iconfile' : 'icon/Icon1.icns',
           'plist': {'CFBundleGetInfoString': 'GCJM',
                     'CFBundleIdentifier': 'edu.uiowa.robertpiper.deepn.gcjm',
                     'CFBundleShortVersionString': '1.0',
                     'CFBundleName': 'GCJM',
                     'CFBundleVersion': '10',
                     'NSHumanReadableCopyright': '(c) 2016 Venkatramanan Krishnamani, Robert C. Piper, Mark Stammnes'},
           'includes': ['sys', 'subprocess'],
           'excludes': ['PyQt4.QtDesigner', 'PyQt4.QtNetwork', 'PyQt4.QtOpenGL', 'PyQt4.QtScript', 'PyQt4.QtSql', 'PyQt4.QtTest', 'PyQt4.QtWebKit', 'PyQt4.QtXml', 'PyQt4.phonon'],
           }

setup(
    app=APP,
    name='GCJM',
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    author='Venkatramanan Krishnamani, Robert C. Piper, Mark Stammnes',
    data_files=[],
)