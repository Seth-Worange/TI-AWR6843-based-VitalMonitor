# -*- coding = utf-8 -*-
# @Time: 2024-07-18 10:12
# @Author: Orange Wang
# @File: init.py
# @Software: PyCharm
import sys
import ui_file.widget as widget
from PyQt5.QtWidgets import QApplication, QWidget
from openpose.libSVM import LibSVM

if __name__ == '__main__':                                                                                                                                                                                                                       
    # 实例化，传参
    app = QApplication(sys.argv)
    # 创建对象
    mainWidget = QWidget()
    # 创建ui，引用文件中的Ui_MainWindow类
    ui = widget.Ui_Form()
    # 调用Ui_MainWindow类的setupUi，创建初始组件
    ui.setupUi(mainWidget)


    # 串口启动
    ui.setup_serialPort()

    # 相机启动
    ui.setup_camera_comboBox()

    # 创建窗口
    mainWidget.show()

    # 进入程序的主循环，并通过exit函数确保主循环安全结束(该释放资源的一定要释放)
    sys.exit(app.exec_())
