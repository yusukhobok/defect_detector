import sys

import numpy as np
import pyqtgraph as pg
from matplotlib import image
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QFileDialog

from main_logic import MainLogic


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("Defect Detector")
        self.open_avi_action = QtWidgets.QAction("Open video...")
        self.open_avi_action.triggered.connect(self.open_avi)
        self.open_csv_action = QtWidgets.QAction("Open CSV...")
        self.open_csv_action.triggered.connect(self.open_csv)
        self.open_csv_action.setShortcut("Ctrl+O")

        self.menuBar().addAction(self.open_avi_action)
        self.menuBar().addAction(self.open_csv_action)

        self.gaps_list = QtWidgets.QListView()
        self.gaps_model = QtGui.QStandardItemModel()
        self.gaps_list.setModel(self.gaps_model)
        self.gaps_list.pressed["const QModelIndex&"].connect(self.on_select_element)
        self.gaps_list.activated["const QModelIndex&"].connect(self.on_select_element)

        self.plotArea = pg.PlotWidget()
        self.plotArea.setCursor(QtCore.Qt.CrossCursor)
        self.plotArea.setMenuEnabled(False)
        self.plotArea.scene().sigMouseClicked.connect(self.mouse_clicked)
        self.plotArea.scene().sigMouseMoved.connect(self.mouse_moved)
        self.plotArea.getPlotItem().getAxis('bottom').enableAutoSIPrefix(False)
        self.plotArea.getPlotItem().getAxis('left').enableAutoSIPrefix(False)
        self.plotArea.getPlotItem().hideAxis('bottom')
        self.plotArea.getPlotItem().hideAxis('left')
        self.plotArea.setAspectLocked(True)

        self.image_item = pg.ImageItem()
        self.plotArea.addItem(self.image_item)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.gaps_list)
        self.splitter.addWidget(self.plotArea)

        self.vbox = QtWidgets.QVBoxLayout(self)
        self.vbox.addWidget(self.splitter)
        self.setCentralWidget(QtWidgets.QWidget(self))
        self.centralWidget().setLayout(self.vbox)
        self.showMaximized()

        self.rectangle_region = None

        self.logic = MainLogic()

    def open_avi(self, checked):
        pass

    def open_csv(self, checked):
        file_name, _ = QFileDialog.getOpenFileName(parent=self, caption="Открыть CSV файл", filter="CSV (*.csv)")
        if file_name:
            if self.logic.open_csv(file_name):
                self.refresh_gaps_list()

    def refresh_gaps_list(self):
        self.gaps_model.clear()
        for i, (index, row) in enumerate(self.logic.df_gaps.iterrows()):
            item = QtGui.QStandardItem(f"{row['kilometer']} км {row['meter']} м: зазор {row['gap']} мм")
            item.setEditable(False)
            self.gaps_model.appendRow(item)
            index = self.gaps_model.indexFromItem(item)
            self.gaps_model.setData(index, i, role=QtCore.Qt.UserRole)
        self.gaps_list.setModel(self.gaps_model)

    def on_select_element(self, index):
        num = index.data(QtCore.Qt.UserRole)
        image_file_name = self.logic.folder + "/" + self.logic.df_gaps["file_name"].values[num]
        img = image.imread(image_file_name)
        img = np.swapaxes(img, 0, 1)
        img = img[:, ::-1, :]
        self.image_item.setImage(img)
        # self.plotArea.setLimits(xMin=0, xMax=img.shape[0], yMin=0, yMax=img.shape[0])

        x1 = self.logic.df_gaps["x1"].values[num]
        x2 = self.logic.df_gaps["x2"].values[num]
        y1 = self.logic.df_gaps["y1"].values[num]
        y2 = self.logic.df_gaps["y2"].values[num]
        self.draw_regions(x1, x2, y1, y2)

    def draw_regions(self, x1, x2, y1, y2):
        color = "r"
        width = 3
        style = QtCore.Qt.PenStyle.SolidLine
        if self.rectangle_region is None:
            self.rectangle_region = self.plotArea.plot(x=[x1, x1, x2, x2, x1], y=[y1, y2, y2, y1, y1], symbol=None,
                                                       pen=pg.mkPen(color=color, width=width, style=style))
        else:
            self.rectangle_region.setData(x=[x1, x1, x2, x2, x1], y=[y1, y2, y2, y1, y1])

    # self.elements[el].setData(x=[distance0, distance0, distance1, distance1, distance0],
    #                           y=[height0, height1, height1, height0, height0],
    #                           pen=pg.mkPen(color=col, width=width, style=style))

    def mouse_clicked(self, evt):
        pnt = evt.scenePos()
        pnt = (pnt.x(), pnt.y())
        mouse_point = self.plotArea.getPlotItem().vb.mapSceneToView(evt.scenePos())
        x = mouse_point.x()
        y = mouse_point.y()
        btn = evt.button()
        print(x, y)

    def mouse_moved(self, evt):
        pass


def config_pyqtgraph():
    pg.setConfigOption("antialias", True)
    pg.setConfigOption("leftButtonPan", True)
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')


if __name__ == "__main__":
    config_pyqtgraph()
    from PyQt5.QtWidgets import QApplication
    QApplication.setAttribute(QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
