import os
import sys
import re
import thread
import time
from PyQt4 import QtCore, QtGui, uic
import subprocess

app = QtGui.QApplication(sys.argv)
form_class, base_class = uic.loadUiType(os.path.join('ui', 'Stat_Maker.ui'))

class MyListWidgetItem(QtGui.QListWidgetItem):
    def __init__(self, *args):
        super(MyListWidgetItem, self).__init__(*args)
        self.data = ''
    def GetData(self):
        return self.data

class Stat_Maker_Gui(QtGui.QMainWindow, form_class):
    def __init__(self, *args):
        super(Stat_Maker_Gui, self).__init__(*args)
        self.setupUi(self)
        self.connect(self.vec_sel_list, QtCore.SIGNAL("dropped"), self.vec_sel_fileDropped)
        self.connect(self.vec_nonsel_list, QtCore.SIGNAL("dropped"), self.vec_nonsel_fileDropped)
        self.connect(self.bait1_sel_list, QtCore.SIGNAL("dropped"), self.bait1_sel_fileDropped)
        self.connect(self.bait1_nonsel_list, QtCore.SIGNAL("dropped"), self.bait1_nonsel_fileDropped)
        self.connect(self.bait2_sel_list, QtCore.SIGNAL("dropped"), self.bait2_sel_fileDropped)
        self.connect(self.bait2_nonsel_list, QtCore.SIGNAL("dropped"), self.bait2_nonsel_fileDropped)

        self.connect(self.vec_sel_list_2, QtCore.SIGNAL("dropped"), self.vec_sel_fileDropped_2)
        self.connect(self.vec_nonsel_list_2, QtCore.SIGNAL("dropped"), self.vec_nonsel_fileDropped_2)
        self.connect(self.bait1_sel_list_2, QtCore.SIGNAL("dropped"), self.bait1_sel_fileDropped_2)
        self.connect(self.bait1_nonsel_list_2, QtCore.SIGNAL("dropped"), self.bait1_nonsel_fileDropped_2)
        self.connect(self.bait2_sel_list_2, QtCore.SIGNAL("dropped"), self.bait2_sel_fileDropped_2)
        self.connect(self.bait2_nonsel_list_2, QtCore.SIGNAL("dropped"), self.bait2_nonsel_fileDropped_2)

        self.connect(self.vec_sel_list, QtCore.SIGNAL("deleted"), self.file_deleted)
        self.connect(self.vec_nonsel_list, QtCore.SIGNAL("deleted"), self.file_deleted)
        self.connect(self.bait1_sel_list, QtCore.SIGNAL("deleted"), self.file_deleted)
        self.connect(self.bait1_nonsel_list, QtCore.SIGNAL("deleted"), self.file_deleted)
        self.connect(self.bait2_sel_list, QtCore.SIGNAL("deleted"), self.file_deleted)
        self.connect(self.bait2_nonsel_list, QtCore.SIGNAL("deleted"), self.file_deleted)

        self.connect(self.vec_sel_list_2, QtCore.SIGNAL("deleted"), self.file_deleted)
        self.connect(self.vec_nonsel_list_2, QtCore.SIGNAL("deleted"), self.file_deleted)
        self.connect(self.bait1_sel_list_2, QtCore.SIGNAL("deleted"), self.file_deleted)
        self.connect(self.bait1_nonsel_list_2, QtCore.SIGNAL("deleted"), self.file_deleted)
        self.connect(self.bait2_sel_list_2, QtCore.SIGNAL("deleted"), self.file_deleted)
        self.connect(self.bait2_nonsel_list_2, QtCore.SIGNAL("deleted"), self.file_deleted)

        # QProcess object for external app
        self.process = QtCore.QProcess(self)
        self.process.readyReadStandardOutput.connect(self.stdout_ready)
        self.process.readyReadStandardError.connect(self.stderr_ready)
        self.process.started.connect(self.process_started)
        self.process.finished.connect(self.process_finished)
        # QThread for processes
        self.thread = QtCore.QThread(self)
        self.run_btn.setEnabled(False)
        self.data = {}

        thread.start_new_thread(self.monitor_files, ())

    def pair_check(self, list1, list2):
        if list1.count() > 0:
            if list2.count() > 0:
                return True
        return False

    def either_check(self, list1, list2):
        if (list1.count() > 0 and list2.count() > 0) or (list1.count() == 0 and list2.count() == 0):
            return True
        else:
            return False

    def monitor_files(self):
        while 1:
            if self.pair_check(self.vec_sel_list, self.vec_nonsel_list) and \
                    self.pair_check(self.bait1_sel_list, self.bait1_nonsel_list):
                if self.either_check(self.bait2_sel_list, self.bait2_nonsel_list) and \
                        self.either_check(self.vec_sel_list_2, self.vec_nonsel_list_2) and \
                        self.either_check(self.bait1_sel_list_2, self.bait1_nonsel_list_2) and \
                        self.either_check(self.bait2_sel_list_2, self.bait2_nonsel_list_2):
                    self.run_btn.setEnabled(True)
                else:
                    self.run_btn.setEnabled(False)
            time.sleep(0.1)

    def process_started(self):
        self.statusbar.showMessage("Process Started", 5000)

    def process_finished(self):
        self.statusbar.showMessage("Process ended!", 5000)

    def stdout_ready(self):
        text = str(self.process.readAllStandardOutput()).strip()
        self.statusbar.showMessage(text)

    def stderr_ready(self):
        text = str(self.process.readAllStandardError())
        self.append(text)

    def which(self, program):
        try:
            cmd = "which " + program
            ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = ps.communicate()[0]
            if len(output) > 0:
                return True
        except OSError:
            return False
        return False

    def get_path(self, program):
        try:
            cmd = "brew info " + program + " | grep /usr/local/Cellar"
            ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = ps.communicate()[0]
            if len(output) > 0:
                return output.rstrip().split()[0]
        except OSError:
            return False

    def file_deleted(self, path):
        for key in self.data.keys():
            if self.data[key] == path:
                self.data.__delitem__(key)

    def fileDropped(self, list, url, key):
        if os.path.exists(url) and self.check_uniqueness(url):
            iconProvider = QtGui.QFileIconProvider()
            fileInfo = QtCore.QFileInfo(url)
            icon = iconProvider.icon(fileInfo)
            item = MyListWidgetItem()
            item.data = url
            item.setIcon(icon)
            item.setText(os.path.basename(os.path.normpath(url)))
            list.clear()
            list.addItem(item)
            self.data[key] = url

    def check_uniqueness(self, path):
        for url in self.data.values():
            if path == url:
                return False
        return True

    @QtCore.pyqtSlot()
    def on_quit_btn_clicked(self):
        app.quit()
        sys.exit()

    @QtCore.pyqtSlot()
    def on_folder_choice_btn_clicked(self):
        directory = str(QtGui.QFileDialog.getExistingDirectory(QtGui.QFileDialog(), "Locate Work Folder",
                                                                    os.path.expanduser("~"),
                                                                    QtGui.QFileDialog.ShowDirsOnly))
        try:
            dirlist = os.listdir(directory)
            existing_items = []
            for index in xrange(self.file_list.count()):
                existing_items.append(str(self.file_list.item(index).text()))

            for file in dirlist:
                if not re.match('^\.', file) and re.match('.+summary\.csv', file) and file not in existing_items:
                    path = os.path.join(directory, file)
                    fileInfo = QtCore.QFileInfo(path)
                    iconProvider = QtGui.QFileIconProvider()
                    icon = iconProvider.icon(fileInfo)
                    item = MyListWidgetItem()
                    item.data = path
                    item.setIcon(icon)
                    item.setText(file)
                    self.file_list.addItem(item)
        except OSError:
            pass

    def vec_sel_fileDropped(self, path):
        path = str(path)
        if os.path.exists(path):
            self.fileDropped(self.vec_sel_list, path, 'Vector_Selected_1')

    def vec_nonsel_fileDropped(self, path):
        path = str(path)
        if os.path.exists(path):
            self.fileDropped(self.vec_nonsel_list, path, "Vector_Non-Selected_1")

    def bait1_sel_fileDropped(self, path):
        path = str(path)
        if os.path.exists(path):
            self.fileDropped(self.bait1_sel_list, path, "Bait1_Selected_1")

    def bait1_nonsel_fileDropped(self, path):
        path = str(path)
        if os.path.exists(path):
            self.fileDropped(self.bait1_nonsel_list, path, "Bait1_Non-Selected_1")

    def bait2_sel_fileDropped(self, path):
        path = str(path)
        if os.path.exists(path):
            self.fileDropped(self.bait2_sel_list, path, "Bait2_Selected_1")

    def bait2_nonsel_fileDropped(self, path):
        path = str(path)
        if os.path.exists(path):
            self.fileDropped(self.bait2_nonsel_list, path, "Bait2_Non-Selected_1")

    def vec_sel_fileDropped_2(self, path):
        path = str(path)
        if os.path.exists(path):
            self.fileDropped(self.vec_sel_list_2, path, "Vector_Selected_2")

    def vec_nonsel_fileDropped_2(self, path):
        path = str(path)
        if os.path.exists(path):
            self.fileDropped(self.vec_nonsel_list_2, path, "Vector_Non-Selected_2")

    def bait1_sel_fileDropped_2(self, path):
        path = str(path)
        if os.path.exists(path):
            self.fileDropped(self.bait1_sel_list_2, path, "Bait1_Selected_2")

    def bait1_nonsel_fileDropped_2(self, path):
        path = str(path)
        if os.path.exists(path):
            self.fileDropped(self.bait1_nonsel_list_2, path, "Bait1_Non-Selected_2")

    def bait2_sel_fileDropped_2(self, path):
        path = str(path)
        if os.path.exists(path):
            self.fileDropped(self.bait2_sel_list_2, path, "Bait2_Selected_2")

    def bait2_nonsel_fileDropped_2(self, path):
        path = str(path)
        if os.path.exists(path):
            self.fileDropped(self.bait2_nonsel_list_2, path, "Bait2_Non-Selected_2")

    def write_r_input(self):
        output = open(os.path.join(os.path.curdir, 'rscript_input.params'), 'w')
        for key in self.data.keys():
            output.write("%s = %s\n" % (key, self.data[key]))
        output.write("Threshold = %d" % self.threshold_sbx.value())
        output.close()

    @QtCore.pyqtSlot()
    def on_run_btn_clicked(self):
        self.write_r_input()

        if not self.which('brew'):
            self.process.start('yes', ['\'\'', '|', '/usr/bin/ruby', '-e', '\"$(curl -fsSL '
                                                    'https://raw.githubusercontent.com/Homebrew/install/master/install)\"'])
        if not self.which('Rscript'):
            self.process.start('brew', ['install', 'r'])

        if not self.which('jags'):
            self.process.start('brew', ['install', 'jags'])

        r_path = os.path.join(self.get_path('R'), 'bin', 'Rscript')
        jags_path = os.path.join(self.get_path('jags'), 'bin', 'jags')

        print jags_path
        self.process.start(r_path, [os.path.join(os.path.curdir, 'sample.r')])


def appExit():
    app.quit()
    sys.exit()

if __name__ == '__main__':
    form = Stat_Maker_Gui()
    form.show()
    app.aboutToQuit.connect(appExit)
    app.exec_()
