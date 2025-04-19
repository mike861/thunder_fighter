"""
雷霆战机 (Thunder Fighter)
一个简单的太空射击游戏

此文件为兼容原版代码入口，实际使用模块化代码结构。
使用方向键控制飞机移动，空格键发射子弹。
"""

from thunder_fighter.game import Game

def main():
    """游戏入口函数"""
    game = Game()
    game.run()

if __name__ == "__main__":
    main() 