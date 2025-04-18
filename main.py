#!/usr/bin/env python3
"""
雷霆战机 (Thunder Fighter)
一个简单的太空射击游戏

使用方向键控制飞机移动，空格键发射子弹。
"""

from thunder_fighter.game import Game

def main():
    """游戏入口函数"""
    game = Game()
    game.run()

if __name__ == "__main__":
    main() 