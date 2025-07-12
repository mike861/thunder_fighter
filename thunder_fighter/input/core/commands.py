"""
命令模式实现 - 解耦输入和游戏逻辑

这个模块定义了游戏命令系统，将输入事件转换为游戏命令，
实现输入系统和游戏逻辑的完全解耦。
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict


class CommandType(Enum):
    """游戏命令类型枚举"""
    
    # 移动命令
    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    
    # 动作命令
    SHOOT = "shoot"
    LAUNCH_MISSILE = "launch_missile"
    
    # 系统命令
    PAUSE = "pause"
    QUIT = "quit"
    TOGGLE_MUSIC = "toggle_music"
    TOGGLE_SOUND = "toggle_sound"
    CHANGE_LANGUAGE = "change_language"
    
    # 调试命令
    TOGGLE_DEBUG = "toggle_debug"
    RESET_INPUT = "reset_input"


@dataclass
class Command:
    """
    游戏命令
    
    表示一个具体的游戏命令，包含命令类型、时间戳和相关数据。
    这是输入系统和游戏逻辑之间的接口。
    """
    type: CommandType
    timestamp: float
    data: Dict[str, Any] = None
    
    def __post_init__(self):
        """初始化后处理，确保数据字典总是存在"""
        if self.data is None:
            self.data = {}
    
    def get_data(self, key: str, default=None):
        """安全获取命令数据"""
        return self.data.get(key, default)
    
    def set_data(self, key: str, value: Any):
        """设置命令数据"""
        self.data[key] = value
    
    def is_movement_command(self) -> bool:
        """检查是否为移动命令"""
        return self.type in (
            CommandType.MOVE_UP, 
            CommandType.MOVE_DOWN, 
            CommandType.MOVE_LEFT, 
            CommandType.MOVE_RIGHT
        )
    
    def is_action_command(self) -> bool:
        """检查是否为动作命令"""
        return self.type in (
            CommandType.SHOOT, 
            CommandType.LAUNCH_MISSILE
        )
    
    def is_system_command(self) -> bool:
        """检查是否为系统命令"""
        return self.type in (
            CommandType.PAUSE,
            CommandType.QUIT,
            CommandType.TOGGLE_MUSIC,
            CommandType.TOGGLE_SOUND,
            CommandType.CHANGE_LANGUAGE,
            CommandType.TOGGLE_DEBUG,
            CommandType.RESET_INPUT
        )