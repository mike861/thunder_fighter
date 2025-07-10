"""
system边界接口definitions

这个moduledefinitions了inputsystem与外部世界交互抽象接口,
implementations依赖反转原则,使核心逻辑不依赖具体implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple
from .events import Event


class EventSource(ABC):
    """
    event源抽象接口
    
    definitions了getinputevent抽象接口,隔离pygame等具体implementations.
    implementations类负责将外部inputevent转换为标准Eventobjects.
    """
    
    @abstractmethod
    def poll_events(self) -> List[Event]:
        """
        getall待processevent
        
        Returns:
            Eventobjects列表,Containsall待processinputevent
        """
        pass
    
    @abstractmethod
    def clear_events(self):
        """cleareventqueue"""
        pass


class KeyboardState(ABC):
    """
    键盘state抽象接口
    
    definitions了查询键盘state抽象接口,支持实时查询按键state.
    """
    
    @abstractmethod
    def is_pressed(self, key_code: int) -> bool:
        """
        check指定键whether按下
        
        Args:
            key_code: 键码
            
        Returns:
            Trueif键被按下,elseFalse
        """
        pass
    
    @abstractmethod
    def get_pressed_keys(self) -> List[int]:
        """
        getall按下键
        
        Returns:
            当前按下all键码列表
        """
        pass


class Clock(ABC):
    """
    时钟抽象接口
    
    definitions了timerelated功能抽象接口,支持可控time流逝.
    """
    
    @abstractmethod
    def now(self) -> float:
        """
        get当前time
        
        Returns:
            当前time戳(秒)
        """
        pass
    
    @abstractmethod
    def delta_time(self) -> float:
        """
        get帧time间隔
        
        Returns:
            上一帧到这一帧time间隔(秒)
        """
        pass


class InputConfiguration(ABC):
    """
    inputconfiguration抽象接口
    
    definitions了inputconfiguration抽象接口,支持键位映射和input行为configuration.
    """
    
    @abstractmethod
    def get_key_mapping(self) -> Dict[int, str]:
        """
        get键位映射
        
        Returns:
            键码到命令类型映射字典
        """
        pass
    
    @abstractmethod
    def get_repeat_delay(self) -> float:
        """
        get按键重复delayed
        
        Returns:
            首次重复前delayedtime(秒)
        """
        pass
    
    @abstractmethod
    def get_repeat_rate(self) -> float:
        """
        get按键重复速率
        
        Returns:
            重复按键间隔time(秒)
        """
        pass
    
    @abstractmethod
    def is_continuous_key(self, key_code: int) -> bool:
        """
        check指定键whether支持连续触发
        
        Args:
            key_code: 键码
            
        Returns:
            Trueif键支持连续触发(如movement键),elseFalse
        """
        pass


class Logger(ABC):
    """
    日志抽象接口
    
    definitions了日志record抽象接口,支持不同级别日志output.
    """
    
    @abstractmethod
    def debug(self, message: str):
        """recorddebugginginformation"""
        pass
    
    @abstractmethod
    def info(self, message: str):
        """recordgenerallyinformation"""
        pass
    
    @abstractmethod
    def warning(self, message: str):
        """recordwarninginformation"""
        pass
    
    @abstractmethod
    def error(self, message: str):
        """recorderrorinformation"""
        pass