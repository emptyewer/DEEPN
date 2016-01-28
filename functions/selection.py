import os
import sys
from PyQt4 import QtGui, uic

app = QtGui.QApplication(sys.argv)
form_class, base_class = uic.loadUiType(os.path.join(os.path.curdir, 'ui', 'Selection_Dialog.ui'))

class Selection_Dialog(QtGui.QDialog, form_class):
    def __init__(self, *args):
        super(Selection_Dialog, self).__init__(*args)
        self.setupUi(self)
        self.setWindowModality(1)
        self.selection = ''
        self.selection_lst.currentIndexChanged.connect(self.select)
        self.select_btn.clicked.connect(self.select_continue)

    def populate_list(self, list):
        for item in list:
            self.selection_lst.addItem(item)
        self.selection = 0

    def select(self):
        self.selection = self.selection_lst.currentIndex()

    def select_continue(self):
        self.hide()

    def windowTitle(self, str):
        self.setWindowTitle(str)
