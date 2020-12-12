import sys

import numpy as np
import pyqtgraph as pg
import qdarkstyle
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

        self.rail_combolist = QtWidgets.QComboBox()
        self.rail_combolist.addItems(["обе нити", "левая нить", "правая нить"])

        self.plot_area = self.create_plot_area(self)
        # self.plot_area2 = self.create_plot_area(self)

        self.image_item = pg.ImageItem()
        self.plot_area.addItem(self.image_item)
        # self.image_item2 = pg.ImageItem()
        # self.plot_area2.addItem(self.image_item2)

        self.vbox_data = QtWidgets.QVBoxLayout()
        self.vbox_data.addWidget(self.gaps_list)
        self.board_widget = QtWidgets.QWidget()
        self.board_widget.setLayout(self.vbox_data)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.board_widget)
        self.splitter.addWidget(self.plot_area)
        # self.splitter.addWidget(self.plot_area2)

        self.vbox = QtWidgets.QVBoxLayout(self)
        self.vbox.addWidget(self.splitter)
        self.setCentralWidget(QtWidgets.QWidget(self))
        self.centralWidget().setLayout(self.vbox)
        self.showMaximized()

        self.rectangle_region = None
        # self.rectangle_region2 = None

        self.logic = MainLogic()
        
    def create_plot_area(self, plot_area):
        plot_area = pg.PlotWidget()
        plot_area.setCursor(QtCore.Qt.CrossCursor)
        plot_area.setMenuEnabled(False)
        plot_area.scene().sigMouseClicked.connect(self.mouse_clicked)
        plot_area.scene().sigMouseMoved.connect(self.mouse_moved)
        plot_area.getPlotItem().getAxis('bottom').enableAutoSIPrefix(False)
        plot_area.getPlotItem().getAxis('left').enableAutoSIPrefix(False)
        plot_area.getPlotItem().hideAxis('bottom')
        plot_area.getPlotItem().hideAxis('left')
        plot_area.setAspectLocked(True)
        return plot_area
        
    def open_avi(self, checked):
        file_name, _ = QFileDialog.getOpenFileName(parent=self, caption="Открыть AVI файл", filter="AVI (*.avi)",
                                                   directory="data")
        if file_name:
            if self.logic.open_avi(file_name):
                self.refresh_gaps_list()

    def open_csv(self, checked):
        file_name, _ = QFileDialog.getOpenFileName(parent=self, caption="Открыть CSV файл", filter="CSV (*.csv)",
                                                   directory="data")
        if file_name:
            if self.logic.open_csv(file_name):
                self.refresh_gaps_list()

    def refresh_gaps_list(self):
        self.gaps_model.clear()
        for i, (index, row) in enumerate(self.logic.df_gaps.iterrows()):
            item = QtGui.QStandardItem(f"({row['rail']}) {row['kilometer']} км {row['meter']} м: зазор {row['gap']} мм")
            item.setEditable(False)
            self.gaps_model.appendRow(item)
            index = self.gaps_model.indexFromItem(item)
            self.gaps_model.setData(index, i, role=QtCore.Qt.UserRole)
        self.gaps_list.setModel(self.gaps_model)

    def on_select_element(self, index):
        num = index.data(QtCore.Qt.UserRole)

        self.draw_image(num, "file_name", self.image_item)
        # self.draw_image(num, "file_name", self.image_item2)

        x1 = self.logic.df_gaps["x1"].values[num]
        x2 = self.logic.df_gaps["x2"].values[num]
        y1 = self.logic.df_gaps["y1"].values[num]
        y2 = self.logic.df_gaps["y2"].values[num]
        self.draw_regions(self.plot_area, self.rectangle_region, x1, x2, y1, y2)
        # self.draw_regions(self.plot_area2, self.rectangle_region2, x1, x2, y1, y2)

    def draw_image(self, num, file_name_key, image_item):
        image_file_name = self.logic.folder + "/" + self.logic.df_gaps[file_name_key].values[num]
        img = image.imread(image_file_name)
        img = np.swapaxes(img, 0, 1)
        img = img[:, ::-1, :]
        image_item.setImage(img)
        # self.plot_area.setLimits(xMin=0, xMax=img.shape[0], yMin=0, yMax=img.shape[0])

    def draw_regions(self, plot_area, rectangle_region, x1, x2, y1, y2):
        color = "r"
        width = 3
        style = QtCore.Qt.PenStyle.SolidLine
        if rectangle_region is None:
            rectangle_region = plot_area.plot(x=[x1, x1, x2, x2, x1], y=[y1, y2, y2, y1, y1], symbol=None,
                                                        pen=pg.mkPen(color=color, width=width, style=style))
        else:
            rectangle_region.setData(x=[x1, x1, x2, x2, x1], y=[y1, y2, y2, y1, y1])

    # self.elements[el].setData(x=[distance0, distance0, distance1, distance1, distance0],
    #                           y=[height0, height1, height1, height0, height0],
    #                           pen=pg.mkPen(color=col, width=width, style=style))

    def mouse_clicked(self, evt):
        pnt = evt.scenePos()
        pnt = (pnt.x(), pnt.y())
        mouse_point = self.plot_area.getPlotItem().vb.mapSceneToView(evt.scenePos())
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
    # config_pyqtgraph()
    from PyQt5.QtWidgets import QApplication
    QApplication.setAttribute(QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    window = MainWindow()
    window.show()
    app.exec()
