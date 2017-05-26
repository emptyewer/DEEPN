import math
import re
import matplotlib as mpl
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.colors as colors
import matplotlib.cm as cm
import numpy as np
from matplotlib.figure import Figure
from PyQt4 import QtGui

class GraphFrame(QtGui.QFrame):
    def __init__(self, filename, parent=None):
        super(GraphFrame, self).__init__(parent)
        self.setFrameShape(QtGui.QFrame.NoFrame)
        self.parent = parent
        self.graph_view = GraphView(filename, self)

    def resizeEvent(self, event):
        self.graph_view.setGeometry(self.rect())

class GraphView(QtGui.QWidget):
    def __init__(self, filename, parent=None):
        super(GraphView, self).__init__(parent)
        self.dpi = 300
        self.filename = filename
        self.data = None
        self.fig = Figure((4.5, 4.5), dpi=self.dpi)
        self.axes = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        self.canvas.mpl_connect('button_press_event', self._onpick)
        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.canvas)
        self.layout.setStretchFactor(self.canvas, 1)
        self.setLayout(self.layout)
        self.x = []
        self.y = []
        self.read_data()
        self.load_data()
        self.canvas.show()
        self.set_parameters()

    def read_data(self):
        fh = open(self.filename)
        for line in fh.readlines():
            if not re.match(r'[A-Za-z]', line):
                values = line.strip().split(',')
                try:
                    self.x.append(float(values[0]))
                    self.y.append(float(values[2]))
                except:
                    pass
        self.x = np.array(self.x)
        self.y = np.array(self.y)

    def load_data(self):
        self.bar = self.axes.plot(self.x, self.y, linewidth=1.0)

    def _get_clicked_residues(self, event):
        xmin, xmax = self.axes.get_xlim()
        return(int(math.ceil(event.xdata - xmin))-1)

    def _onpick(self, event):
        pass

    def set_parameters(self):
        self.axes.tick_params(axis=u'both', which=u'both', length=0)
        self.axes.set_xlim(min(self.x), max(self.x))
        self.axes.set_ylim(0, max(self.y) + 1)
        self.axes.set_xlabel('Threshold')
        self.axes.set_ylabel('Overdispersion')
        # fractions = self.y / max(self.y)
        # normalized_colors = colors.Normalize(fractions.min(), fractions.max())
        # count = 0
        # for rect in self.bar:
        #     c = cm.jet(normalized_colors(fractions[count]))
        #     rect.set_facecolor(c)
        #     count += 1
        # self.fig.patch.set_facecolor((0.886, 0.886, 0.886))
        ticks_font = mpl.font_manager.FontProperties(family='times new roman', style='normal', size=12,
                                                     weight='normal', stretch='normal')
        labels = [self.axes.title, self.axes.xaxis.label, self.axes.yaxis.label]
        labels += self.axes.get_xticklabels() + self.axes.get_yticklabels()
        for item in labels:
            item.set_fontproperties(ticks_font)
            item.set_fontsize(4)
        self.fig.set_size_inches(30, self.fig.get_figheight(), forward=True)
    #
    # def update_graph(self):
    #     self.axes.clear()
    #     if self.pmap.use_ca:
    #         self.xcoor = self.pmap.residue_numbers_ca[self.pmap.parent.current_model]
    #     else:
    #         self.xcoor = self.pmap.residue_numbers_cb[self.pmap.parent.current_model]
    #     self.ycoor = self.pmap.histogram_maps[self.pmap.parent.current_model]
    #     self.bar = self.axes.bar(self.xcoor, self.ycoor, width=1.0, linewidth=0)
    #     self.set_parameters()
    #     self.canvas.draw()
