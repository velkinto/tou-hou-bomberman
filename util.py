import os
import time
import typing
import threading

from PyQt5 import QtGui, QtCore, QtMultimedia
from PyQt5.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

from gui import gui

class AudioPlayer:

    medias = {}
    players = {}

    @staticmethod
    def load(directive, *path):
        file = QtCore.QUrl.fromLocalFile(QtCore.QDir.current().absoluteFilePath(os.path.join('assets', 'audios', *path))) # 音频文件路径
        content = QtMultimedia.QMediaContent(file)
        AudioPlayer.medias[directive] = content

    @staticmethod
    def unload(directive):
        if directive in AudioPlayer.medias.keys():
            AudioPlayer.medias.pop(directive)

    @staticmethod
    def get(directive):
        if not directive in AudioPlayer.players.keys():
            AudioPlayer.players[directive] = AudioPlayer(directive)
        return AudioPlayer.players[directive]

    def __init__(self, directive) -> None:
        self.player = QtMultimedia.QMediaPlayer(gui)
        self.player.setMedia(AudioPlayer.medias[directive])
        self.player.setVolume(100.0)

    def play(self):
        self.player.play()

    def stop(self):
        self.player.stop()

class ImageGraphicsItem(QGraphicsItem):

    def __init__(self, imager) -> None:
        super().__init__()
        self.imager = imager
        gui.addGraphicsItem(self)

    def boundingRect(self) -> QtCore.QRectF:
        if hasattr(self.imager, 'boundingRect'):
            return self.imager.boundingRect()

    def paint(self, painter: QtGui.QPainter, option: QStyleOptionGraphicsItem, widget: typing.Optional[QWidget]) -> None:
        painter.drawImage(self.boundingRect(), self.imager.image)

class PaintGraphicsItem(QGraphicsItem):

    def __init__(self, painter) -> None:
        super().__init__()
        self.painter = painter
        gui.addGraphicsItem(self)

    def boundingRect(self) -> QtCore.QRectF:
        return self.painter.boundingRect()

    def paint(self, painter: QtGui.QPainter, option: QStyleOptionGraphicsItem, widget: typing.Optional[QWidget]) -> None:
        self.painter.paint(painter)

def loadImages(path):
    images = []
    dir, _, files = list(os.walk(path))[0]
    files.sort()
    for f in files:
        if f.endswith('.png'):
            images.append(QtGui.QImage(os.path.join(dir, f)))
    return images

def loadSprites(image, directives, n_columns):
    if not isinstance(image, QtGui.QImage):
        image = QtGui.QImage(image)
    n_rows = len(directives)
    imageDict = {}
    crop_width = image.width() / n_columns
    crop_height = image.height() / n_rows
    for i in range(n_rows):
        directive = directives[i]
        images = []
        for j in range(n_columns):
            img = image.copy(j * crop_width, i * crop_height, crop_width, crop_height)
            images.append(img)
        imageDict[directive] = images
    return imageDict
