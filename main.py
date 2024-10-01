import sys
from PyQt6.QtCore import QSize, QRectF, QEvent, Qt, QPoint
from PyQt6.QtGui import QImage, QColor, QPainter
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton)
from PyQt6 import uic

from LaserMachine import LaserMachine
from QZoomStageView import QZoomStageView

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.image = QImage()
        self.userIsResizing = False
        self.resize(800, 500)
        self.init_image(self.size())
        self.stageView = QZoomStageView()
        self.setWindowTitle("Virtual Laser")
        self.setCentralWidget(self.stageView)
        self.installEventFilter(self)
        self.__connectedMachine: LaserMachine = None
        self.stageView.signals.mouseStageClicked.connect(self.mouse_stage_clicked)
        self.UiComponents()

    def UiComponents(self):

        # creating a push button
        button = QPushButton("ON/OFF", self)

        # setting geometry of button
        button.setGeometry(200, 150, 100, 40)

        # adding action to a button
        button.clicked.connect(self.clickme)

    def clickme(self):
        self.__connectedMachine.stateChange()
        print("pressed")

    def mouse_stage_clicked(self, wpos: QPoint):
        self.__connectedMachine.setDestination(wpos.x(), -wpos.y())

    def connectMachine(self, machine : LaserMachine):
        if self.__connectedMachine is not None:
            self.__connectedMachine.positionChanged.changed.disconnected(self.machine_position_changed)
        self.__connectedMachine = machine
        self.__connectedMachine.positionChanged.changed.connect(self.machine_position_changed)
        self.stageView.setStageLimits(machine.getBounds())

    def machine_position_changed(self):
        self.stageView.setCurrentPosition(self.__connectedMachine.getPosition())

    def eventFilter(self, object, event) -> bool:
        if event.type() == QEvent.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton and self.userIsResizing:
            self.complete_resize()
        elif event.type() == QEvent.Type.NonClientAreaMouseButtonRelease and self.userIsResizing:
            self.complete_resize()
        return super().eventFilter(object, event)

    def resizeEvent(self, e) -> None:
        self.userIsResizing = True


    def complete_resize(self):
        self.userIsResizing = False
        self.init_image(self.size())
        self.update()

    def init_image(self, size: QSize):
        self.image = QImage(size.width(), size.height(), QImage.Format.Format_ARGB32)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    machine = LaserMachine()
    window.connectMachine(machine)
    machine.setDestination(0, 0)
    sys.exit(app.exec())

