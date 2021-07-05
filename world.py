import time
import timeit
import threading
from typing import List

from gui import gui
from util import AudioPlayer
from systems import *
from entities import *

# constants
HZ = 60
INTERVAL = 1 / HZ

# typings
SystemList = List[System]

class SystemManager:

    def __init__(self, world) -> None:
        self.systems : SystemList = []
        self.world = world

    def cancelSystems(self):
        AudioPlayer.unload('zhongdan')
        for system in self.systems:
            system.cancel()

    def nextTick(self):
        for system in self.systems:
            system.nextTick()

    def registerStarterSystems(self):
        self.systems.append(AnimationSys(world))
        self.systems.append(SelectSys(world))
        self.systems.append(MusicSys(world, 'starter'))

    def registerStageSystems(self, stage):
        AudioPlayer.load('zhongdan', 'select.wav')
        AudioPlayer.get('zhongdan')
        if stage == 0:
            music = 'stage-1'
        self.systems.append(MusicSys(world, music))
        self.systems.append(BoardSys(world))
        self.systems.append(PlayerSys(world))
        self.systems.append(AccelerationSys(world))
        self.systems.append(MoveSys(world))

        self.systems.append(PlayerRenderSys(world))
        self.systems.append(EnemyRenderSys(world))
        self.systems.append(DanManageSys(world))
        self.systems.append(DanmakuManageSys(world))
        self.systems.append(EnemyManageSys(world, stage))

        self.systems.append(EnemyShootSys(world))
        self.systems.append(PlayerCollisionSys(world))

class EntityManager:

    def __init__(self, world) -> None:
        self.entites = {}
        self.world = world

    def cancelEntities(self):
        for entity in Entity.entities.values():
            components = vars(entity).values()
            for component in components:
                if hasattr(component, '_graphicsItem'):
                    gui.removeGraphicsItem(component._graphicsItem)
        self.entites.clear()
        Entity.entities.clear()
        Entity.nextEntityId = 0

    def registerStarterEntities(self):
        self.entites['bgi'] = HomeBackground()
        self.entites['button_start'] = ButtonStart()
        self.entites['button_exit'] = ButtonExit()

    def registerStageEntities(self, stage):
        self.entites['board'] = GameBoard()
        self.entites['player'] = GamePlayer()
        self.entites['danmaku'] = GameDanmaku()
        self.entites['bgi'] = GameBackground()
        self.entites['hud'] = GameHUD()
        # self.entites['bgi'] = GameBackground()

class WorldRunner(threading.Thread):
    def __init__(self, world):
        super().__init__()
        self.world = world

    def run(self) -> None:
        count = 0
        while self.world.running:
            start = timeit.default_timer()
            count += 1
            self.world.nextTick()
            end = timeit.default_timer()
            sleepTime = INTERVAL - (end - start)
            if sleepTime > 0:
                time.sleep(sleepTime)


class World:

    def __init__(self):
        super().__init__()
        self.entityManager = EntityManager(self)
        self.systemManager = SystemManager(self)
        self.running = False

    def init(self):
        AudioPlayer.load('starter', 'rainbow_world.mp3')
        AudioPlayer.load('stage-1', 'desire_drive.mp3')

    def start(self):
        self.running = True
        self.thread = WorldRunner(self)
        self.thread.start()

    def nextTick(self):
        self.systemManager.nextTick()
        gui.update()

    def process(self, type, stage=0):
        if type == 'starter':
            self.running = False
            if hasattr(self, 'thread') and self.thread is not None:
                self.thread.join()
            self.systemManager.cancelSystems()
            self.entityManager.cancelEntities()
            self.entityManager.registerStarterEntities()
            self.systemManager.registerStarterSystems()
        elif type == 'stage':
            self.running = False
            self.systemManager.cancelSystems()
            self.entityManager.cancelEntities()
            self.stage(stage)
            self.start()

    def stage(self, stage):
        self.entityManager.registerStageEntities(stage)
        self.systemManager.registerStageSystems(stage)

    def gameStarter(self):
        # 标题界面
        self.process('starter')

    def gameStart(self, stage=0):
        # 重新开始
        self.process('stage', stage)

    def end(self):
        # 游戏结束
        print('游戏结束')

world = World()
