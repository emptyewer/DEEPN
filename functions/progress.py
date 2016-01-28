import os
import sys
from PyQt4 import QtCore, QtGui, uic

app = QtGui.QApplication(sys.argv)
form_class, base_class = uic.loadUiType(os.path.join(os.path.curdir, 'ui', 'Progress_Dialog.ui'))

class Progress_Dialog(QtGui.QDialog, form_class):
    def __init__(self, *args):
        super(Progress_Dialog, self).__init__(*args)
        self.setupUi(self)

    def showMessage(self, message):
        self.message_txt.clear()
        self.message_txt.setText(message)

    def windowTitle(self, str):
        self.setWindowTitle(str)
