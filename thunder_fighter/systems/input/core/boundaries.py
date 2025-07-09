"""
系统边界接口定义

这个模块定义了输入系统与外部世界交互的抽象接口，
实现依赖反转原则，使核心逻辑不依赖具体的实现。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple
from .events import Event


class EventSource(ABC):
    """
    事件源抽象接口
    
    定义了获取输入事件的抽象接口，隔离pygame等具体实现。
    实现类负责将外部输入事件转换为标准的Event对象。
    """
    
    @abstractmethod
    def poll_events(self) -> List[Event]:
        """
        获取所有待处理事件
        
        Returns:
            Event对象列表，包含所有待处理的输入事件
        """
        pass
    
    @abstractmethod
    def clear_events(self):
        """清空事件队列"""
        pass


class KeyboardState(ABC):
    """
    键盘状态抽象接口
    
    定义了查询键盘状态的抽象接口，支持实时查询按键状态。
    """
    
    @abstractmethod
    def is_pressed(self, key_code: int) -> bool:
        """
        检查指定键是否按下
        
        Args:
            key_code: 键码
            
        Returns:
            True如果键被按下，否则False
        """
        pass
    
    @abstractmethod
    def get_pressed_keys(self) -> List[int]:
        """
        获取所有按下的键
        
        Returns:
            当前按下的所有键码列表
        """
        pass


class Clock(ABC):
    """
    时钟抽象接口
    
    定义了时间相关功能的抽象接口，支持可控的时间流逝。
    """
    
    @abstractmethod
    def now(self) -> float:
        """
        获取当前时间
        
        Returns:
            当前时间戳（秒）
        """
        pass
    
    @abstractmethod
    def delta_time(self) -> float:
        """
        获取帧时间间隔
        
        Returns:
            上一帧到这一帧的时间间隔（秒）
        """
        pass


class InputConfiguration(ABC):
    """
    输入配置抽象接口
    
    定义了输入配置的抽象接口，支持键位映射和输入行为配置。
    """
    
    @abstractmethod
    def get_key_mapping(self) -> Dict[int, str]:
        """
        获取键位映射
        
        Returns:
            键码到命令类型的映射字典
        """
        pass
    
    @abstractmethod
    def get_repeat_delay(self) -> float:
        """
        获取按键重复延迟
        
        Returns:
            首次重复前的延迟时间（秒）
        """
        pass
    
    @abstractmethod
    def get_repeat_rate(self) -> float:
        """
        获取按键重复速率
        
        Returns:
            重复按键的间隔时间（秒）
        """
        pass
    
    @abstractmethod
    def is_continuous_key(self, key_code: int) -> bool:
        """
        检查指定键是否支持连续触发
        
        Args:
            key_code: 键码
            
        Returns:
            True如果键支持连续触发（如移动键），否则False
        """
        pass


class Logger(ABC):
    """
    日志抽象接口
    
    定义了日志记录的抽象接口，支持不同级别的日志输出。
    """
    
    @abstractmethod
    def debug(self, message: str):
        """记录调试信息"""
        pass
    
    @abstractmethod
    def info(self, message: str):
        """记录一般信息"""
        pass
    
    @abstractmethod
    def warning(self, message: str):
        """记录警告信息"""
        pass
    
    @abstractmethod
    def error(self, message: str):
        """记录错误信息"""
        pass