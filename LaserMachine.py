import time
from math import sqrt

from PyQt6.QtCore import QTimer, QPoint, pyqtSignal, QObject, QSize, QPointF, Qt
from PyQt6.QtGui import QAction, QPainter, QStaticText, QKeyEvent, QMouseEvent
from PyQt6.QtWidgets import QWidget, QMainWindow, QLabel
from PyQt6.uic.properties import QtCore, QtWidgets
from PyQt5 import QtWidgets, Qt, QtCore
from MarkerState import MarkerState


class PushButtonRight(QtWidgets.QPushButton):
    right_click = QtCore.pyqtSignal()

    def __init__(self, string):
        super().__init__(string)

    def mousePressEvent(self, event):
        if event.button() == Qt.Qt.RightButton:
            self.right_click.emit()
            print('right click')

        QtWidgets.QPushButton.mousePressEvent(self, event)

class PropertyEvent(QObject):
    changed = pyqtSignal()

class LaserMachine():
    def __init__(self):
        self.__timer = QTimer()
        self.__timer.timeout.connect(self.__processOneThing)
        self.__laserState = MarkerState.HIDE
        self.__position = QPoint(0,0)
        self.__destination = QPoint(0,0)
        self.__isMoving = False
        self.__maxSpeed = 5
        self.__bounds = QSize(500, 500)
        self.laserStateChanged = PropertyEvent()
        self.positionChanged = PropertyEvent()
        self.destinationChanged = PropertyEvent()
        self.isMovingChanged = PropertyEvent()
        self.__nextMoveTime = 0
        self.__error = 0
        self.err = 0

        #self.rightsignal = PushButtonRight('hi')
        #self.rightsignal.right_click.connect(self.stateChange())

    def stateChange(self):
        state = self.getLaserState()
        if state == MarkerState.OFF or state == MarkerState.HIDE:
            self.__laserState = MarkerState.ON
        else:
            self.__laserState = MarkerState.OFF
        print(self.getLaserState())

    """
    def mousePressEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.MouseButton.RightButton:
            self.stateChange()
            print("clicked")
    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.MouseButton.RightButton:
            print("clicked")
    """



    def __setIsMoving(self, value):
        self.__isMoving = value
        if(self.__isMoving):
            self.__timer.start()
        else:
            self.__timer.stop()
        self.isMovingChanged.changed.emit()

    def keyPressEvent(self, event: QKeyEvent):
        self.__maxSpeed = int(event.text())

    def getLaserState(self) -> MarkerState:
        return self.__laserState

    def getPosition(self) -> QPoint:
        return self.__position

    def getDestination(self) -> QPoint:
        return self.__destination

    def getMaxSpeed(self) -> float:
        return self.__maxSpeed

    def getBounds(self) -> QSize:
        return self.__bounds

    def setDestination(self, x, y):
        self.__destination = QPoint(x, y)
        self.destinationChanged.changed.emit()
        self.__setIsMoving(True)

    def __setPosition(self, x, y):
        self.__position.setX(x)
        self.__position.setY(y)
        self.positionChanged.changed.emit()

    def __processOneThing(self):
        step_time = 1.0 / self.__maxSpeed
        self.__lastTimerTick = time.time()
        if self.__isMoving and self.__lastTimerTick > self.__nextMoveTime:
            self.step = False
            self.__doMove()
            self.__nextMoveTime = self.__lastTimerTick + step_time

    def __doMove(self):
        # err - ошибка. Тут используется формула перемещения y1 = (a/b)*x - y1
        # err(x,y) = (a/b)*dx - dy
        # err = 0
        # err += a/b
        # if (err > 0.5):
        #   y++
        #   err -=1
        # else x++
        # Чтобы избавиться от чисел с плавающей точкой домножаю на 2b
        # err = 0
        # err += 2a
        # .. и тд
        # таким образом ошибка не накапливается
        x0 = self.__position.x()
        y0 = self.__position.y()
        x1 = self.__destination.x()
        y1 = self.__destination.y()

        dx = int(x1-x0)
        dy = -int(y1-y0)
        print(dx)
        print(dy)
        self.err += 2*abs(dy)
        #print(self.err)

        if self.__position == self.__destination:
            self.__setIsMoving(False)

        else:


            if self.err >= dx:
                ystep = 1 if dy > 0 else -1
                y = y0 - ystep
                x = x0
                self.err -= 2*abs(dx)

            else:
                xstep = 1 if dx > 0 else -1
                x = x0 + xstep
                y = y0
            print(self.err)

            self.__setPosition(x,y)
            if self.__position == self.__destination:
                self.__setIsMoving(False)
                self.err =0
