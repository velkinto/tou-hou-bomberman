import abc
import math

from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QMessageBox

from gui import gui
from util import *
from entities import *
from components import *

GROUND_X = 50
GROUND_Y = 20
GROUND_WIDTH = 550
GROUND_HEIGHT = 675

KEY_MAP = {
    Qt.Key_Left: 1,
    Qt.Key_Up: 2,
    Qt.Key_Right: 4,
    Qt.Key_Down: 8,
}
DIRECTION_MAP = {
    0: -1,
    1: 270,
    2: 180,
    3: 225,
    4: 90,
    5: -1,
    6: 135,
    7: 180,
    8: 0,
    9: 315,
    10: -1,
    11: 270,
    12: 45,
    13: 0,
    14: 90,
    15: -1,
}

class System(metaclass=abc.ABCMeta):

    def __init__(self, world) -> None:
        self.world = world

    @abc.abstractmethod
    def nextTick(self):
        pass

    @abc.abstractmethod
    def cancel(self):
        pass

class AnimationSys(System):

    def __init__(self, world) -> None:
        super().__init__(world)

    def nextTick(self):
        for ani in Component.components['ani-render']:
            if ani.active and ani.index + 1 < ani.length:
                ani.index += 1

    def cancel(self):
        pass

class KeyListener(metaclass=abc.ABCMeta):

    @property
    @abc.abstractmethod
    def listens(self):
        pass

    @abc.abstractmethod
    def dispatch(self, key, flag):
        pass


class PlayerMove(KeyListener):

    def __init__(self, player) -> None:
        super().__init__()
        self.player = player
        self.keys = []
        self.directionMap = {
            Qt.Key_Left: 270,
            Qt.Key_Up: 180,
            Qt.Key_Right: 90,
            Qt.Key_Down: 0,
        }

    @property
    def listens(self):
        return [Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right]

    def dispatch(self, key, flag):
        if flag:
            self.keys.append(key)
        else:
            self.keys.remove(key)
        """
        code = sum([ KEY_MAP[k] for k in self.keys ])
        direction = DIRECTION_MAP[code]
        if direction == -1:
            self.player.velocityCom.direction = 0
            self.player.moveCom.moving = False
        else:
            self.player.velocityCom.direction = direction
            self.player.moveCom.moving = True
        """
        if len(self.keys) == 0:
            self.player.velocityCom.direction = 0
            self.player.moveCom.moving = False
        else:
            if self.player.invincible > self.player.reviveTime:
                self.player.moveCom.moving = False
                return
            horizontal = None
            vertical = None
            direction = None
            for k in self.keys:
                if k == Qt.Key_Left or k == Qt.Key_Right:
                    horizontal = self.directionMap[k]
                elif k == Qt.Key_Up or k == Qt.Key_Down:
                    vertical = self.directionMap[k]
            if horizontal == None:
                direction = vertical
            elif vertical == None:
                direction = horizontal
            else:
                if horizontal == 270 and vertical == 0:
                    vertical = 360
                direction = (horizontal + vertical) / 2
            self.player.velocityCom.direction = direction
            self.player.moveCom.moving = True


class PlayerLowSpeed(KeyListener):

    def __init__(self, player) -> None:
        self.player = player

    @property
    def listens(self):
        return [ Qt.Key_Shift ]

    def dispatch(self, key, shift):
        if shift:
            self.player.velocityCom.calculate(0.5)
            self.player.lowSpeed = True
        else:
            self.player.velocityCom.calculate(1)
            self.player.lowSpeed = False

class PlayerFire(KeyListener):

    def __init__(self, player) -> None:
        self.player = player

    @property
    def listens(self):
        return [ Qt.Key_Z ]

    def dispatch(self, key, shift):
        if shift:
            self.player.fireCom.firing = True
        else:
            self.player.fireCom.firing = False

class GameEnd(KeyListener):

    def __init__(self, player, world) -> None:
        self.player = player
        self.world = world

    @property
    def listens(self):
        return [ Qt.Key_Q, Qt.Key_B, Qt.Key_R ]

    def dispatch(self, key, shift):
        if key == Qt.Key_Q:
            gui.exit()
        elif key == Qt.Key_B:
            self.world.gameStarter()
            self.world.start()
        elif key == Qt.Key_R:
            self.world.gameStart()

class Bomb(KeyListener):

    def __init__(self, player, world) -> None:
        self.player = player
        self.world = world
        self.star = Component.components.get('star')[0]
        self.score = Component.components.get('score')[0]
        self.player = Entity.entities.get(Component.components.get('player')[0].id)

    @property
    def listens(self):
        return [ Qt.Key_X ]

    def dispatch(self, key, shift):
        if shift == True:
            if self.star.value > 0 and not self.player.bombY > 550:
                self.player.bombY = GROUND_HEIGHT + GROUND_Y
                self.star.value -= 1
                danmakus = Component.components.get('danmaku')
                if danmakus is not None:
                    danmakus.clear()
                enemyComs = Component.components.get('enemy')
                removes = []
                if enemyComs is None:
                    return
                for enemyCom in enemyComs:
                    enemy = enemyCom.enemy
                    enemy.healthCom.health -= 30
                    if enemy.healthCom.dead():
                        self.score.value += 300
                        removes.append(enemy)
                enemy_remove = set(removes)
                for enemy in enemy_remove:
                    enemy.destroy()

class PlayerSys(System):

    def __init__(self, world) -> None:
        super().__init__(world)
        gui.subscribe(self)
        playerCom = Component.components['player'][0]
        self.player = Entity.entities.get(playerCom.id)
        self.listeners = []
        self.listeners.append(PlayerMove(self.player))
        self.listeners.append(PlayerLowSpeed(self.player))
        self.listeners.append(PlayerFire(self.player))
        self.listeners.append(GameEnd(self.player, world))
        self.listeners.append(Bomb(self.player, world))

    def cancel(self):
        gui.unSubscribe(self)

    def keyPressEvent(self, event):
        if not event.isAutoRepeat():
            self.dispatch(event.key(), True)

    def keyReleaseEvent(self, event):
        self.dispatch(event.key(), False)

    def dispatch(self, key, flag):
        for listener in self.listeners:
            if key in listener.listens:
                listener.dispatch(key, flag)

    def nextTick(self):
        # revive
        if self.player.invincible > 0:
            self.player.invincible -= 1

        # fire logic
        fireCom = self.player.fireCom
        if fireCom.counter > 0:
            fireCom.counter -= 1
        elif fireCom.firing:
            # create dan
            speed = fireCom.speed
            Dan(self.player, speed)


class BoardSys(System):

    def __init__(self, world) -> None:
        super().__init__(world)

    def nextTick(self):
        for board in Component.components['board-render']:
            if board.counter + 1 < board.length:
                board.counter += 1
            else:
                board.counter = 0

    def cancel(self):
        pass

class MusicSys(System):

    def __init__(self, world, directive) -> None:
        super().__init__(world)
        self.player = AudioPlayer.get(directive)
        self.player.play()

    def nextTick(self):
        pass

    def cancel(self):
        self.player.stop()

class SelectSys(System):

    def __init__(self, world) -> None:
        super().__init__(world)
        gui.subscribe(self)
        AudioPlayer.load('select', 'select.wav')
        self.selectedIndex = 0

    def cancel(self):
        gui.unSubscribe(self)
        AudioPlayer.unload('select')

    def keyPressEvent(self, event):
        AudioPlayer('select').play()
        length = len(Component.components['select-item'])
        key = event.key()
        if key == Qt.Key_Up:
            if self.selectedIndex > 0:
                self.selectedIndex -= 1
            else:
                self.selectedIndex = length - 1
        elif key == Qt.Key_Down:
            if self.selectedIndex < length - 1:
                self.selectedIndex += 1
            else:
                self.selectedIndex = 0
        elif key == Qt.Key_X:
            if self.selectedIndex != length - 1:
                self.selectedIndex = length - 1
            else:
                gui.exit()
        elif (key == Qt.Key_Z) or (key == Qt.Key_Return):
            if self.selectedIndex == 0:
                self.world.gameStart()
            elif self.selectedIndex == 1:
                gui.exit()

    def nextTick(self):
        coms = Component.components['select-item']
        for index in range(len(coms)):
            item = coms[index]
            if self.selectedIndex == index:
                item.selected = True
                if item.id in Entity.entities.keys():
                    entity = Entity.entities[item.id]
                    if hasattr(entity, 'aniRenderCom'):
                        entity.aniRenderCom.active = True
            else:
                item.selected = False
                if item.id in Entity.entities.keys():
                    entity = Entity.entities[item.id]
                    if hasattr(entity, 'aniRenderCom'):
                        entity.aniRenderCom.active = False

class AccelerationSys(System):

    def __init__(self, world) -> None:
        super().__init__(world)

    def cancel(self):
        pass

    def nextTick(self):
        accelerators = Component.components.get('acceleration')
        if accelerators is None:
            return
        for accelerator in accelerators:
            entity = Entity.entities.get(accelerator.id)
            velocity = entity.velocityCom
            # 编写使用加速度改变速度的逻辑
            velocityX = round(math.sin(math.radians(velocity.direction)), 2) * velocity.speed
            velocityY = round(math.cos(math.radians(velocity.direction)), 2) * velocity.speed
            accelerationX = round(math.sin(math.radians(accelerator.direction)), 2) * accelerator.acceleration
            accelerationY = round(math.cos(math.radians(accelerator.direction)), 2) * accelerator.acceleration
            x = velocityX + accelerationX
            y = velocityY + accelerationY
            speed = round((x ** 2 + y ** 2) ** 0.5, 2)
            if y == 0:
                direction = velocity.direction
            elif x == 0:
                direction = 0 if y > 0 else 180
            else:
                direction = round(math.atan(x / y) * 180 / math.pi, 2)
            velocity.speed = speed
            velocity.direction = direction

class MoveSys(System):

    def __init__(self, world) -> None:
        super().__init__(world)

    def cancel(self):
        pass

    def move(self, position, velocity, size):
        if velocity.speed == 0:
            return
        offsetX = round(math.sin(math.radians(velocity.direction)), 2) * velocity.speed
        offsetY = round(math.cos(math.radians(velocity.direction)), 2) * velocity.speed
        position.x += offsetX
        position.y += offsetY
        if not position.enableOut:
            if position.x < 0:
                position.x = 0
            elif position.x > GROUND_WIDTH - size.width:
                position.x = GROUND_WIDTH - size.width
            if position.y < 0:
                position.y = 0
            elif position.y > GROUND_HEIGHT - size.height:
                position.y = GROUND_HEIGHT - size.height
            

    def nextTick(self):
        movers = Component.components.get('move')
        if movers is None:
            return
        for mover in movers:
            if not mover.moving:
                continue
            entity = Entity.entities.get(mover.id)
            position = entity.positionCom
            velocity = entity.velocityCom
            size = entity.sizeCom
            self.move(position, velocity, size)
            if hasattr(entity, 'danmakuCom') and entity.speed * 0.8 < velocity.speed:
                velocity.speed *= 0.99

class PlayerCollisionSys(System):

    def __init__(self, world) -> None:
        super().__init__(world)
        self.player = Entity.entities.get(Component.components.get('player')[0].id)
        self.cadan = Component.components.get('cadan')[0]
        self.score = Component.components.get('score')[0]

    def nextTick(self):
        danmakuComs = Component.components.get('danmaku')
        if danmakuComs is None:
            return
        if self.player.invincible > 0:
            self.player.invincible -= 1
            return
        for danmakuCom in danmakuComs:
            danmaku = Entity.entities.get(danmakuCom.id)
            player = Entity.entities.get(Component.components.get('player')[0].id)
            playerPos = player.positionCom.position
            danmakuX = danmaku.positionCom.position.x() + danmaku.sizeCom.width / 2
            danmakuY = danmaku.positionCom.position.y() + danmaku.sizeCom.height / 2
            danmakuR = danmaku.sizeCom.width / 2
            playerX = playerPos.x() + 22
            playerY = playerPos.y() + 19
            playerR = 5
            distance = ((danmakuX - playerX) ** 2 + (danmakuY - playerY) ** 2) ** 0.5
            isCollided = distance < (danmakuR + playerR)
            if isCollided:
                AudioPlayer.get('zhongdan').play()
                self.player.die()
                heart = Component.components.get('heart')[0]
                star = Component.components.get('star')[0]
                heart.val -= 1
                star.value = 4
                if heart.val < 0:
                    print('你没命了')
                    self.world.running = False
            elif not danmaku.isCaed and distance < (danmakuR + playerR) + 40:
                self.cadan.value += 1
                danmaku.isCaed = True
                self.score.value += 1000

    def cancel(self):
        pass

class DanManageSys(System):

    def __init__(self, world) -> None:
        super().__init__(world)
        self.painter = PaintGraphicsItem(self)
        self.rect = QRectF(50, 20, 550, 675)

    def nextTick(self):
        pass

    def cancel(self):
        gui.removeGraphicsItem(self.painter)

    def boundingRect(self):
        return self.rect

    def moveDan(self, dan):
        pos = dan.positionCom
        velocity = dan.velocityCom
        pos.y -= velocity.speed

    def isDanOutside(self, dan):
        position = dan.positionCom
        size = dan.sizeCom
        isOut = False
        if position.x > GROUND_WIDTH:
            isOut = True
        elif position.y > GROUND_HEIGHT:
            isOut = True
        elif position.x < -size.width:
            isOut = True
        elif position.y < -size.height:
            isOut = True
        return isOut

    def paint(self, painter: QPainter):
        if Component.components.get('dan') == None:
            return
        removeDan = []
        danComs = Component.components.get('dan')
        for danCom in danComs:
            dan = Entity.entities.get(danCom.id)
            self.moveDan(dan)
            if self.isDanOutside(dan):
                removeDan.append(dan)
        for dan in removeDan:
            dan.destory()

class EnemyManageSys(System):

    def __init__(self, world, stage) -> None:
        super().__init__(world)
        gui.subscribe(self)

        self.time = 0
        self.stage = stage
        self.score = Component.components.get('score')[0]

    def isOut(self, position, size):
        isOut = False
        if position.x > GROUND_WIDTH + (size.width / 2):
            isOut = True
        elif position.y > GROUND_HEIGHT + (size.height / 2):
            isOut = True
        elif position.x < -(size.width / 2):
            isOut = True
        elif position.y < -(size.height / 2 ):
            isOut = True
        return isOut

    def nextTick(self):
        self.time += 1
        if (self.time >= 180 and self.time <= 300 and self.time % 20 == 0):
            Enemy1()
            Enemy2()
        elif self.time == 360:
            Enemy3()
        elif (self.time >= 400 and self.time < 700 and self.time % 20 == 0):
            Enemy4()
        elif (self.time >= 800 and self.time < 1100 and self.time % 20 == 0):
            Enemy5()
            if self.time == 840:
                Enemy6()
        elif (self.time >= 1200 and self.time < 1500 and self.time % 20 == 0):
            Enemy4(20)
        elif (self.time >= 1600 and self.time < 1900 and self.time % 20 == 0):
            Enemy5()
            if self.time % 30 == 0:
                Enemy6()
        elif self.time >= 2000 and self.time < 2810 and self.time % 30 == 0:
            Enemy7()
            Enemy8()
        elif self.time == 2870:
            Enemy9()
        elif self.time == 3050:
            Enemy10(100)
        elif self.time == 3220:
            Enemy10(-100)
        elif self.time == 3400:
            Enemy10(100)
            Enemy10(-100)
        elif self.time == 3700:
            for i in range(10):
                Enemy12(i)
        elif self.time == 3900:
            for i in range(10):
                Enemy13(i)
        elif self.time == 4100:
            for i in range(10):
                Enemy12(i)
        elif self.time == 4300:
            for i in range(10):
                Enemy13(i)
        elif self.time == 4500:
            Enemy15()
        else:
            pass
        ################################################
        enemyComs = Component.components.get('enemy')
        danComs = Component.components.get('dan')
        dans = None
        if danComs is not None:
            dans = [ Entity.entities.get(danCom.id) for danCom in danComs ]
        if enemyComs is None:
            return
        removes = []
        for enemyCom in enemyComs:
            enemy = enemyCom.enemy
            position = enemy.positionCom
            size = enemy.sizeCom
            if self.isOut(position, size):
                removes.append(enemy)
                continue
            # 检测Dan碰撞
            if dans is None:
                continue
            for dan in dans:
                danSize = dan.sizeCom
                # 左上角坐标
                danPosition = dan.positionCom
                enemySize = enemy.sizeCom
                enemyPosition = enemy.positionCom
                danRect = QRectF(danPosition.x + 14, danPosition.y, danSize.width, danSize.height)
                enemyRect = QRectF(enemyPosition.x, enemyPosition.y, enemySize.width, enemySize.height)
                xCo = (danRect.right() > enemyRect.left() and danRect.right() < enemyRect.right()) or (danRect.left() > enemyRect.left() and danRect.left() < enemyRect.right())
                yCo = (danRect.top() > enemyRect.top() and danRect.top() < enemyRect.bottom()) or (danRect.bottom() > enemyRect.top() and danRect.bottom() < enemyRect.bottom())
                co = xCo and yCo
                if co:
                    # scorexxx
                    self.score.value += 10
                    dan.destory()
                    enemy.healthCom.decrease()
                    if enemy.healthCom.dead():
                        self.score.value += 300
                        removes.append(enemy)
        enemy_remove = set(removes)
        for enemy in enemy_remove:
            enemy.destroy()

    def cancel(self):
        gui.unSubscribe(self)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_T:
            print(self.time)

class EnemyRenderSys(System):

    def __init__(self, world) -> None:
        super().__init__(world)
        self.painter = PaintGraphicsItem(self)
        self.rect = QRectF(50, 20, 550, 675)
        self.enemyImg = QImage('assets/bm.png')

    def nextTick(self):
        pass

    def cancel(self):
        gui.removeGraphicsItem(self.painter)

    def boundingRect(self):
        return self.rect

    def paint(self, painter: QPainter):
        if Component.components.get('enemy') == None:
            return
        enemyComs = Component.components.get('enemy')
        for enemyCom in enemyComs:
            enemy = Entity.entities.get(enemyCom.id)
            pos = enemy.positionCom.position
            size = enemy.sizeCom
            x = pos.x() - size.width / 2
            y = pos.y() - size.height / 2
            image = self.enemyImg
            if hasattr(enemy, 'image'):
                image = enemy.image
            painter.drawImage(QRectF(x, y, size.width, size.height), image)

class EnemyShootSys(System):

    def __init__(self, world) -> None:
        super().__init__(world)
        self.player = Entity.entities.get(Component.components.get('player')[0].id)

    def nextTick(self):
        enemyComs = Component.components.get('enemy')
        if enemyComs is None:
            return
        for enemyCom in enemyComs:
            enemy = enemyCom.enemy
            shooter = enemy.shooterCom
            if shooter.cooldown > 0:
                shooter.cooldown -= 1
                continue
            pos = enemy.positionCom
            shooter.cooldown = shooter.interval
            directions = shooter.direction(self.player)
            size = 15
            if hasattr(shooter, 'size'):
                size = shooter.size
            for direction in directions:
                Danmaku(pos.x, pos.y, shooter.speed, direction, size)

    def cancel(self):
        pass

class DanmakuManageSys(System):

    def __init__(self, world) -> None:
        super().__init__(world)

    def nextTick(self):
        danmakuComs = Component.components.get('danmaku')
        if danmakuComs is None:
            return
        for danmakuCom in danmakuComs:
            danmaku = danmakuCom.danmaku
            size = danmaku.sizeCom
            isOut = self.isOut(danmaku.positionCom, size)
            if isOut:
                danmaku.destory()

    def isOut(self, position, size):
        isOut = False
        if position.x > GROUND_WIDTH + (size.width / 2):
            isOut = True
        elif position.y > GROUND_HEIGHT + (size.height / 2):
            isOut = True
        elif position.x < -(size.width / 2):
            isOut = True
        elif position.y < -(size.height / 2 ):
            isOut = True
        return isOut

    def cancel(self):
        pass

class PlayerRenderSys(System):

    def __init__(self, world) -> None:
        super().__init__(world)
        self._frames = 8
        self._interval = 4
        self.painter = PaintGraphicsItem(self)
        self._images = loadSprites('assets/reimu_sprite.png', ['default', 'left', 'right'], self._frames)
        self._width = self._images['default'][0].width()
        self._height = self._images['default'][0].height()
        self._ticker = -1
        self._maxTick = self._interval * self._frames

        self._directive = 'default'
        self.player = Entity.entities.get(Component.components.get('player')[0].id)

        self.pen = QPen(QColor(201, 93, 99), 2)
        self.brush = QBrush(QColor(255, 255, 255), QtCore.Qt.BrushStyle(1))

        self.position = QtCore.QPointF(0, 0)
        self.lowSpeed = False
        self.danImage = QImage('assets/dan.png')
        self.imageBomb = QImage('assets/Bomb_f01.png')

    def nextTick(self):
        if self._ticker + 1 >= self._maxTick:
            if self.directive == 'default':
                self._ticker = 0
            else:
                pass
        else:
            self._ticker += 1

    def cancel(self):
        gui.removeGraphicsItem(self.painter)

    @property
    def directive(self):
        return self._directive

    @directive.setter
    def directive(self, val):
        if self._directive != val:
            self._ticker = -1
            self._directive = val

    @property
    def image(self) -> None:
        return self._images[self.directive][self.index]

    @property
    def index(self) -> None:
        return math.floor(self._ticker / self._interval)

    def paint(self, painter: QtGui.QPainter):
        rect = self.boundingRect()
        self.position = self.player.positionCom.position
        self.directive = self.player.velocityCom.horizontalDirection
        
        if self.player.invincible > 0 and self.player.invincible % 3 == 0:
            return

        if self.player.bombY >= -550:
            self.player.bombY -= 20
            painter.drawImage(QRectF(50, self.player.bombY, 550, 550), self.imageBomb)

        if self.player.invincible > self.player.reviveTime:
            # 来个从下到上的位移
            gap = self.player.invincible - self.player.reviveTime
            painter.drawImage(rect.left(), rect.top() + gap, self.image)
        else:
            painter.drawImage(rect, self.image)
        if self.player.lowSpeed:
            painter.setPen(self.pen)
            painter.setBrush(self.brush)
            x = self.boundingRect().left() + 11
            y = self.boundingRect().top() + 19
            width = 10
            height = 10
            painter.drawEllipse(x, y, width, height)
        danComs = Component.components.get('dan')
        if danComs is not None:
            for index in range(len(danComs) - 1, -1, -1):
                danCom = danComs[index]
                dan = danCom.dan
                position = dan.positionCom.position
                painter.drawImage(position, self.danImage)

    def boundingRect(self):
        return QtCore.QRectF(self.position.x(), self.position.y(), self._width, self._height)
