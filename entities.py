import abc

from PyQt5 import QtCore
from PyQt5.QtGui import QPainter

from components import *

class Entity(metaclass=abc.ABCMeta):

    nextEntityId = 0

    entities = {}

    def __init__(self) -> None:
        self.id = Entity.nextEntityId
        Entity.nextEntityId += 1
        Entity.entities[self.id] = self

class AnimationEntity(Entity):

    @abc.abstractproperty

    @abc.abstractmethod
    def boundingRect(self):
        pass

    @property
    def image(self):
        pass

    @property
    def index(self):
        pass
    @index.setter
    @abc.abstractmethod
    def index(self, val):
        pass

    @property
    def active(self):
        pass
    @active.setter
    @abc.abstractmethod
    def active(self, val):
        pass

    @property
    def interval(self):
        pass

    @property
    def repeat(self):
        pass

class HomeBackground(Entity):

    def __init__(self) -> None:
        super().__init__()
        self.imgRenderCom = ImageRenderCom(self.id, 'assets/home.png')

class GameBackground(Entity):

    def __init__(self) -> None:
        super().__init__()
        self.imgRenderCom = ImageRenderCom(self.id, 'assets/template.png')

class GameBoard(Entity):

    def __init__(self) -> None:
        super().__init__()
        self.boardRenderCom = BoardRenderCom(self.id, 'assets/board.png')

class GamePlayer(Entity):

    def __init__(self) -> None:
        super().__init__()
        self.playerCom = PlayerCom(self.id)
        self.moveCom = MoveCom(self.id, False)
        self.sizeCom = SizeCom(self.id, 32, 48)
        self.positionCom = PositionCom(self.id, 259, 600, enableOut=False)
        self.velocityCom = VelocityCom(self.id, 8)
        self.fireCom = FireCom(self.id, 30, 10)
        self.collisionCom = RelativeBoxCom(self.id, self.positionCom, 11, 19, 10, 10)
        self.invincible = 0
        self.reviveTime = 240
        self.lowSpeed = False
        self.bombY = -600

    def die(self):
        self.positionCom.x = 259
        self.positionCom.y = 600
        self.invincible = 300

class GameHUD(Entity):

    def __init__(self) -> None:
        super().__init__()
        self.scoreCom = ScoreCom(self.id)
        self.heartCom = HeartCom(self.id, 3)
        self.starCom = StarCom(self.id, 4)
        self.cadanCom = CaDanCom(self.id)

class ButtonStart(Entity):

    def __init__(self) -> None:
        super().__init__()
        self.aniRenderCom = AnimationRenderCom(self.id, 'assets/buttons/start', QtCore.QRectF(700, 520, 201, 38))
        self.selectCom = SelectCom(self.id, True)

class ButtonExit(Entity):

    def __init__(self) -> None:
        super().__init__()
        self.aniRenderCom = AnimationRenderCom(self.id, 'assets/buttons/exit', QtCore.QRectF(700, 578, 220, 40))
        self.selectCom = SelectCom(self.id)


class Dan(Entity):

    def __init__(self, player, speed) -> None:
        super().__init__()
        # 提供渲染组件并且进行标记
        self.danCom = DanCom(self)
        # player 提供初始位置
        pos = player.positionCom
        self.positionCom = PositionCom(self.id, pos.x + 3, pos.y - 57, False)
        self.sizeCom = SizeCom(self.id, 28, 56)
        self.velocityCom = VelocityCom(self.id, speed)
        self.destoryed = False

    def destory(self):
        if self.destoryed:
            return
        Entity.entities.pop(self.id)
        DanCom.components.get('dan').remove(self.danCom)
        DanCom.components.get('position').remove(self.positionCom)
        DanCom.components.get('size').remove(self.sizeCom)
        DanCom.components.get('velocity').remove(self.velocityCom)
        self.destoryed = True

class GameDanmaku(Entity):

    def __init__(self) -> None:
        super().__init__()
        self._graphicsItem = PaintGraphicsItem(self)
        self.rect = QtCore.QRectF(50, 20, 550, 675)

        self.pen = QPen(QColor(201, 93, 99), 2)
        self.brush = QBrush(QColor(255, 255, 255), QtCore.Qt.BrushStyle(1))

    def boundingRect(self):
        return self.rect

    def paint(self, painter: QPainter):
        danmakuComs = Component.components.get('danmaku')
        if danmakuComs is None:
            return
        for danmakuCom in danmakuComs:
            danmaku = danmakuCom.danmaku
            pos = danmaku.positionCom.position
            size = danmaku.sizeCom
            painter.setPen(self.pen)
            painter.setBrush(self.brush)
            x = pos.x() - size.width / 2
            y = pos.y() - size.height / 2
            painter.drawEllipse(x, y, size.width, size.height)

class Enemy1(Entity):

    def __init__(self) -> None:
        super().__init__()
        # 进行标记
        self.enemyCom = EnemyCom(self)
        # 手动设置初始位置速度和加速度
        self.moveCom = MoveCom(self.id)
        self.velocityCom = VelocityCom(self.id, 5, 80)
        self.positionCom = PositionCom(self.id, -10, 50, True)
        # self.accelerationCom = AccelerationCom(self.id, 0.06, 0)
        self.sizeCom = SizeCom(self.id, 32, 64)
        self.healthCom = HealthCom(self.id, 5)
        # 初始化 shooterCom
        self.shooterCom = PlayerShooterCom(self, speed=6, interval=10, five=15)

    def destroy(self):
        Entity.entities.pop(self.id)

        Component.components.get('enemy').remove(self.enemyCom)
        Component.components.get('move').remove(self.moveCom)
        Component.components.get('velocity').remove(self.velocityCom)
        Component.components.get('position').remove(self.positionCom)
        # Component.components.get('acceleration').remove(self.accelerationCom)
        Component.components.get('size').remove(self.sizeCom)
        Component.components.get('shooter').remove(self.shooterCom)

class Enemy2(Entity):

    def __init__(self) -> None:
        super().__init__()
        # 进行标记
        self.enemyCom = EnemyCom(self)
        # 手动设置初始位置速度和加速度
        self.moveCom = MoveCom(self.id)
        self.velocityCom = VelocityCom(self.id, 5, 280)
        self.positionCom = PositionCom(self.id, 550, 50, True)
        # self.accelerationCom = AccelerationCom(self.id, 0.06, 0)
        self.sizeCom = SizeCom(self.id, 32, 64)
        self.healthCom = HealthCom(self.id, 5)
        # 初始化 shooterCom
        self.shooterCom = PlayerShooterCom(self, speed=6, interval=10, triple=15)

    def destroy(self):
        Entity.entities.pop(self.id)

        Component.components.get('enemy').remove(self.enemyCom)
        Component.components.get('move').remove(self.moveCom)
        Component.components.get('velocity').remove(self.velocityCom)
        Component.components.get('position').remove(self.positionCom)
        # Component.components.get('acceleration').remove(self.accelerationCom)
        Component.components.get('size').remove(self.sizeCom)
        Component.components.get('shooter').remove(self.shooterCom)

class Enemy3(Entity):

    def __init__(self) -> None:
        super().__init__()
        # 进行标记
        self.enemyCom = EnemyCom(self)
        # 手动设置初始位置速度和加速度
        self.moveCom = MoveCom(self.id)
        self.velocityCom = VelocityCom(self.id, 10, 0)
        self.positionCom = PositionCom(self.id, 267, -30, True)
        self.accelerationCom = AccelerationCom(self.id, 0.1, 90)
        self.sizeCom = SizeCom(self.id, 32, 64)
        self.healthCom = HealthCom(self.id, 100)
        # 初始化 shooterCom
        self.shooterCom = PlayerShooterCom(self, speed=12, interval=4, four=30)

    def destroy(self):
        Entity.entities.pop(self.id)

        Component.components.get('enemy').remove(self.enemyCom)
        Component.components.get('move').remove(self.moveCom)
        Component.components.get('velocity').remove(self.velocityCom)
        Component.components.get('position').remove(self.positionCom)
        Component.components.get('acceleration').remove(self.accelerationCom)
        Component.components.get('size').remove(self.sizeCom)
        Component.components.get('shooter').remove(self.shooterCom)

class Enemy4(Entity):

    def __init__(self, health=4) -> None:
        super().__init__()
        # 进行标记
        self.enemyCom = EnemyCom(self)
        # 手动设置初始位置速度和加速度
        self.moveCom = MoveCom(self.id)
        self.velocityCom = VelocityCom(self.id, 5, 90)
        self.positionCom = PositionCom(self.id, -15, 30, True)
        self.accelerationCom = AccelerationCom(self.id, 0.1, 0)
        self.sizeCom = SizeCom(self.id, 32, 64)
        self.healthCom = HealthCom(self.id, health)
        # 初始化 shooterCom
        self.shooterCom = PlayerShooterCom(self, speed=12, interval=4, four=30)

    def destroy(self):
        Entity.entities.pop(self.id)
        Component.components.get('enemy').remove(self.enemyCom)
        Component.components.get('move').remove(self.moveCom)
        Component.components.get('velocity').remove(self.velocityCom)
        Component.components.get('position').remove(self.positionCom)
        Component.components.get('acceleration').remove(self.accelerationCom)
        Component.components.get('size').remove(self.sizeCom)
        Component.components.get('shooter').remove(self.shooterCom)


class Enemy5(Entity):

    def __init__(self, health=4) -> None:
        super().__init__()
        # 进行标记
        self.enemyCom = EnemyCom(self)
        # 手动设置初始位置速度和加速度
        self.moveCom = MoveCom(self.id)
        self.velocityCom = VelocityCom(self.id, 5, 270)
        self.positionCom = PositionCom(self.id, 560, 30, True)
        self.accelerationCom = AccelerationCom(self.id, 0.1, 0)
        self.sizeCom = SizeCom(self.id, 32, 64)
        self.healthCom = HealthCom(self.id, health)
        # 初始化 shooterCom
        self.shooterCom = PlayerShooterCom(self, speed=12, interval=4, four=30)

    def destroy(self):
        Entity.entities.pop(self.id)

        Component.components.get('enemy').remove(self.enemyCom)
        Component.components.get('move').remove(self.moveCom)
        Component.components.get('velocity').remove(self.velocityCom)
        Component.components.get('position').remove(self.positionCom)
        Component.components.get('acceleration').remove(self.accelerationCom)
        Component.components.get('size').remove(self.sizeCom)
        Component.components.get('shooter').remove(self.shooterCom)

class Enemy6(Entity):

    def __init__(self) -> None:
        super().__init__()
        # 进行标记
        self.enemyCom = EnemyCom(self)
        # 手动设置初始位置速度和加速度
        self.moveCom = MoveCom(self.id)
        self.velocityCom = VelocityCom(self.id, 3, 0)
        self.positionCom = PositionCom(self.id, 550, -30, True)
        self.accelerationCom = AccelerationCom(self.id, 0.1, 270)
        self.sizeCom = SizeCom(self.id, 32, 64)
        self.healthCom = HealthCom(self.id, 4)
        # 初始化 shooterCom
        self.shooterCom = PlayerShooterCom(self, speed=12, interval=4)

    def destroy(self):
        Entity.entities.pop(self.id)

        Component.components.get('enemy').remove(self.enemyCom)
        Component.components.get('move').remove(self.moveCom)
        Component.components.get('velocity').remove(self.velocityCom)
        Component.components.get('position').remove(self.positionCom)
        Component.components.get('acceleration').remove(self.accelerationCom)
        Component.components.get('size').remove(self.sizeCom)
        Component.components.get('shooter').remove(self.shooterCom)


class Enemy7(Entity):

    def __init__(self) -> None:
        super().__init__()
        # 进行标记
        self.enemyCom = EnemyCom(self)
        # 手动设置初始位置速度和加速度
        self.moveCom = MoveCom(self.id)
        self.velocityCom = VelocityCom(self.id, 3, 80)
        self.positionCom = PositionCom(self.id, 0, 50, True)
        # self.accelerationCom = AccelerationCom(self.id, 0.1, 270)
        self.sizeCom = SizeCom(self.id, 32, 64)
        self.healthCom = HealthCom(self.id, 4)
        # 初始化 shooterCom
        self.shooterCom = RandomShooterCom(self, speed=5, interval=6)

    def destroy(self):
        Entity.entities.pop(self.id)

        Component.components.get('enemy').remove(self.enemyCom)
        Component.components.get('move').remove(self.moveCom)
        Component.components.get('velocity').remove(self.velocityCom)
        Component.components.get('position').remove(self.positionCom)
        # Component.components.get('acceleration').remove(self.accelerationCom)
        Component.components.get('size').remove(self.sizeCom)
        Component.components.get('shooter').remove(self.shooterCom)

class Enemy8(Entity):

    def __init__(self) -> None:
        super().__init__()
        # 进行标记
        self.enemyCom = EnemyCom(self)
        # 手动设置初始位置速度和加速度
        self.moveCom = MoveCom(self.id)
        self.velocityCom = VelocityCom(self.id, 3, 280)
        self.positionCom = PositionCom(self.id, 550, 50, True)
        # self.accelerationCom = AccelerationCom(self.id, 0.1, 270)
        self.sizeCom = SizeCom(self.id, 32, 64)
        self.healthCom = HealthCom(self.id, 4)
        # 初始化 shooterCom
        self.shooterCom = RandomShooterCom(self, speed=5, interval=6)

    def destroy(self):
        Entity.entities.pop(self.id)

        Component.components.get('enemy').remove(self.enemyCom)
        Component.components.get('move').remove(self.moveCom)
        Component.components.get('velocity').remove(self.velocityCom)
        Component.components.get('position').remove(self.positionCom)
        # Component.components.get('acceleration').remove(self.accelerationCom)
        Component.components.get('size').remove(self.sizeCom)
        Component.components.get('shooter').remove(self.shooterCom)

class Enemy9(Entity):

    def __init__(self) -> None:
        super().__init__()
        # 进行标记
        self.enemyCom = EnemyCom(self)
        # 手动设置初始位置速度和加速度
        self.moveCom = MoveCom(self.id)
        self.velocityCom = VelocityCom(self.id, 5, 0)
        self.positionCom = PositionCom(self.id, 267, 0, True)
        self.accelerationCom = AccelerationCom(self.id, 0.05, 180)
        self.sizeCom = SizeCom(self.id, 32, 64)
        self.healthCom = HealthCom(self.id, 100)
        # 初始化 shooterCom
        self.shooterCom = RandomShooterCom(self, speed=5, interval=1, double=180)

    def destroy(self):
        Entity.entities.pop(self.id)

        Component.components.get('enemy').remove(self.enemyCom)
        Component.components.get('move').remove(self.moveCom)
        Component.components.get('velocity').remove(self.velocityCom)
        Component.components.get('position').remove(self.positionCom)
        Component.components.get('acceleration').remove(self.accelerationCom)
        Component.components.get('size').remove(self.sizeCom)
        Component.components.get('shooter').remove(self.shooterCom)

class Enemy10(Entity):

    def __init__(self, offsetX) -> None:
        super().__init__()
        # 进行标记
        self.enemyCom = EnemyCom(self)
        # 手动设置初始位置速度和加速度
        self.moveCom = MoveCom(self.id)
        self.velocityCom = VelocityCom(self.id, 4, 0)
        self.positionCom = PositionCom(self.id, 267 + offsetX, 0, True)
        self.accelerationCom = AccelerationCom(self.id, 0.05, 180)
        self.sizeCom = SizeCom(self.id, 32, 64)
        self.healthCom = HealthCom(self.id, 100)
        # 初始化 shooterCom
        self.shooterCom = RandomShooterCom(self, speed=5, interval=1, double=180)

    def destroy(self):
        Entity.entities.pop(self.id)

        Component.components.get('enemy').remove(self.enemyCom)
        Component.components.get('move').remove(self.moveCom)
        Component.components.get('velocity').remove(self.velocityCom)
        Component.components.get('position').remove(self.positionCom)
        Component.components.get('acceleration').remove(self.accelerationCom)
        Component.components.get('size').remove(self.sizeCom)
        Component.components.get('shooter').remove(self.shooterCom)

class Enemy11(Entity):

    def __init__(self, offsetX) -> None:
        super().__init__()
        # 进行标记
        self.enemyCom = EnemyCom(self)
        # 手动设置初始位置速度和加速度
        self.moveCom = MoveCom(self.id)
        self.velocityCom = VelocityCom(self.id, 1, 0)
        self.positionCom = PositionCom(self.id, 0, 5, True)
        self.accelerationCom = AccelerationCom(self.id, 0.04, 90)
        self.sizeCom = SizeCom(self.id, 32, 64)
        self.healthCom = HealthCom(self.id, 100)
        # 初始化 shooterCom
        self.shooterCom = PlayerShooterCom(self, speed=10, interval=5, five=90)

    def destroy(self):
        Entity.entities.pop(self.id)

        Component.components.get('enemy').remove(self.enemyCom)
        Component.components.get('move').remove(self.moveCom)
        Component.components.get('velocity').remove(self.velocityCom)
        Component.components.get('position').remove(self.positionCom)
        Component.components.get('acceleration').remove(self.accelerationCom)
        Component.components.get('size').remove(self.sizeCom)
        Component.components.get('shooter').remove(self.shooterCom)

class Enemy12(Entity):

    def __init__(self, index) -> None:
        super().__init__()
        # 进行标记
        self.enemyCom = EnemyCom(self)
        # 手动设置初始位置速度和加速度
        self.moveCom = MoveCom(self.id)
        self.velocityCom = VelocityCom(self.id, 0.8, 0)
        self.positionCom = PositionCom(self.id, 20 + index * 50, 20, True)
        self.accelerationCom = AccelerationCom(self.id, 0.08, 45)
        self.sizeCom = SizeCom(self.id, 32, 64)
        self.healthCom = HealthCom(self.id, 3)
        # 初始化 shooterCom
        self.shooterCom = PlayerShooterCom(self, speed=10, interval=10, five=40)

    def destroy(self):
        Entity.entities.pop(self.id)

        Component.components.get('enemy').remove(self.enemyCom)
        Component.components.get('move').remove(self.moveCom)
        Component.components.get('velocity').remove(self.velocityCom)
        Component.components.get('position').remove(self.positionCom)
        Component.components.get('acceleration').remove(self.accelerationCom)
        Component.components.get('size').remove(self.sizeCom)
        Component.components.get('shooter').remove(self.shooterCom)

class Enemy13(Entity):

    def __init__(self, index) -> None:
        super().__init__()
        # 进行标记
        self.enemyCom = EnemyCom(self)
        # 手动设置初始位置速度和加速度
        self.moveCom = MoveCom(self.id)
        self.velocityCom = VelocityCom(self.id, 0.8, 0)
        self.positionCom = PositionCom(self.id, 520 +- index * 50, 20, True)
        self.accelerationCom = AccelerationCom(self.id, 0.08, 315)
        self.sizeCom = SizeCom(self.id, 32, 64)
        self.healthCom = HealthCom(self.id, 3)
        # 初始化 shooterCom
        self.shooterCom = PlayerShooterCom(self, speed=10, interval=10, five=20)

    def destroy(self):
        Entity.entities.pop(self.id)

        Component.components.get('enemy').remove(self.enemyCom)
        Component.components.get('move').remove(self.moveCom)
        Component.components.get('velocity').remove(self.velocityCom)
        Component.components.get('position').remove(self.positionCom)
        Component.components.get('acceleration').remove(self.accelerationCom)
        Component.components.get('size').remove(self.sizeCom)
        Component.components.get('shooter').remove(self.shooterCom)

class Enemy14(Entity):

    def __init__(self) -> None:
        super().__init__()
        # 进行标记
        self.enemyCom = EnemyCom(self)
        # 手动设置初始位置速度和加速度
        self.moveCom = MoveCom(self.id)
        self.velocityCom = VelocityCom(self.id, 0, 180)
        self.positionCom = PositionCom(self.id, 275, 300, True)
        # self.accelerationCom = AccelerationCom(self.id, 0.08, 315)
        self.sizeCom = SizeCom(self.id, 32, 64)
        self.healthCom = HealthCom(self.id, 100)
        # 初始化 shooterCom
        self.shooterCom = RotateShooterCom(self)

    def destroy(self):
        Entity.entities.pop(self.id)

        Component.components.get('enemy').remove(self.enemyCom)
        Component.components.get('move').remove(self.moveCom)
        Component.components.get('velocity').remove(self.velocityCom)
        Component.components.get('position').remove(self.positionCom)
        # Component.components.get('acceleration').remove(self.accelerationCom)
        Component.components.get('size').remove(self.sizeCom)
        Component.components.get('shooter').remove(self.shooterCom)

class Enemy15(Entity):

    def __init__(self) -> None:
        super().__init__()
        # 进行标记
        self.enemyCom = EnemyCom(self)
        self.image = QImage('assets/bm2.png')
        # 手动设置初始位置速度和加速度
        self.moveCom = MoveCom(self.id)
        self.velocityCom = VelocityCom(self.id, 0, 180)
        self.positionCom = PositionCom(self.id, 275, 120, True)
        # self.accelerationCom = AccelerationCom(self.id, 0.08, 315)
        self.sizeCom = SizeCom(self.id, 64, 64)
        self.healthCom = HealthCom(self.id, 600)
        # 初始化 shooterCom
        self.shooterCom = BoliShooterCom(self, 8, count=6, rotate1=1, rotate2=25)

    def destroy(self):
        Entity.entities.pop(self.id)

        Component.components.get('enemy').remove(self.enemyCom)
        Component.components.get('move').remove(self.moveCom)
        Component.components.get('velocity').remove(self.velocityCom)
        Component.components.get('position').remove(self.positionCom)
        # Component.components.get('acceleration').remove(self.accelerationCom)
        Component.components.get('size').remove(self.sizeCom)
        Component.components.get('shooter').remove(self.shooterCom)

class Danmaku(Entity):

    def __init__(self, x, y, speed, direction, size=15) -> None:
        super().__init__()
        # 进行标记
        self.speed = speed
        self.danmakuCom = DanmakuCom(self)
        self.moveCom = MoveCom(self.id)
        self.positionCom = PositionCom(self.id, x, y, True)
        self.sizeCom = SizeCom(self.id, size, size)
        self.velocityCom = VelocityCom(self.id, speed, direction)
        self.isCaed = False

    def destory(self):
        Entity.entities.pop(self.id)
        DanCom.components.get('danmaku').remove(self.danmakuCom)
        DanCom.components.get('move').remove(self.moveCom)
        DanCom.components.get('position').remove(self.positionCom)
        DanCom.components.get('size').remove(self.sizeCom)
        DanCom.components.get('velocity').remove(self.velocityCom)
