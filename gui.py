from PyQt5 import QtCore, QtGui, QtMultimedia
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView


"""
负责 GUI 的显示

提供：
1. 控制窗口显示 API
2. 提供键盘事件的订阅
3. 提供物品绘制隐藏的接口
"""

class GameScene(QGraphicsScene):

    def __init__(self, gui):
        super().__init__(0, 0, 960, 720)
        self.gui = gui

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        self.gui.triggerKeyPressEvent(event)

    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        self.gui.triggerKeyReleaseEvent(event)


class Gui(QApplication):

    instance = None

    def __init__(self) -> None:
        super().__init__([])
        self.scene = GameScene(self)
        self.view = QGraphicsView()
        self.view.setScene(self.scene)
        self.subscriptors = []
        self.view.setFixedSize(960, 720)
        self.view.setWindowTitle('东方炸弹人 ～ Touhou Bomberman')
        self._exit = None

    def start(self, exit) -> None:
        self.view.show()
        self._exit = exit
        self.exec()
        self._exit()

    def addGraphicsItem(self, item) -> None:
        self.scene.addItem(item)

    def removeGraphicsItem(self, item) -> None:
        self.scene.removeItem(item)

    def update(self) -> None:
        self.scene.update()

    def subscribe(self, subscriptor) -> None:
        self.subscriptors.append(subscriptor)

    def unSubscribe(self, subscriptor) -> None:
        try:
            self.subscriptors.remove(subscriptor)
        except:
            pass

    def triggerKeyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        for sub in self.subscriptors:
            if hasattr(sub, 'keyPressEvent'):
                sub.keyPressEvent(event)

    def triggerKeyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        for sub in self.subscriptors:
            if hasattr(sub, 'keyReleaseEvent'):
                sub.keyReleaseEvent(event)

    def exit(self):
        self.closeAllWindows()
        self._exit()

gui = Gui()
