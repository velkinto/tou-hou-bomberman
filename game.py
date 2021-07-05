from gui import gui
from world import world

def init():
    world.init()

def start():
    world.gameStarter()
    world.start()
    gui.start(exit)

def exit():
    world.running = False

if __name__ == '__main__':
    init()
    start()
