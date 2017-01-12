import os
import sys
from PyQt4 import QtGui, uic

app = QtGui.QApplication(sys.argv)
ui_path = os.path.join(os.path.curdir, 'ui', 'Message_Dialog.ui')
if sys.platform == 'win32':
    ui_path = os.path.join(os.path.curdir, 'ui', 'Windows', 'Message_Dialog.ui')
form_class, base_class = uic.loadUiType(ui_path)

class Message_Dialog(QtGui.QDialog, form_class):
    def __init__(self, *args):
        super(Message_Dialog, self).__init__(*args)
        self.setupUi(self)
        self.setWindowModality(1)

    def showMessage(self, message):
        self.message_txt.clear()
        self.message_txt.setText(message)

    def windowTitle(self, str):
        self.setWindowTitle(str)


