import sys
import os
import re
import time
import thread
import itertools
import pyqtgraph as pg
import functions.db as db
import functions.fileio_gui as f
import functions.printio_gui as p
import functions.message as m

from PyQt4 import QtCore, QtGui, uic

app = QtGui.QApplication(sys.argv)
form_class, base_class = uic.loadUiType(os.path.join('ui', 'DEEPN.ui'))

class vQlistWidgetItem(QtGui.QListWidgetItem):
    def __init__(self, value, data):
        super(vQlistWidgetItem, self).__init__(QtCore.QString('%s' % value))
        self.data = data

class DEEPN_Launcher(QtGui.QMainWindow, form_class):
    def __init__(self, *args):
        super(DEEPN_Launcher, self).__init__(*args)
        self.setupUi(self)
        self.proceed = 1
        self.prompt = 2
        self.fileio = f.fileio()
        self.printio = p.printio()
        self.directory = None
        self.clicked_button = None
        self.clicked_button_text = None
        self.db_selection = None
        self.blast_db_name = ''
        self.gene_dictionary = ''
        self.gene_list_file = ''
        self.chromosome_list = ''
        self.start_match = re.compile(r'^[>>>|\t|***]')
        self.bar = itertools.cycle(['/', '-', '\\'])
        self._layouts = [self.analyze_data_layout, self.process_data_layout_1,
                         self.process_data_layout_2, self.process_data_layout_3,
                         self.process_data_layout_4, self.status_layout]
        self.window = self.window()
        self.window.setGeometry(10, 30, self.width(), self.height())
        self.buttons = []
        self.thread = None
        self.message = m.Message_Dialog()
        self.comment = m.Message_Dialog()
        self.quit = False
        for layout in self._layouts:
            widgets = (layout.itemAt(i).widget() for i in range(layout.count()))
            for btn in widgets:
                if btn != None:
                    self.buttons.append(btn)

        self.buttons1 = []
        widgets = (self.layout1.itemAt(i).widget() for i in range(self.layout1.count()))
        for btn in widgets:
            if btn != None:
                self.buttons1.append(btn)

        # Checkbox
        self.prompt_box.stateChanged.connect(self.on_prompt_box_stateChanged)

        # QProcess object for external app
        self.process = QtCore.QProcess(self)
        self.process.readyReadStandardOutput.connect(self.stdout_ready)
        # self.process.readyReadStandardError.connect(self.stderr_ready)
        self.process.started.connect(self.process_started)
        self.process.finished.connect(self.process_finished)

        # QThread for processes
        self.thread = QtCore.QThread(self)

        # Connect database
        self.g_db = db.genome_db(os.path.join('DEEPN_db.sqlite3'))
        for row in self.g_db.select_all('*'):
            self.db_list_wgt.addItem(vQlistWidgetItem(row[1], row[0]))

        # Binding Selection Changed Signal
        self.db_list_wgt.itemSelectionChanged.connect(self.selection_changed)

        # Disable All buttons
        self.disable_unused_buttons()
        for btn in self.buttons1:
            btn.setEnabled(False)

        self.message.quit_btn.clicked.connect(self.message_quit_signal)
        self.message.continue_btn.clicked.connect(self.message_continue_signal)
        self.comment.continue_btn.clicked.connect(self.comment_continue_signal)
        self.comment.quit_btn.setEnabled(False)

    def message_quit_signal(self):
        self.quit = True
        self.message.hide()

    def message_continue_signal(self):
        self.quit = False
        self.message.hide()

    def comment_continue_signal(self):
        self.comment.hide()

    def check_and_create_initial_folders(self):
        if os.path.exists(os.path.join(self.directory, 'mapped_sam_files')):
            pass
        else:
            os.makedirs(os.path.join(self.directory, 'mapped_sam_files'))

        if os.path.exists(os.path.join(self.directory, 'unmapped_sam_files')):
            pass
        else:
            os.makedirs(os.path.join(self.directory, 'unmapped_sam_files'))

    def check_path(self, root, folders):
        existing_directories = []
        for dir in folders:
            if os.path.exists(os.path.join(root, dir)):
                existing_directories.append(dir)
        if len(existing_directories) > 0:
            message = "One or more of the following folders is already present:<br>"
            count = 1
            for d in existing_directories:
                message += "<br>%d.<b>%s</b><br>" % (count, d)
                count += 1
            message += "<br><br>These folders and/or their contexts can be moved to avoid risk of being over-written"
            self.message.windowTitle('Warning!')
            self.message.showMessage('<b>WARNING</b><br><br>%s<br>' % message)
            self.message.continue_btn.setEnabled(True)
            self.message.exec_()
            self.message.activateWindow()

    def print_comment(self, tag):
        text = self.printio.get_text_block(tag)
        self.comment.windowTitle('Message')
        self.comment.showMessage('%s' % text)
        self.comment.continue_btn.setEnabled(True)
        self.comment.show()

    # def check_for_sam_files(self):
    #     if len(self.fileio.get_file_list(self.directory, 'mapped_sam_files', '.sam')) <= 0 or \
    #             len(self.fileio.get_file_list(self.directory, 'unmapped_sam_files', '.sam')) <= 0:
    #         self.status_txt.setText('Waiting to load .sam files into selected directory...')
    #         thread.start_new_thread(self.monitor_directory_for_changes, ())
    #         self.disable_unused_buttons()
    #     else:
    #         self.initiate_all_buttons()

    # def initiate_all_buttons(self):
    #     self.status_txt.setText(self.directory)
    #     self.enable_all_buttons()

    def get_main_directory(self):
        self.directory = str(QtGui.QFileDialog.getExistingDirectory(QtGui.QFileDialog(), "Locate Work Folder",
                                                                    os.path.expanduser("~"),
                                                                    QtGui.QFileDialog.ShowDirsOnly))
        if self.directory == None:
            self.get_main_directory()
        else:
            self.check_and_create_initial_folders()
            self.disable_unused_buttons()
            self.proceed = 1
            thread.start_new_thread(self.monitor_directory_for_changes, ())
            pass

    def monitor_directory_for_changes(self):
        while self.proceed == 1:
            if len(self.fileio.get_file_list(self.directory, 'mapped_sam_files', '.sam')) <= 0 or \
                    len(self.fileio.get_file_list(self.directory, 'unmapped_sam_files', '.sam')) <= 0:
                self.gene_count_btn.setEnabled(False)
                self.junction_make_btn.setEnabled(False)
                self.gene_count_junction_make_btn.setEnabled(False)
                self.status_txt.setText('Waiting to load .sam files into selected directory...')
            else:
                self.junction_sequence_txt.setEnabled(True)
                self.exclude_sequence_txt.setEnabled(True)
                self.gene_count_btn.setEnabled(True)
                self.junction_make_btn.setEnabled(True)
                self.gene_count_junction_make_btn.setEnabled(True)
                self.status_txt.setText(self.directory)

            if os.path.exists(os.path.join(self.directory, 'blast_results_query')):
                if len(self.fileio.get_file_list(self.directory, 'blast_results_query', '.p')) <= 0:
                    self.query_blast_btn.setEnabled(False)
                else:
                    self.query_blast_btn.setEnabled(True)
            else:
                self.query_blast_btn.setEnabled(False)


            if os.path.exists(os.path.join(self.directory, 'gene_count_summary')) and len(self.fileio.get_file_list(
                    self.directory, 'mapped_sam_files', '.sam')) > 0:
                self.read_depth_btn.setEnabled(True)
            else:
                self.read_depth_btn.setEnabled(False)

            if self.clicked_button != None:
                for btn in self.buttons1:
                    btn.setEnabled(False)
            else:
                for btn in self.buttons1:
                    btn.setEnabled(True)

            self.gene_count_btn.setText("Gene Count")
            self.junction_make_btn.setText("Junction Make")
            self.gene_count_junction_make_btn.setText("Gene Count + Junction Make")
            self.query_blast_btn.setText("Blast Query")
            self.read_depth_btn.setText("Read Depth")
            time.sleep(0.1)


    def selection_changed(self):
        self.db_selection = self.db_list_wgt.item(self.db_list_wgt.currentRow())
        for row in self.g_db.select('*', id=str(self.db_selection.data)):
            self.junction_sequence_txt.setText(row[7])
            self.gene_dictionary = str(row[4])
            self.chromosome_list = str(row[8])
            self.blast_db_name = str(row[6])
            self.gene_list_file = str(row[5])
        self.enable_select_folder()

    def enable_select_folder(self):
        for btn in self.buttons1:
            btn.setEnabled(True)

    def stdout_ready(self):
        text = str(self.process.readAllStandardOutput()).strip()
        self.append(text)

    def stderr_ready(self):
        text = str(self.process.readAllStandardError())
        self.append(text)

    def append(self, text):
        self.status_bar.showMessage("Running %s script...  %s" % (self.clicked_button_text, next(self.bar)))
        cursor = self.status_text.textCursor()
        if self.start_match.match(text):
            cursor.select(QtGui.QTextCursor.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()
            cursor.movePosition(QtGui.QTextCursor.EndOfLine)
            cursor.insertText(text + "\n\n")
        else:
            cursor.select(QtGui.QTextCursor.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()
            cursor.insertText(text)
        self.status_text.ensureCursorVisible()

    def disable_unused_buttons(self):
        for btn in self.buttons:
            if btn is not self.clicked_button:
                btn.setEnabled(False)
            else:
                btn.setText("Abort")

        for btn in self.buttons1:
            btn.setEnabled(False)

        if self.clicked_button:
            self.db_list_wgt.setEnabled(False)

    # def enable_all_buttons(self):
    #     for btn in self.buttons:
    #         if btn is not self.clicked_button:
    #             btn.setEnabled(True)
    #         else:
    #             btn.setText(self.clicked_button_text)
    #     if self.clicked_button:
    #         self.db_list_wgt.setEnabled(True)

    def process_started(self):
        self.status_text.clear()
        self.proceed = 0
        self.disable_unused_buttons()

    def process_finished(self):
        self.quit = False
        self.status_bar.showMessage("%s process ended!" % self.clicked_button_text, 5000)
        self.clicked_button = None
        self.clicked_button_text = ''
        self.pid = None
        self.proceed = 1
        thread.start_new_thread(self.monitor_directory_for_changes, ())

    def kill_processes(self, name):
        time.sleep(1)
        os.system('kill $(ps aux | awk \'/' + name + '/ {print $2}\')')

    @QtCore.pyqtSlot()
    def on_prompt_box_stateChanged(self):
        self.prompt = self.prompt_box.checkState()

    @QtCore.pyqtSlot()
    def on_select_folder_btn_clicked(self):
        self.get_main_directory()

    @QtCore.pyqtSlot()
    def on_gene_count_btn_clicked(self):
        print self.prompt
        if self.clicked_button is None:
            self.clicked_button = self.sender()
            self.clicked_button_text = self.clicked_button.text()
            if self.prompt == 2:
                self.check_path(self.directory, ['gene_count_summary', 'chromosome_files'])
            if self.quit == False:
                self.status_bar.showMessage("Running %s ..." % self.clicked_button_text)
                if sys.platform == 'win32':
                    # self.process.start('python', ['gene_count_gui.py', self.directory, self.gene_dictionary, self.chromosome_list])
                    self.process.start('Gene Count\Gene Count.exe', [self.directory, self.gene_dictionary, self.chromosome_list])
                elif sys.platform == 'darwin':
                    self.process.start('Gene Count.app/Contents/MacOS/Gene Count', [self.directory, self.gene_dictionary,
                                                                                self.chromosome_list])
                    # self.process.start('python', ['gene_count_gui.py', self.directory, self.gene_dictionary, self.chromosome_list])
            else:
                self.process_finished()
        elif self.clicked_button == self.sender():
            self.process.terminate()
            self.kill_processes('Gene Count')

    @QtCore.pyqtSlot()
    def on_junction_make_btn_clicked(self):
        if self.clicked_button is None:
            self.clicked_button = self.sender()
            self.clicked_button_text = self.clicked_button.text()
            if self.prompt == 2:
                self.check_path(self.directory, ['junction_files', 'blast_results', 'blast_results_query'])
            if self.quit == False:
                self.status_bar.showMessage("Running %s ..." % self.clicked_button_text)
                if sys.platform == 'win32':
                    self.process.start('Junction Make\Junction Make.exe',
                                [self.directory, str(self.junction_sequence_txt.text()),
                                str(self.exclude_sequence_txt.text()), self.blast_db_name])
                elif sys.platform == 'darwin':
                    self.process.start('Junction Make.app/Contents/MacOS/Junction Make',
                                [self.directory, str(self.junction_sequence_txt.text()),
                                str(self.exclude_sequence_txt.text()), self.blast_db_name])
                    # print 'python ', 'junction_make_gui.py ', self.directory, str(self.junction_sequence_txt.text()),\
                    #     str(self.exclude_sequence_txt.text()), self.blast_db_name
                    # self.process.start('python', ['junction_make_gui.py', self.directory, str(self.junction_sequence_txt.text()),
                    #                           str(self.exclude_sequence_txt.text()), self.blast_db_name])


            else:
                self.process_finished()
        elif self.clicked_button == self.sender():
            self.process.terminate()

    @QtCore.pyqtSlot()
    def on_gene_count_junction_make_btn_clicked(self):
        if self.clicked_button is None:
            self.clicked_button = self.sender()
            self.clicked_button_text = self.clicked_button.text()
            if self.prompt == 2:
                self.check_path(self.directory, ['junction_files', 'blast_results', 'blast_results_query', 'gene_count_summary', 'chromosome_files'])
            if self.quit == False:
                self.status_bar.showMessage("Running %s ..." % self.clicked_button_text)
                if sys.platform == 'win32':
                    self.process.start('GCJM/GCJM.exe', [self.directory,
                                                                self.gene_dictionary, self.chromosome_list,
                                                                str(self.junction_sequence_txt.text()),
                                                                str(self.exclude_sequence_txt.text()),
                                                                self.blast_db_name,
                                                                'Gene Count\Gene Count.exe',
                                                                'Junction Make\Junction Make.exe'])
                elif sys.platform == 'darwin':
                    self.process.start('GCJM.app/Contents/MacOS/GCJM', [self.directory,
                                                                self.gene_dictionary, self.chromosome_list,
                                                                str(self.junction_sequence_txt.text()),
                                                                str(self.exclude_sequence_txt.text()),
                                                                self.blast_db_name,
                                                                '../../../Gene Count.app/Contents/MacOS/Gene Count',
                                                                '../../../Junction Make.app/Contents/MacOS/Junction Make'])
            else:
                self.process_finished()
        elif self.clicked_button == self.sender():
            self.process.terminate()
            self.kill_processes('Gene Count')

    @QtCore.pyqtSlot()
    def on_query_blast_btn_clicked(self):
        if self.clicked_button is None:
            self.clicked_button = self.sender()
            self.clicked_button_text = self.clicked_button.text()
            self.status_bar.showMessage("Running %s ..." % self.clicked_button_text)
            if sys.platform == 'win32':
                self.process.start('Blast Query\Blast Query.exe', [self.directory, self.gene_list_file])
            elif sys.platform == 'darwin':
                self.process.start('Blast Query.app/Contents/MacOS/Blast Query', [self.directory,
                                                                                  self.gene_list_file])
        elif self.clicked_button == self.sender():
            self.process.terminate()

    @QtCore.pyqtSlot()
    def on_read_depth_btn_clicked(self):
        if self.clicked_button is None:
            self.clicked_button = self.sender()
            self.clicked_button_text = self.clicked_button.text()
            self.status_bar.showMessage("Running %s ..." % self.clicked_button_text)
            if sys.platform == 'win32':
                self.process.start('Read Depth/Read Depth.exe', [self.directory,
                                                                 self.gene_list_file])
            elif sys.platform == 'darwin':
                self.process.start('Read Depth.app/Contents/MacOS/Read Depth', [self.directory,
                                                                                self.gene_list_file])
        elif self.clicked_button == self.sender():
            self.process.terminate()

    # @QtCore.pyqtSlot()
    # def on_tophat2_btn_clicked(self):
    #     if self.clicked_button is None:
    #         self.clicked_button = self.sender()
    #         self.clicked_button_text = self.clicked_button.text()
    #         self.status_bar.showMessage("Running %s ..." % self.clicked_button_text)
    #         self.process.start('python', ['tophat2_gui.py'])
    #     elif self.clicked_button == self.sender():
    #         self.process.terminate()



    # @QtCore.pyqtSlot()
    # def on_tophat2_gene_count_junction_make_btn_clicked(self):
    #     if self.clicked_button is None:
    #         self.clicked_button = self.sender()
    #         self.clicked_button_text = self.clicked_button.text()
    #         self.status_bar.showMessage("Running %s ..." % self.clicked_button_text)
    #         self.process.start('python', ['tophat2+gene_count+junction_make.py'])
    #     elif self.clicked_button == self.sender():
    #         self.process.terminate()

    # @QtCore.pyqtSlot()
    # def on_tophat2_gene_count_btn_clicked(self):
    #     if self.clicked_button is None:
    #         self.clicked_button = self.sender()
    #         self.clicked_button_text = self.clicked_button.text()
    #         self.status_bar.showMessage("Running %s ..." % self.clicked_button_text)
    #         self.process.start('python', ['tophat2+gene_count.py'])
    #     elif self.clicked_button == self.sender():
    #         self.process.terminate()

    # @QtCore.pyqtSlot()
    # def on_tophat2_junction_make_btn_clicked(self):
    #     if self.clicked_button is None:
    #         self.clicked_button = self.sender()
    #         self.clicked_button_text = self.clicked_button.text()
    #         self.status_bar.showMessage("Running %s ..." % self.clicked_button_text)
    #         self.process.start('python', ['tophat2+junction_make.py'])
    #     elif self.clicked_button == self.sender():
    #         self.process.terminate()

form = DEEPN_Launcher()
form.show()
app.exec_()
app.deleteLater()
sys.exit()
