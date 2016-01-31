import os
import sys
import time
import pyqtgraph as pg
from PyQt4 import QtCore, QtGui, uic
import numpy as np

app = QtGui.QApplication(sys.argv)
form_class, base_class = uic.loadUiType(os.path.join(os.path.curdir, 'ui', 'QBGraph.ui'))

__all__ = ['BarGraphItem']

class BarGraphItem(pg.GraphicsObject):
    def __init__(self, **opts):
        pg.GraphicsObject.__init__(self)
        self.opts = dict(
            x=None,
            y=None,
            x0=None,
            y0=None,
            x1=None,
            y1=None,
            height=None,
            width=None,
            pen=None,
            brush=None,
            pens=None,
            brushes=None,
        )
        self.setOpts(**opts)

    def setOpts(self, **opts):
        self.opts.update(opts)
        self.picture = None
        self.update()
        self.informViewBoundsChanged()

    def drawPicture(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)

        pen = self.opts['pen']
        pens = self.opts['pens']

        if pen is None and pens is None:
            pen = pg.getConfigOption('foreground')

        brush = self.opts['brush']
        brushes = self.opts['brushes']
        if brush is None and brushes is None:
            brush = (128, 128, 128)

        def asarray(x):
            if x is None or np.isscalar(x) or isinstance(x, np.ndarray):
                return x
            return np.array(x)


        x = asarray(self.opts.get('x'))
        x0 = asarray(self.opts.get('x0'))
        x1 = asarray(self.opts.get('x1'))
        width = asarray(self.opts.get('width'))

        if x0 is None:
            if width is None:
                raise Exception('must specify either x0 or width')
            if x1 is not None:
                x0 = x1 - width
            elif x is not None:
                x0 = x - width/2.
            else:
                raise Exception('must specify at least one of x, x0, or x1')
        if width is None:
            if x1 is None:
                raise Exception('must specify either x1 or width')
            width = x1 - x0

        y = asarray(self.opts.get('y'))
        y0 = asarray(self.opts.get('y0'))
        y1 = asarray(self.opts.get('y1'))
        height = asarray(self.opts.get('height'))

        if y0 is None:
            if height is None:
                y0 = 0
            elif y1 is not None:
                y0 = y1 - height
            elif y is not None:
                y0 = y - height/2.
            else:
                y0 = 0
        if height is None:
            if y1 is None:
                raise Exception('must specify either y1 or height')
            height = y1 - y0

        p.setPen(pg.mkPen(pen))
        p.setBrush(pg.mkBrush(brush))
        for i in range(len(x0)):
            if pens is not None:
                p.setPen(pg.mkPen(pens[i]))
            if brushes is not None:
                p.setBrush(pg.mkBrush(brushes[i]))

            if np.isscalar(y0):
                y = y0
            else:
                y = y0[i]
            if np.isscalar(width):
                w = width
            else:
                w = width[i]
            p.drawRect(QtCore.QRectF(x0[i], y, w, height[i]))
        p.end()
        self.prepareGeometryChange()


    def paint(self, p, *args):
        if self.picture is None:
            self.drawPicture()
        self.picture.play(p)

    def boundingRect(self):
        if self.picture is None:
            self.drawPicture()
        return QtCore.QRectF(self.picture.boundingRect())

class QBPlot(QtGui.QDialog, form_class):
    def __init__(self, xtitle, ytitle,*args):
        super(QBPlot, self).__init__(*args)
        self.setupUi(self)
        self.x_axis_title = xtitle
        self.y_axis_title = ytitle
        pg.setConfigOption('background', (226, 226, 226))
        pg.setConfigOption('foreground', 'k')

    def initialize_plot(self):
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.plotItem.showGrid(True, True, alpha=0.2)
        self.plot_widget.plotItem.setLabel('bottom', text=self.x_axis_title)
        self.plot_widget.plotItem.setLabel('left', text=self.y_axis_title)
        self.plot_widget.plotItem.setMouseEnabled(x=False, y=False)
        self.plot_widget_viewbox = self.plot_widget.plotItem.getViewBox()
        self.plot_widget.plotItem.enableAutoRange(axis=self.plot_widget_viewbox.XYAxes)
        self.plot_layout.addWidget(self.plot_widget)
        self.plot_widget.plotItem.addLegend()
        self.legend_added = 0

    def add_legends(self):
        style = pg.PlotDataItem(pen=pg.mkPen({'color':'1A64B0','width': 4}))
        self.plot_widget.plotItem.legend.addItem(style, "In ORF")
        style = pg.PlotDataItem(pen=pg.mkPen({'color':'1CC5FF','width': 4}))
        self.plot_widget.plotItem.legend.addItem(style, "Upstream")
        style = pg.PlotDataItem(pen=pg.mkPen({'color':'777777','width': 4}))
        self.plot_widget.plotItem.legend.addItem(style, "Downstream / Out of Frame")
        style = pg.PlotDataItem(pen=pg.mkPen({'color':'D13A26','width': 4}))
        self.plot_widget.plotItem.legend.addItem(style, "Start/Stop of CDS")

    def plot(self, data, start, stop):
        self.plot_widget.clear()
        x_grey = []
        y_grey = []
        x_blue = []
        y_blue = []
        x_lightblue = []
        y_lightblue = []
        max_count = 0
        for row, row_item in enumerate(data):
            if row != 0:
                if row_item[4] == "In Frame" and row_item[3] == "In ORF":
                    x_blue.append(int(row_item[0]))
                    y_blue.append(float(row_item[1]))
                    if max_count < float(row_item[1]):
                        max_count = float(row_item[1])
                elif row_item[4] == "In Frame" and row_item[3] == "Upstream":
                    x_lightblue.append(int(row_item[0]))
                    y_lightblue.append(float(row_item[1]))
                    if max_count < float(row_item[1]):
                        max_count = float(row_item[1])
                else:
                    x_grey.append(int(row_item[0]))
                    y_grey.append(float(row_item[1]))
                    if max_count < float(row_item[1]):
                        max_count = float(row_item[1])

        x_neg = [start, stop]
        if max_count > 1:
            y_neg = [max_count * 0.05 * -1, max_count * 0.05 * -1]
        else:
            y_neg = [-1, -1]

        self.plot_widget.addItem(BarGraphItem(x=x_blue, height=y_blue, width=5,
                                              pen=pg.mkPen({'color':'1A64B0','width': 1}),
                                              brush='1A64B0'))


        self.plot_widget.addItem(BarGraphItem(x=x_lightblue, height=y_lightblue, width=5,
                                              pen=pg.mkPen({'color':'1CC5FF','width': 1}),
                                              brush='1CC5FF'))


        self.plot_widget.addItem(BarGraphItem(x=x_grey, height=y_grey, width=5,
                                              pen=pg.mkPen({'color':'777777','width': 1}),
                                              brush='777777'))


        self.plot_widget.addItem(BarGraphItem(x=x_neg, height=y_neg, width=20,
                                              pen=pg.mkPen({'color':'D13A26','width': 1}),
                                              brush='D13A26'))

        if self.legend_added == 0:
            self.add_legends()
            self.legend_added = 1


    def clear_plot(self):
        self.plot_widget.clear()


class RDPlot(pg.PlotWidget):
    def __init__(self, xtitle, ytitle, *args):
        super(RDPlot, self).__init__(*args)
        self.x_axis_title = xtitle
        self.y_axis_title = ytitle
        self.plotItem.showGrid(True, True, alpha=0.2)
        self.plotItem.setLabel('bottom', text=self.x_axis_title)
        self.plotItem.setLabel('left', text=self.y_axis_title)
        self.plotItem.setMouseEnabled(x=False, y=False)
        self.plot_widget_viewbox = self.plotItem.getViewBox()
        self.plotItem.enableAutoRange(axis=self.plot_widget_viewbox.XYAxes)
        self.plotItem.addLegend()
        self.legend_added = 0

    def add_legends(self):
        style = pg.PlotDataItem(pen=pg.mkPen({'color':'1A64B0','width': 8}))
        self.plotItem.legend.addItem(style, "In ORF")
        style = pg.PlotDataItem(pen=pg.mkPen({'color':'777777','width': 8}))
        self.plotItem.legend.addItem(style, "Not in CDS")
        style = pg.PlotDataItem(pen=pg.mkPen({'color':'D13A26','width': 8}))
        self.plotItem.legend.addItem(style, "Start/Stop of CDS")

    def plot(self, data, start, stop):
        self.clear()
        x_grey = []
        y_grey = []
        x_blue = []
        y_blue = []
        max_count = 0
        for bp, count, orf in data:
            if orf == "In ORF":
                x_blue.append(int(bp))
                y_blue.append(int(count))
                if max_count < count:
                    max_count = count
            else:
                x_grey.append(int(bp))
                y_grey.append(int(count))
                if max_count < count:
                    max_count = count

        x_neg = [start, stop]
        if max_count > 1:
            y_neg = [max_count * 0.05 * -1, max_count * 0.05 * -1]
        else:
            y_neg = [-1, -1]

        self.addItem(BarGraphItem(x=x_blue, height=y_blue, width=15,
                                  pen=pg.mkPen({'color':'1A64B0','width': 1}),
                                  brush='1A64B0'))


        self.addItem(BarGraphItem(x=x_grey, height=y_grey, width=15,
                                  pen=pg.mkPen({'color':'777777','width': 1}),
                                  brush='777777'))


        self.addItem(BarGraphItem(x=x_neg, height=y_neg, width=20,
                                  pen=pg.mkPen({'color':'D13A26','width': 1}),
                                  brush='D13A26'))

        if self.legend_added == 0:
            self.add_legends()
            self.legend_added = 1


