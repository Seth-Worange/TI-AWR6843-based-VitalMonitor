import sys
import pyqtgraph as pg
from PyQt5 import QtWidgets
import numpy as np


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # 创建一个 PlotWidget 对象
        self.graphWidget = pg.PlotWidget()

        # 设置图表标题和颜色
        self.graphWidget.setBackground('w')
        self.graphWidget.setTitle("Title", color="b", size="30pt")

        # 添加网格
        styles = {"color": "#f00", "font-size": "20px"}
        self.graphWidget.setLabel("left", "Y Axis", **styles)
        self.graphWidget.setLabel("bottom", "X Axis", **styles)

        self.graphWidget.showGrid(x=True, y=True)

        # 设置数据
        x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        y = np.array([30, 32, 34, 32, 33, 31, 29, 32, 35, 45])

        # 在 PlotWidget 上绘制数据
        pen = pg.mkPen(color="#dcbeff")
        self.graphWidget.plot(x, y, pen=pen)

        # 设置主窗口的中心小部件为图表
        self.setCentralWidget(self.graphWidget)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
