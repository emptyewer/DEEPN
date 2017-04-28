import os
import sys
import time
import cStringIO
import traceback
from time import localtime, strftime
import pyqtgraph as pg
from collections import OrderedDict
from PyQt4 import QtCore, QtGui, uic
import libraries.xlsxwriter as xls

import functions.fileio_gui as f
import functions.plot as plot
import functions.process as process

app = QtGui.QApplication(sys.argv)
ui_path = os.path.join('ui', 'Read_Depth.ui')
if sys.platform == 'win32':
    ui_path = os.path.join('ui', 'Windows', 'Read_Depth.ui')
form_class, base_class = uic.loadUiType(ui_path)
pg.setConfigOption('background', (236, 236, 236))
pg.setConfigOption('foreground', 'k')

main_directory = sys.argv[1]
gene_list_file = sys.argv[2]
combined = int(sys.argv[3])

# def excepthook(excType, excValue, tracebackobj):
#     """
#     Global function to catch unhandled exceptions.
#
#     @param excType exception type
#     @param excValue exception value
#     @param tracebackobj traceback object
#     """
#     separator = '-' * 80
#     logFile = main_directory + "/read_depth_error.log"
#     notice = \
#         """An unhandled exception occurred. Please report the problem\n""" \
#         """using the error reporting dialog or via email to <%s>.\n""" \
#         """A log has been written to "%s".\n\nError information:\n""" % \
#         ("yourmail at server.com", "")
#
#     timeString = time.strftime("%Y-%m-%d, %H:%M:%S")
#
#     tbinfofile = cStringIO.StringIO()
#     traceback.print_tb(tracebackobj, None, tbinfofile)
#     tbinfofile.seek(0)
#     tbinfo = tbinfofile.read()
#     errmsg = '%s: \n%s' % (str(excType), str(excValue))
#     sections = [separator, timeString, separator, errmsg, separator, tbinfo]
#     msg = '\n'.join(sections)
#     try:
#         f = open(logFile, "w")
#         f.write(msg)
#         f.close()
#     except IOError:
#         pass
#
# sys.excepthook = excepthook

class QCustomTableWidgetItemInt(QtGui.QTableWidgetItem):
    def __init__(self, value):
        super(QCustomTableWidgetItemInt, self).__init__(QtCore.QString('%d' % value))

    def __lt__(self, other):
        if isinstance(other, QCustomTableWidgetItemInt):
            self_data_value = int(str(self.data(QtCore.Qt.EditRole).toString()))
            other_data_value = int(str(other.data(QtCore.Qt.EditRole).toString()))
            return self_data_value < other_data_value
        else:
            return QtGui.QTableWidgetItem.__lt__(self, other)

class GetReadList_Thread(QtCore.QThread):
    def __init__(self, directory, input_folder, dataset_name, selected_gene, parent):
        QtCore.QThread.__init__(self, parent)
        self.directory = directory
        self.input_folder = input_folder
        self.dataset_name = dataset_name
        self.selected_gene = selected_gene
        self.parent = parent

    def run(self):
        # if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == 'darwin':
        #     dir = '.' + self.dataset_name[:-4]
        # else:
        #     dir = self.dataset_name[:-4]
        filehandle = open(os.path.join(self.directory, 'gene_count_indices', self.dataset_name[:-4],
                                       self.selected_gene['chromosome'] + '.bin'), 'rb')
        self.parent.list_of_reads = []
        count = 0
        for line in filehandle.readlines():
            split = line.strip().split(':')
            if int(split[0]) >= int(self.selected_gene['chromosome_start']) and int(split[0]) <= int(self.selected_gene['chromosome_stop']):
                self.parent.list_of_reads.append(split[1])
                count += 1
        self.emit(QtCore.SIGNAL("GeneListFinished"))

class CalculateDepth_Thread(QtCore.QThread):
    def __init__(self, parent):
        QtCore.QThread.__init__(self, parent)
        self.process = process.process()
        self.parent = parent

    def make_list_of_mRNA(self):
        sequence = []
        for position in range(0, len(self.parent.selected_gene['mRNA']), self.parent.interval):
            seq = self.parent.selected_gene['mRNA'][position:position + 20]
            sequence.append((position, seq))
            position += self.parent.interval
        return sequence

    def run(self):
        sequences = self.make_list_of_mRNA()
        self.parent.results = []
        for (position, item) in sequences:
            item_reverse = self.process.reverse_complement(item)
            count = 0
            countt = 0
            for read in self.parent.list_of_reads:
                countt += 1
                if (str(item) in str(read)) or (str(item_reverse) in str(read)):
                    count += 1
            orfness = "Not in CDS"
            if int(position) >= int(self.parent.selected_gene['orf_start']) and int(position) <= int(self.parent.selected_gene['orf_stop']):
                    orfness = "In ORF"
            self.parent.results.append((position+1, count, orfness))
        self.emit(QtCore.SIGNAL('CalculateDepthFinished'))


class Read_Depth_Gui(QtGui.QMainWindow, form_class):
    depth_calculated_signal = QtCore.pyqtSignal()
    dataset_loaded_signal = QtCore.pyqtSignal()

    def __init__(self, folder, directory, gene_list_file, *args):
        super(Read_Depth_Gui, self).__init__(*args)
        self.setupUi(self)
        self.input_folder = folder
        self.interval = 100
        self.interval_spin.setValue(100)
        self.allowed_mismatches = 1
        self.directory = directory
        self.gene_list_file = gene_list_file
        self.fileio = f.fileio()
        self.list_of_reads = []
        self.plot = plot.RDPlot("Base Pair", "# Hits")
        self.selected_accession_number_name = ''
        self.selected_gene = {}
        self.dataset_name = '-- Select --'
        self.gene_list = OrderedDict()
        self.datasets_cache = OrderedDict()
        self.accession_numbers_list = QtCore.QStringList()
        self._initialize_ui_elements()
        self.process = process.process()
        self.read_list_thread = GetReadList_Thread(self.directory, self.input_folder, self.dataset_name,
                                                   self.selected_gene, self)
        self.connect(self.read_list_thread, QtCore.SIGNAL("GeneListFinished"), self.dataset_loaded)
        self.calculate_depth_thread = CalculateDepth_Thread(self)
        self.connect(self.calculate_depth_thread, QtCore.SIGNAL("CalculateDepthFinished"), self.load_table_w_data)


    def populate_accession_suggestions(self):
        self.accession_numbers_list.removeDuplicates()
        self.completer = QtGui.QCompleter(self.accession_numbers_list, self)
        self.completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.accession_number_search.setCompleter(self.completer)
        self.accession_number_search.setText("NM_")
        self.accession_number_search.textChanged.connect(self._accession_number_search_changed)
        self.interval_spin.valueChanged.connect(self.on_interval_spin_changed)

    def sequence_format_html(self, selected_gene):
        sequence = selected_gene['mRNA']
        start = selected_gene['orf_start'] - 1
        stop = selected_gene['orf_stop']
        html_string = '<html><body>> %s (%s) on chromosome %s (%s) ORF Start: %d ORF Stop: %d<br><font ' \
                      'color="silver">' % (selected_gene['nm_number'], selected_gene['gene_name'],
                                           selected_gene['chromosome'], selected_gene['intron'],
                                           selected_gene['orf_start'], selected_gene['orf_stop'])
        html_string += sequence[:start] + '</font>'
        html_string += sequence[start:stop]
        html_string += '<font color="silver">' + sequence[stop:] + '</font>'
        html_string += '</body></html>'
        return html_string

    @QtCore.pyqtSlot()
    def _accession_number_search_changed(self):
        self.selected_accession_number_name = str(self.accession_number_search.text())
        try:
            self.selected_gene = self.gene_list[str(self.selected_accession_number_name)]
            self.read_list_thread.selected_gene = self.selected_gene
            _sequence = self.sequence_format_html(self.selected_gene)
            self.sequence_browser.setHtml(QtCore.QString(_sequence))
            self.set_buttons_status(True)
            if self.dataset_name != '-- Select --':
                self.set_buttons_status(False)
                self.read_list_thread.start()
        except KeyError:
            self.set_buttons_status(False)
            self.selected_gene = {}
            pass

    @QtCore.pyqtSlot()
    def on_interval_spin_changed(self):
        self.interval = self.interval_spin.value()
        if self.dataset_name != '-- Select --':
            self.set_buttons_status(False)
            self.calculate_depth_thread.start()

    @QtCore.pyqtSlot()
    def dataset_loaded(self):
       self.set_buttons_status(False)
       self.calculate_depth_thread.start()

    @QtCore.pyqtSlot()
    def load_table_w_data(self):
        self.set_buttons_status(True)
        self.results_lst.clearContents()
        self.results_lst.setSortingEnabled(False)
        self.results_lst.setRowCount(len(self.results))
        for i, data in enumerate(self.results):
            self.results_lst.setItem(i, 0, QCustomTableWidgetItemInt(data[0]))
            self.results_lst.setItem(i, 1, QCustomTableWidgetItemInt(data[1]))
            self.results_lst.setItem(i, 2, QtGui.QTableWidgetItem(data[2]))

        if self.results[0][2] != 'NULL':
            self.plot.plot(self.results, self.selected_gene['orf_start'], self.selected_gene['orf_stop'])


    def get_accession_number_list(self, gene_list_file):
        fh = open(os.path.join('lists', gene_list_file), 'r')
        gene_list = OrderedDict()
        accession_list = QtCore.QStringList()
        for line in fh.readlines():
            split = line.split()
            gene_list[split[0]] = {'nm_number': split[0], 'gene_name': split[1], 'orf_start': int(split[6])+1,
                                   'orf_stop': int(split[7]), 'mRNA': split[9], 'intron': split[8],
                                   'chromosome': split[2], 'chromosome_start': split[4], 'chromosome_stop': split[5]}
            accession_list.append(QtCore.QString(split[0]))
        return gene_list, accession_list

    def _initialize_ui_elements(self):
        self.plot_layout.addWidget(self.plot)
        self.gene_list, self.accession_numbers_list = self.get_accession_number_list(self.gene_list_file)
        self.populate_accession_suggestions()
        for fi in self.fileio.get_file_list(self.directory, self.input_folder, '.sam'):
            self.sam_files_ddl_1.addItem(fi)
        self.sam_files_ddl_1.currentIndexChanged.connect(self._dataset_selected)
        self.set_buttons_status(False)

    def set_buttons_status(self, status):
        self.sam_files_ddl_1.setEnabled(status)
        self.save_btn.setEnabled(status)
        self.results_lst.setEnabled(status)
        self.sequence_browser.setEnabled(status)
        self.plot.setEnabled(status)
        self.interval_spin.setEnabled(status)

    def _get_sender_index_name(self, sender):
        index = 0
        sender_objectname = sender.objectName()
        try:
            index = int(sender_objectname[-1:]) - 1
        except ValueError:
            pass
        dataset_name = '-- Select --'
        try:
            dataset_name = str(self.sender().currentText())
        except AttributeError:
            pass
        return index, dataset_name

    def _dataset_selected(self):
        if isinstance(self.sender(), QtGui.QComboBox):
            index, self.dataset_name = self._get_sender_index_name(self.sender())
            self.read_list_thread.dataset_name = self.dataset_name
        else:
            pass

        if self.dataset_name != '-- Select --':
            self.set_buttons_status(False)
            self.read_list_thread.start()
        else:
            self.set_buttons_status(False)

    @QtCore.pyqtSlot()
    def on_save_btn_clicked(self):
        self.save_query_results(self.selected_accession_number_name, self.directory)
        self.status_bar.showMessage("Saved to file %s" % os.path.join('depth_results', '%s_%s.xlsx' %
                                    (self.selected_accession_number_name, strftime("%Y-%m-%d_%Hh%Mm%Ss",
                                                                                   localtime()))),
                                    5000)

    def save_query_results(self, file_name, directory, path='depth_results'):
        self.fileio.create_new_folder(directory, path)
        workbook = xls.Workbook(os.path.join(directory, path, '%s_%s.xlsx' %
                                             (file_name, strftime("%Y-%m-%d_%Hh%Mm%Ss", localtime()))))
        worksheet = workbook.add_worksheet(self.dataset_name[:25])
        for row, row_item in enumerate(self.results):
            for col, item in enumerate(row_item):
                worksheet.write(row, col, item)
        workbook.close()


def appExit():
    app.quit()
    sys.exit()

if __name__ == '__main__':
    input_folder = 'mapped_sam_files'
    if combined == 1:
        input_folder = 'sam_files'
    form = Read_Depth_Gui(input_folder, main_directory, gene_list_file)
    form.show()
    app.aboutToQuit.connect(appExit)
    app.exec_()
