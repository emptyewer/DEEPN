import os
import re
import thread
import glob
import cPickle
import time
import subprocess

from datetime import datetime
from libraries.pyper import *
from PyQt4 import QtCore, QtGui, uic

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
        # self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)

        # QThread for processes
        self.process = None
        # self.run_btn.setEnabled(False)
        self.set_interaction_state(False)
        self.verify_installation_btn.setEnabled(True)
        self.data = {}
        self.directory = '~/'
        self.jags_path = None
        self.r_path = None
        self.started = 0
        self.r = None

    def dataReady(self, p):
        print str(p.readAllStandardOutput()).strip()

    def started(self):
        print "Started!"

    def finished(self):
        print "Finished"

    def pair_check(self, list1, list2):
        if list1.count() > 0 and list2.count() > 0:
            return True
        else:
            return False

    def either_check(self, list1, list2):
        if (list1.count() > 0 and list2.count() > 0) or (list1.count() == 0 and list2.count() == 0):
            return True
        else:
            return False

    def monitor_files(self):
        if self.pair_check(self.vec_sel_list, self.vec_nonsel_list) and \
                self.pair_check(self.bait1_sel_list, self.bait1_nonsel_list) and \
                self.pair_check(self.vec_sel_list_2, self.vec_nonsel_list_2):
            if self.either_check(self.bait2_sel_list, self.bait2_nonsel_list) and \
                    self.either_check(self.vec_sel_list_2, self.vec_nonsel_list_2) and \
                    self.either_check(self.bait1_sel_list_2, self.bait1_nonsel_list_2) and \
                    self.either_check(self.bait2_sel_list_2, self.bait2_nonsel_list_2):
                self.run_btn.setEnabled(True)
            else:
                self.run_btn.setEnabled(False)

                # if not self.process == None:
                #     try:
                #         os.kill(self.process.pid + 1, 0)
                #     except OSError:
                #         self.statusbar.showMessage("Finished Installation", 8000)
                #         self.started = 0

                # if not os.path.exists('/usr/local/bin/jags') and self.started == 0:
                #     self.process = subprocess.Popen('open statistics/JAGS.pkg', shell=True)
                #     self.started = 1

                # if not os.path.exists('/usr/local/bin/R') and self.started == 0:
                #     self.process = subprocess.Popen('open statistics/R.pkg', shell=True)
                #     self.started = 1

    def get_exec_path(self, executable):
        if os.path.exists('/usr/local/bin/' + executable):
            return True
        if os.path.exists('/usr/bin/' + executable):
            return True
        return False

    def check_deepn_installed(self):
        dout = self.r("require('deepn')")
        dout = dout.replace(' ', '')
        dout = dout.replace('\n', '')
        if re.match('.+nopackage.+', dout):
            return False
        return True

    @QtCore.pyqtSlot()
    def on_verify_installation_btn_clicked(self):  #####################   new definition
        if not self.get_exec_path('jags'):
            self.verify_installation_btn.setText("Installing JAGS...")
            self.process = subprocess.Popen('open statistics/JAGS.pkg', shell=True)
            while not self.get_exec_path('jags'):
                time.sleep(0.5)

        if os.path.exists('/usr/local/bin/jags'):
            self.jags_path = '/usr/local/bin/jags'
        if os.path.exists('/usr/bin/jags'):
            self.jags_path = '/usr/bin/jags'

        if not self.get_exec_path('R'):
            self.verify_installation_btn.setText("Installing R...")
            self.process = subprocess.Popen('open statistics/R.pkg', shell=True)
            while not self.get_exec_path('R'):
                time.sleep(0.5)

        if os.path.exists('/usr/local/bin/R'):
            self.r_path = '/usr/local/bin/R'
        if os.path.exists('/usr/bin/R'):
            self.r_path = '/usr/bin/R'

        if os.path.exists(self.r_path):
            self.r = R(RCMD=self.r_path)
            if not self.check_deepn_installed():
                self.verify_installation_btn.setText("Finishing Installation...")
                subprocess.Popen(['bash install_deepn.sh ' + self.r_path], shell=True)
                while not self.check_deepn_installed():
                    time.sleep(0.5)
            else:
                self.statusbar.showMessage("Updating DEEPN...")
                subprocess.Popen(['bash update_deepn.sh ' + self.r_path], shell=True)

        self.set_interaction_state(True)
        self.run_btn.setEnabled(False)
        self.verify_installation_btn.setEnabled(False)
        self.verify_installation_btn.setText("Installations are Correct")
        self.statusbar.showMessage("R, JAGS, and DEEPN Installations is Correct")

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
            cmd = "which " + program
            ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = ps.communicate()[0]
            if len(output) > 0:
                return output.rstrip().split()[0]
        except OSError:
            return None

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
        self.monitor_files()

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
        self.directory = directory
        try:
            dirlist = os.listdir(os.path.join(self.directory, 'gene_count_summary'))
            existing_items = []
            for index in xrange(self.file_list.count()):
                existing_items.append(str(self.file_list.item(index).text()))

            for file in dirlist:
                if not re.match('^\.', file) and re.match('.+summary\.csv', file) and file not in existing_items:
                    path = os.path.join(self.directory, 'gene_count_summary', file)
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

    def write_four_columns_from_csv(self, csv_file):
        filehandle = open(csv_file, 'r')
        outhandle = open(csv_file.replace("_summary.csv", "_stats.csv"), 'w')
        count = 0
        for line in filehandle.readlines():
            if count > 3:
                split = line.split(',')
                last = "\"" + "-".join(split[3:]) + "\""
                outhandle.write("%s,%s,%s,%s\n" % (split[0], split[1], split[2], last))
            count += 1
        outhandle.close()

    def write_r_input(self):
        output = open(os.path.join(self.directory, 'r_input.params'), 'w')
        for key in sorted(self.data.keys()):
            self.write_four_columns_from_csv(self.data[key])
            output.write("%-25s = %s\n" % (key, self.data[key]))
        output.write("%-25s = %d\n" % ("Threshold", self.threshold_sbx.value()))
        # output.write("%-25s = %s\n" % ("R Path", self.r_path))
        # output.write("%-25s = %s" % ("JAGS Path", self.jags_path))
        output.close()

    def set_interaction_state(self, state):
        self.run_btn.setEnabled(state)
        self.file_list.setEnabled(state)
        self.vec_sel_list.setEnabled(state)
        self.vec_nonsel_list.setEnabled(state)
        self.bait1_sel_list.setEnabled(state)
        self.bait1_nonsel_list.setEnabled(state)
        self.bait2_sel_list.setEnabled(state)
        self.bait2_nonsel_list.setEnabled(state)

        self.vec_sel_list_2.setEnabled(state)
        self.vec_nonsel_list_2.setEnabled(state)
        self.bait1_sel_list_2.setEnabled(state)
        self.bait1_nonsel_list_2.setEnabled(state)
        self.bait2_sel_list_2.setEnabled(state)
        self.bait2_nonsel_list_2.setEnabled(state)
        self.folder_choice_btn.setEnabled(state)
        self.quit_btn.setEnabled(state)
        self.threshold_sbx.setEnabled(state)

    def _merge_dicts(*dict_args):
        """
        Given any number of dicts, shallow copy and merge into a new dict,
        precedence goes to key value pairs in latter dicts.
        """
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result

    def runr(self):
        self.r("analyzeDeepn('" + os.path.join(self.directory, 'r_input.params') + "', outfile='" + \
               os.path.join(self.directory, 'gene_count_summary', 'statmaker_output.csv') + "')")
        parameters = []
        stats = {}
        for key in self.data.keys():
            filename = os.path.basename(self.data[key].replace("_summary.csv", "") + ".bqp")
            stats[key] = cPickle.load(open(os.path.join(self.directory, 'blast_results_query', filename), 'rb'))

        p = open(os.path.join(self.directory, "r_input.params"))
        for line in p:
            parameters.append(line)
        p.close()
        s = open(os.path.join(self.directory, 'gene_count_summary', "statmaker_output.csv"))
        for line in s:
            split = line.rstrip().split(",")
            if split[0] == 'Gene':
                length = len(split)
                for key in sorted(self.data.keys()):
                    split.extend([" ", " ", " ", " ", key, " ", " ", " "])
                parameters.append(",".join(split))
                parameters.append(",".join([" "] * (length + 1) + ["inframe_inorf", "upstream", "in_orf",
                                                                   "downstream", "in_frame", "backwards",
                                                                   "intron", " "] * len(self.data.keys())))
            else:
                for key in sorted(self.data.keys()):
                    try:
                        t = stats[key][split[0]]['stats']
                        split.extend(map(str, [" ", t['frame_orf'] * 100.0/t['total'],
                                               t['upstream'] * 100.0/t['total'],
                                               t['in_orf'] * 100.0/t['total'],
                                               t['downstream'] * 100.0/t['total'],
                                               t['in_frame'] * 100.0/t['total'],
                                               t['backwards'] * 100.0 / t['total'],
                                               t['intron'] * 100.0 / t['total']]))
                    except KeyError:
                        split.extend([" "] + ["N/A"] * 7)
                parameters.append(",".join(split))

        s.close()

        FORMAT = '%d%b%Y-%H%M%S'
        name = '%s_%s.csv' % ('statmaker_output', datetime.now().strftime(FORMAT))
        out = open(os.path.join(self.directory, 'gene_count_summary', name), 'w')
        for l in parameters:
            out.write(l)
            out.write("\n")
        out.close()

        map(os.remove, glob.glob(os.path.join(self.directory, 'gene_count_summary', "*_stats.csv")))
        map(os.remove, glob.glob(os.path.join(self.directory, "r_input.params")))
        map(os.remove, glob.glob(os.path.join(self.directory, 'gene_count_summary', "statmaker_output.csv")))
        self.statusbar.showMessage("Saved Results to File: %s" % os.path.join(self.directory, name))
        self.set_interaction_state(True)

    @QtCore.pyqtSlot()
    def on_run_btn_clicked(self):
        # self.r = R(RCMD='/usr/local/bin/R')
        # dout = self.r("require('deepn')")
        # dout = dout.replace(' ', '')
        # dout = dout.replace('\n', '')
        # if re.match('.+nopackage.+', dout):
        #     self.statusbar.showMessage("DEEPN R Package Not Found. To install follow instructions in the manual.")
        # else:
        self.statusbar.showMessage("Running DEEPN statistics... Please Wait...")
        self.write_r_input()
        self.set_interaction_state(False)
        thread.start_new_thread(self.runr, ())
        # self.process.start(self.r_path, [os.path.join(self.directory, 'sample.r')])


def appExit():
    app.quit()
    sys.exit()


if __name__ == '__main__':
    form = Stat_Maker_Gui()
    form.show()
    app.aboutToQuit.connect(appExit)
    app.exec_()
