import os
import sys
from time import localtime, strftime
import pyqtgraph as pg
from PyQt4 import QtCore, QtGui, uic
from collections import OrderedDict
import cPickle
import libraries.xlsxwriter as xls

import functions.fileio_gui as f
import functions.plot as plot

app = QtGui.QApplication(sys.argv)
form_class, base_class = uic.loadUiType(os.path.join('ui', 'Query_Blast.ui'))

main_directory = sys.argv[1]
gene_list_file = sys.argv[2]

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

class QCustomTableWidgetItemFloat(QtGui.QTableWidgetItem):
    def __init__(self, value):
        super(QCustomTableWidgetItemFloat, self).__init__(QtCore.QString('%.3f' % value))

    def __lt__(self, other):
        if isinstance(other, QCustomTableWidgetItemFloat):
            self_data_value = float(str(self.data(QtCore.Qt.EditRole).toString()))
            other_data_value = float(str(other.data(QtCore.Qt.EditRole).toString()))
            return self_data_value < other_data_value
        else:
            return QtGui.QTableWidgetItem.__lt__(self, other)

class Query_Blast_Gui(QtGui.QMainWindow, form_class):
    def __init__(self, folder, directory, gene_list_file, *args):
        super(Query_Blast_Gui, self).__init__(*args)
        self.setupUi(self)
        self.input_folder = folder
        self.directory = directory
        self.gene_list_file = gene_list_file

        self.fileio = f.fileio()
        # Selections from GUI
        self.selected_accession_number_name = ''
        self.selected_dataset_names = ['-- Select --', '-- Select --', '-- Select --']
        # Generic Table Names
        self.table = None
        self.table_filtered = None
        # Cache for storing data
        self.selected_gene = {}
        self.gene_information = OrderedDict()
        self.datasets_cache = OrderedDict()
        self.accession_numbers_list = QtCore.QStringList()
        # Methods
        self._initialize_ui_elements()
        # Results Store
        self.results = [[], [], []]
        self.filtered_results = [[], [], []]

        self.graph1 = plot.QBPlot('Base Pair', 'Junction Count (ppm)')
        self.tabWidget_1.addTab(self.graph1, "Plot")
        self.graph1.initialize_plot()

        self.graph2 = plot.QBPlot('Base Pair', 'Junction Count (ppm)')
        self.tabWidget_2.addTab(self.graph2, "Plot")
        self.graph2.initialize_plot()

        self.graph3 = plot.QBPlot('Base Pair', 'Junction Count (ppm)')
        self.tabWidget_3.addTab(self.graph3, "Plot")
        self.graph3.initialize_plot()


    def populate_accession_suggestions(self):
        self.accession_numbers_list.removeDuplicates()
        self.completer = QtGui.QCompleter(self.accession_numbers_list, self)
        self.completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.accession_number_search.setCompleter(self.completer)
        self.accession_number_search.setText("NM_")
        self.accession_number_search.textChanged.connect(self._accession_number_search_changed)

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

    def get_accession_number_list(self, directory, gene_list_file):
        fh = open(os.path.join('lists', gene_list_file), 'r')
        gene_list = {}
        accession_list = QtCore.QStringList()
        for line in fh.readlines():
            split = line.split()
            gene_list[split[0]] = {'nm_number': split[0], 'gene_name': split[1], 'orf_start': int(split[6])+1, 'orf_stop': int(split[7]), 'mRNA': split[9], 'intron': split[8], 'chromosome': split[2]}
            accession_list.append(QtCore.QString(split[0]))
        return gene_list, accession_list

    def make_condensed_list(self, inlist):
        count = 0
        roster = set()
        return_list = []
        [item for item in inlist if item[0] not in roster and not roster.add(item[0])]
        for item in roster:
            for thing in inlist:
                if thing[0] == item:
                    count += thing[2]
            return_list.append((item, count))
            count = 0
        return_list.sort()
        return return_list

    def _accession_number_search_changed(self):
        self.selected_accession_number_name = str(self.accession_number_search.text())
        try:
            self.selected_gene = self.gene_information[str(self.selected_accession_number_name)]
            _sequence = self.sequence_format_html(self.selected_gene)
            self.sequence_browser.setHtml(QtCore.QString(_sequence))
        except KeyError:
            self.selected_gene = {}
            pass

        if self.selected_gene != {}:
            self._dataset_selected()


    def _initialize_ui_elements(self):
        self.gene_information, self.accession_numbers_list = self.get_accession_number_list(self.directory,
                                                                                            self.gene_list_file)
        self.populate_accession_suggestions()
        self.blast_dataset_ddl_1.addItem('-- Select --')
        self.blast_dataset_ddl_2.addItem('-- Select --')
        self.blast_dataset_ddl_3.addItem('-- Select --')
        for fi in self.fileio.get_file_list(self.directory, self.input_folder, '.p'):
            self.blast_dataset_ddl_1.addItem(fi)
            self.blast_dataset_ddl_2.addItem(fi)
            self.blast_dataset_ddl_3.addItem(fi)
        self.blast_dataset_ddl_1.currentIndexChanged.connect(self._dataset_selected)
        self.blast_dataset_ddl_2.currentIndexChanged.connect(self._dataset_selected)
        self.blast_dataset_ddl_3.currentIndexChanged.connect(self._dataset_selected)

    def _initialize_results_store(self):
        self.results = [[], [], []]
        self.filtered_results = [[], [], []]
        self.results[0].append(('Position', "# Junctions", "Query Start", "CDS Status", "Reading Frame"))
        self.filtered_results[0].append(('Position', "# Junctions"))
        self.results[1].append(('Position', "# Junctions", "Query Start", "CDS Status", "Reading Frame"))
        self.filtered_results[1].append(('Position', "# Junctions"))
        self.results[2].append(('Position', "# Junctions", "Query Start", "CDS Status", "Reading Frame"))
        self.filtered_results[2].append(('Position', "# Junctions"))

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

    def get_filtered_data(self, dataset1, dataset2, table, index, name, filtered_results):
        freq1 = [(int(position.split('-')[0]), position, dataset1[name].count(position) * 1000000 / float(dataset1['total'])) for position in set(dataset1[name])]
        freq1B = self.make_condensed_list(freq1)

        freq2 = [(int(position.split('-')[0]), position, dataset2[name].count(position) * 1000000 / float(dataset2['total'])) for position in set(dataset2[name])]
        freq2B = self.make_condensed_list(freq2)
        for item2 in freq2B:
            if item2[0] in [item[0] for item in freq1B]:
                filtered_results[index].append((item2[0], round(item2[1], 3)))
        table.clearContents()
        table.setSortingEnabled(False)
        table.setRowCount(len(filtered_results[index]) - 1)
        for i, row in enumerate(filtered_results[index]):
            if i != 0:
                table.setItem(i-1, 0, QCustomTableWidgetItemInt(row[0]))
                table.setItem(i-1, 1, QCustomTableWidgetItemFloat(row[1]))
        table.setSortingEnabled(True)
        table.sortItems(1, 1)

    def _dataset_selected(self):
        index = 0
        dataset_name = self.selected_dataset_names[index]
        self._initialize_results_store()

        if isinstance(self.sender(), QtGui.QComboBox):
            index, dataset_name = self._get_sender_index_name(self.sender())
            self.selected_dataset_names[index] = dataset_name
        else:
            pass

        if dataset_name != '-- Select --':
            try:
                self.datasets_cache[dataset_name]
            except KeyError:
                self.datasets_cache[dataset_name] = cPickle.load(open(os.path.join(self.directory, self.input_folder,
                                                                                   dataset_name), 'rb'))

            count = 1
            for name in self.selected_dataset_names:
                if name != '-- Select --':
                    dataset = self.datasets_cache[name]
                    try:
                        exec("%s = %s" % ("self.table", "self.results_lst_" + str(count)))
                        exec("%s = %s" % ("self.table_filtered", "self.results_filtered_lst_" + str(count)))
                        exec("%s = %s" % ("self.graph", "self.graph" + str(count)))
                    except AttributeError:
                        pass

                    try:
                        self.table.clearContents()
                        frequency = [(int(position.split('-')[0]), position, dataset[self.selected_accession_number_name].count(position)
                                      * 1000000 / float(dataset['total'])) for position in set(dataset[self.selected_accession_number_name])]
                        self.table.setSortingEnabled(False)
                        self.table.setRowCount(len(frequency))
                        for row, values in enumerate(sorted(frequency, key=lambda x: x[2], reverse=True)):
                            frame = 'Not in Frame'
                            orf = "Not in ORF"
                            fudge_factor = int(values[1].split('-')[1]) - 1
                            num = int(values[0]) - int(self.selected_gene['orf_start']) - fudge_factor
                            if num % 3 == 0 or num == 0:
                                frame = 'In Frame'
                            if self.selected_gene['intron']== 'INTRON':
                                frame = 'Intron'
                            if int(values[0]) < int(self.selected_gene['orf_start']):
                                orf = 'Upstream'
                            if int(values[0]) > int(self.selected_gene['orf_stop']):
                                orf = 'Downstream'
                            if int(values[0]) >= int(self.selected_gene['orf_start']) and int(values[0]) <= int(self.selected_gene['orf_stop']):
                                orf = "In ORF"
                            self.table.setItem(row, 0, QCustomTableWidgetItemInt(values[0]))
                            self.table.setItem(row, 1, QCustomTableWidgetItemFloat(round(values[2], 3)))
                            self.table.setItem(row, 2, QCustomTableWidgetItemInt(fudge_factor + 1))
                            self.table.setItem(row, 3, QtGui.QTableWidgetItem(orf))
                            self.table.setItem(row, 4, QtGui.QTableWidgetItem(frame))
                            data = (str(values[0]), str(round(values[2], 3)), str(fudge_factor + 1), orf, frame)
                            self.results[count - 1].append(data)
                        self.table.setSortingEnabled(True)
                        self.table.sortItems(1, 1)
                        self.graph.plot(self.results[count - 1], self.selected_gene['orf_start'], self.selected_gene['orf_stop'])
                        try:
                            self.get_filtered_data(self.datasets_cache[self.selected_dataset_names[0]], dataset,
                                                      self.table_filtered, count - 1, self.selected_accession_number_name,
                                                      self.filtered_results)
                        except KeyError:
                            pass

                    except KeyError:
                        self.status_bar.showMessage("Gene Not Found!", 5000)
                        self.graph.clear_plot()
                        self.table.clearContents()
                        self.table_filtered.clearContents()
                        self.table.setRowCount(1)
                        self.table_filtered.setRowCount(1)
                        for i in range(5):
                            self.table.setItem(0, i, QtGui.QTableWidgetItem("NULL"))
                            self.table_filtered.setItem(0, i, QtGui.QTableWidgetItem("NULL"))
                    count += 1

    @QtCore.pyqtSlot()
    def on_save_btn_clicked(self):
        self.save_query_results(self.results, self.filtered_results, self.selected_accession_number_name,
                                self.selected_dataset_names, self.directory)
        self.status_bar.showMessage("Saved to file %s" % os.path.join('query_results', '%s_%s.xlsx' %
                                    (self.selected_accession_number_name, strftime("%Y-%m-%d_%Hh%Mm%Ss",
                                                                                   localtime()))),
                                    5000)

    def save_query_results(self, results, filtered_results, file_name, dataset_names, directory, path='query_results'):
        self.fileio.create_new_folder(directory, path)
        workbook = xls.Workbook(os.path.join(directory, path, '%s_%s.xlsx' %
                                             (file_name, strftime("%Y-%m-%d_%Hh%Mm%Ss", localtime()))))
        for index, result in enumerate(results):
            worksheet = workbook.add_worksheet(dataset_names[index][:20] + '..._' + str(index))
            for row, row_item in enumerate(result):
                for col, item in enumerate(row_item):
                    worksheet.write(row, col, item)

            for row, row_item in enumerate(filtered_results[index]):
                for col, item in enumerate(row_item):
                    worksheet.write(row, col+10, item)
        workbook.close()

if __name__ == '__main__':
    input_folder = 'blast_results_query'
    form = Query_Blast_Gui(input_folder, main_directory, gene_list_file)
    form.show()
    app.exec_()
    app.deleteLater()
    sys.exit()
