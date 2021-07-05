from util import *
import math
import random
from PyQt5 import QtCore
from PyQt5.QtGui import QBrush, QColor, QImage, QPainter, QPen

GROUND_RECT = QtCore.QRectF(50, 20, 550, 675)

class Component:

    components = {}

    def __init__(self, cls, id) -> None:
        if cls not in Component.components.keys():
            Component.components[cls] = []
        Component.components[cls].append(self)
        self.cls = cls
        self.id = id

class SelectCom(Component):

    def __init__(self, id, selected=False) -> None:
        super().__init__('select-item', id)
        self.selected = selected

class PositionCom(Component):

    def __init__(self, id, x=0, y=0, enableOut=True) -> None:
        super().__init__('position', id)
        self._x = x
        self._y = y
        self.enableOut = enableOut

    @property
    def x(self):
        return self._x
    @x.setter
    def x(self, val):
        self._x = val
    @property
    def y(self):
        return self._y
    @y.setter
    def y(self, val):
        self._y = val
    @property
    def position(self):
        return QtCore.QPointF(self._x + 50, self._y + 20)

class RelativeBoxCom(Component):

    def __init__(self, id, positionCom, offsetX, offsetY, width, height) -> None:
        super().__init__('relative-box', id)
        self.posCom = positionCom
        self.offsetX = offsetX
        self.offsetY = offsetY
        self.width = width
        self.height = height

    @property
    def x(self):
        return self.posCom.position.x() + self.offsetX
    @x.setter
    def x(self, val):
        pass
    @property
    def y(self):
        return self.posCom.position.y() + self.offsetY
    @y.setter
    def y(self, val):
        pass
    @property
    def position(self):
        return QtCore.QPointF(self.x + 50, self.y + 20)
    @property
    def rect(self):
        return QtCore.QRectF(self.x + 50, self.y + 20, self.width, self.height)

class RelativePositionCom(PositionCom):

    def __init__(self, id, player, offsetX, offsetY) -> None:
        super().__init__('position', id)
        self.player = player
        self.posCom = player.positionCom
        self.sizeCom = player.sizeCom
        self.offsetX = offsetX
        self.offsetY = offsetY

    @property
    def x(self):
        return self.posCom.position.x() + self.offsetX
    @x.setter
    def x(self, val):
        pass
    @property
    def y(self):
        return self.posCom.position.y() + self.offsetY
    @y.setter
    def y(self, val):
        pass
    @property
    def position(self):
        return QtCore.QPointF(self.x + 50, self.y + 20)

class AccelerationCom(Component):

    def __init__(self, id, acceleration, direction) -> None:
        super().__init__('acceleration', id)
        self.acceleration = acceleration
        self.direction = direction

class VelocityCom(Component):

    def __init__(self, id, defaultSpeed, direction=0) -> None:
        super().__init__('velocity', id)
        self.defaultSpeed = defaultSpeed
        self.speed = defaultSpeed
        self.direction = direction

    @property
    def horizontalDirection(self):
        if self.direction > 0 and self.direction < 180:
            return 'right'
        elif self.direction > 180 and self.direction < 360:
            return 'left'
        else:
            return 'default'

    def calculate(self, rate):
        self.speed = self.defaultSpeed * rate

class MoveCom(Component):

    def __init__(self, id, moving=True) -> None:
        super().__init__('move', id)
        self.moving = moving

class SizeCom(Component):

    def __init__(self, id, width, height) -> None:
        super().__init__('size', id)
        self.width = width
        self.height = height

class PlayerCom(Component):

    def __init__(self, id) -> None:
        super().__init__('player', id)


class ImageRenderCom(Component):

    def __init__(self, id, imagePath, rect=QtCore.QRectF(0, 0, 960, 720)) -> None:
        super().__init__('img-render', id)
        self._image = QImage(imagePath)
        self._graphicsItem = ImageGraphicsItem(self)
        self._rect = rect

    def boundingRect(self):
        return self._rect

    @property
    def image(self):
        return self._image

class BoardRenderCom(Component):

    def __init__(self, id, imagePath) -> None:
        super().__init__('board-render', id)
        self._image = QImage(imagePath)
        self._graphicsItem = PaintGraphicsItem(self)
        self._rect = QtCore.QRectF(50, 20, 550, 675)
        self.counter = 0
        self.length = 675

    def boundingRect(self):
        return self._rect

    def paint(self, painter: QtGui.QPainter):
        upperPoint = QtCore.QPointF(50, 20 + self.counter - 675)
        lowerPoint = QtCore.QPointF(50, 20 + self.counter)
        painter.drawImage(upperPoint, self._image)
        painter.drawImage(lowerPoint, self._image)
        # painter.drawImage(self._rect.topLeft(), self._image)

class AnimationRenderCom(Component):

    def __init__(self, id, imagePath, rect) -> None:
        super().__init__('ani-render', id)
        self._index = 0
        self._interval = 3
        self._repeat = 'forward'
        self._images = loadImages(imagePath)
        self._active = False
        self._graphicsItem = ImageGraphicsItem(self)
        self._rect = rect

    def boundingRect(self):
        return self._rect

    @property
    def image(self):
        return self._images[self._index]

    @property
    def length(self):
        return len(self._images)

    @property
    def index(self):
        return self._index
    @index.setter
    def index(self, val):
        self._index = val

    @property
    def active(self):
        return self._active
    @active.setter
    def active(self, val):
        self._active = val
        if val == False:
            self._index = 0

    @property
    def interval(self):
        return self._interval

    @property
    def repeat(self):
        return self._repeat

class HeartCom(Component):

    def __init__(self, id, val) -> None:
        super().__init__('heart', id)
        self._images = loadImages('assets/hearts')
        self._graphicsItem = ImageGraphicsItem(self)
        self._rect = QtCore.QRectF(785, 245, 136, 22)
        self.val = val

    @property
    def index(self):
        if self.val >= 0:
            return self.val
        else:
            return 0

    def boundingRect(self):
        return self._rect

    @property
    def image(self):
        return self._images[self.index]

class StarCom(Component):

    def __init__(self, id, val) -> None:
        super().__init__('star', id)
        self._images = loadImages('assets/stars')
        self._graphicsItem = ImageGraphicsItem(self)
        self._rect = QtCore.QRectF(785, 310, 136, 22)
        self.value = val

    @property
    def index(self):
        if self.value < 0:
            return 0
        return self.value

    def boundingRect(self):
        return self._rect

    @property
    def image(self):
        return self._images[self.index]

class ScoreCom(Component):

    def __init__(self, id) -> None:
        super().__init__('score', id)
        self.value = 0
        self._graphicsItem = PaintGraphicsItem(self)
        self.images = {
            '0': QImage('assets/numbers/0.png'),
            '1': QImage('assets/numbers/1.png'),
            '2': QImage('assets/numbers/2.png'),
            '3': QImage('assets/numbers/3.png'),
            '4': QImage('assets/numbers/4.png'),
            '5': QImage('assets/numbers/5.png'),
            '6': QImage('assets/numbers/6.png'),
            '7': QImage('assets/numbers/7.png'),
            '8': QImage('assets/numbers/8.png'),
            '9': QImage('assets/numbers/9.png'),
            '_': QImage('assets/numbers/_.png'),
        }

    def boundingRect(self):
        return QtCore.QRectF(720, 170, 168, 29)

    def paint(self, painter: QPainter):
        score = self.value
        scoreString = str(score).zfill(10)
        xNow = 904
        for i in range(9, -1, -1):
            # integer at i
            integer = scoreString[i]
            painter.drawImage(xNow, 170, self.images[integer])
            if (i + 2) % 3 == 0:
                xNow -= 12
                painter.drawImage(xNow, 170, self.images['_'])
            xNow -= 14


class CaDanCom(Component):

    def __init__(self, id) -> None:
        super().__init__('cadan', id)
        self.value = 0
        self._graphicsItem = PaintGraphicsItem(self)
        self.images = {
            '0': QImage('assets/numbers/0.png'),
            '1': QImage('assets/numbers/1.png'),
            '2': QImage('assets/numbers/2.png'),
            '3': QImage('assets/numbers/3.png'),
            '4': QImage('assets/numbers/4.png'),
            '5': QImage('assets/numbers/5.png'),
            '6': QImage('assets/numbers/6.png'),
            '7': QImage('assets/numbers/7.png'),
            '8': QImage('assets/numbers/8.png'),
            '9': QImage('assets/numbers/9.png'),
            '_': QImage('assets/numbers/_.png'),
        }

    def boundingRect(self):
        return QtCore.QRectF(761, 373, 160, 29)

    def paint(self, painter: QPainter):
        scoreString = str(self.value).zfill(7)
        xNow = 904
        for i in range(6, -1, -1):
            # integer at i
            integer = scoreString[i]
            painter.drawImage(xNow, 373, self.images[integer])
            if (i + 2) % 3 == 0:
                xNow -= 12
                painter.drawImage(xNow, 373, self.images['_'])
            xNow -= 14

class FireCom(Component):

    def __init__(self, id, speed, interval) -> None:
        super().__init__('fire', id)
        self.counter = 0
        self.firing = False
        self.speed = speed
        self.interval = interval

class DanCom(Component):

    def __init__(self, dan) -> None:
        super().__init__('dan', dan.id)
        self.dan = dan

class DanmakuCom(Component):

    def __init__(self, danmaku) -> None:
        super().__init__('danmaku', danmaku.id)
        self.danmaku = danmaku

class EnemyCom(Component):

    def __init__(self, enemy) -> None:
        super().__init__('enemy', enemy.id)
        self.enemy = enemy

class DirectionShooterCom(Component):

    def __init__(self, enemy, direction=0, speed=10, interval=10, triple=-1, five=-1, double=-1, four=-1) -> None:
        super().__init__('shooter', enemy.id)
        self.speed = speed
        self.interval = interval
        self.cooldown = 0
        self.posCom = enemy.positionCom
        self.tripleDegree = triple
        self.five = five
        self.double = double
        self.four = four
        self._direction = direction

    def direction(self, player):
        direction = self._direction
        if self.tripleDegree != -1:
            return [ direction - self.tripleDegree, direction, direction + self.tripleDegree ]
        elif self.five != -1:
            return [ direction - self.five * 2, direction - self.five, direction, direction + self.five, direction + self.five * 2 ]
        elif self.double != -1:
            return [ direction - self.double / 2, direction + self.double / 2 ]
        elif self.four != -1:
            return [ direction - self.four * 3 / 2, direction - self.four / 2, direction + self.four / 2, direction + self.four * 3 / 2 ]
        else:
            return [ direction ]


class RandomShooterCom(Component):

    def __init__(self, enemy, speed=10, interval=10, triple=-1, five=-1, double=-1, four=-1) -> None:
        super().__init__('shooter', enemy.id)
        self.speed = speed
        self.interval = interval
        self.cooldown = 0
        self.posCom = enemy.positionCom
        self.tripleDegree = triple
        self.five = five
        self.double = double
        self.four = four

    def direction(self, player):
        direction = random.randrange(0, 360)
        if self.tripleDegree != -1:
            return [ direction - self.tripleDegree, direction, direction + self.tripleDegree ]
        elif self.five != -1:
            return [ direction - self.five * 2, direction - self.five, direction, direction + self.five, direction + self.five * 2 ]
        elif self.double != -1:
            return [ direction - self.double / 2, direction + self.double / 2 ]
        elif self.four != -1:
            return [ direction - self.four * 3 / 2, direction - self.four / 2, direction + self.four / 2, direction + self.four * 3 / 2 ]
        else:
            return [ direction ]


class PlayerShooterCom(Component):

    def __init__(self, enemy, speed=10, interval=10, triple=-1, five=-1, double=-1, four=-1) -> None:
        super().__init__('shooter', enemy.id)
        self.speed = speed
        self.interval = interval
        self.cooldown = 0
        self.posCom = enemy.positionCom
        self.tripleDegree = triple
        self.five = five
        self.double = double
        self.four = four

    def direction(self, player):
        pos = self.posCom.position
        x = pos.x()
        y = pos.y()
        pX = player.positionCom.position.x() + 16
        pY = player.positionCom.position.y() + 24
        dX = pX - x
        dY = pY - y
        direction = round(math.atan(dX / dY) * 180 / math.pi, 2)
        if self.tripleDegree != -1:
            return [ direction - self.tripleDegree, direction, direction + self.tripleDegree ]
        elif self.five != -1:
            return [ direction - self.five * 2, direction - self.five, direction, direction + self.five, direction + self.five * 2 ]
        elif self.double != -1:
            return [ direction - self.double / 2, direction + self.double / 2 ]
        elif self.four != -1:
            return [ direction - self.four * 3 / 2, direction - self.four / 2, direction + self.four / 2, direction + self.four * 3 / 2 ]
        else:
            return [ direction ]

class RotateShooterCom(Component):

    def __init__(self, enemy, speed=5, interval=5, count=6) -> None:
        super().__init__('shooter', enemy.id)
        self.speed = speed
        self.interval = interval
        self.cooldown = 0
        self.posCom = enemy.positionCom
        self.count = count
        self.currentDirection = 0
        self.size = 10

    def direction(self, player):
        average = 360 / self.count
        directions = [ self.currentDirection - i * average for i in range(self.count) ]
        self.currentDirection += 3
        return directions

class BoliShooterCom(Component):

    def __init__(self, enemy, speed=6, interval=2, count=8, rotate1=2, rotate2=10) -> None:
        super().__init__('shooter', enemy.id)
        self.speed = speed
        self.interval = interval
        self.cooldown = 0
        self.posCom = enemy.positionCom
        self.count = count
        self.currentDirection = 0
        self.size = 10
        self.rotate1 = rotate1
        self.rotate2 = rotate2
        self.functionX = 0

    def direction(self, player):
        average = 360 / self.count
        self.functionX += self.rotate1
        directions = [ self.currentDirection - i * average for i in range(self.count) ]
        self.currentDirection += self.rotate2 * math.sin(math.radians(self.functionX))
        return directions


class HealthCom(Component):

    def __init__(self, id, health) -> None:
        super().__init__('health', id)
        self.id = id
        self.health = health

    def decrease(self):
        if self.health > 0:
            self.health -= 1

    def dead(self):
        return self.health <= 0
