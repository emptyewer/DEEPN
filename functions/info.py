import os
import sys
from PyQt4 import QtGui, uic

app = QtGui.QApplication(sys.argv)
form_class, base_class = uic.loadUiType(os.path.join(os.path.curdir, 'ui', 'Info_Dialog.ui'))

class Info_Dialog(QtGui.QDialog, form_class):
    def __init__(self, *args):
        super(Info_Dialog, self).__init__(*args)
        self.setupUi(self)
        self.setWindowModality(1)

    def message(self, message):
        self.message_txt.clear()
        self.message_txt.setText(message)

    def windowTitle(self, str):
        self.setWindowTitle(str)


