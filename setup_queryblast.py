import os
import glob
from setuptools import setup

def find_data_files(sources, targets, patterns):
    """Locates the specified data-files and returns the matches
    in a data_files compatible format.

    source is the root of the source data tree.
        Use '' or '.' for current directory.
    target is the root of the target data tree.
        Use '' or '.' for the distribution directory.
    patterns is a sequence of glob-patterns for the
        files you want to copy.
    """

    ret = {}
    for i, source in enumerate(sources):
        target = targets[i]
        if glob.has_magic(source) or glob.has_magic(target):
            raise ValueError("Magic not allowed in src, target")
        pattern = os.path.join(source, patterns[i])
        for filename in glob.glob(pattern):
            if os.path.isfile(filename):
                targetpath = os.path.join(target, os.path.relpath(filename, source))
                path = os.path.dirname(targetpath)
                ret.setdefault(path, []).append(filename)
    return sorted(ret.items())


APP = ['query_blast_gui.py']
OPTIONS = {'argv_emulation': True,
           'iconfile' : 'icon/Icon4.icns',
           'plist': {'CFBundleGetInfoString': 'Blast Query',
                     'CFBundleIdentifier': 'edu.uiowa.robertpiper.deepn.blast_query',
                     'CFBundleShortVersionString': '0.9',
                     'CFBundleName': 'Blast Query',
                     'CFBundleVersion': '09',
                     'NSHumanReadableCopyright': '(c) 2016 Venkatramanan Krishnamani, Robert C. Piper, Mark Stammnes'},
           'includes': ['PyQt4', 'glob', 'cPickle', 'time', 'sys', 'os', 'pydoc',
                        'json', 'numbers', 'hashlib', 'decimal', 'csv', 'collections', 'pyqtgraph', 'numpy'],
           'excludes': ['PyQt4.QtDesigner', 'PyQt4.QtNetwork', 'PyQt4.QtOpenGL', 'PyQt4.QtScript',
                        'PyQt4.QtSql', 'PyQt4.QtTest', 'PyQt4.QtWebKit', 'PyQt4.QtXml', 'PyQt4.phonon'],
           }

setup(
    app=APP,
    name='Blast Query',
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    author='Venkatramanan Krishnamani, Robert C. Piper, Mark Stammnes',
    data_files=find_data_files(['functions', 'libraries/xlsxwriter', 'lists', 'ui', '.'],
                               ['functions', 'libraries/xlsxwriter', 'lists', 'ui', ''],
                               ['*.py', '*.py', '*', '*.ui', '*.txt'])
)
