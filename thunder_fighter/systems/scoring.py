"""
分数管理系统

统一管理游戏分数、等级、成就等相关逻辑。
从utils/score.py重构而来。
"""

import pygame
from typing import Dict, List, Callable, Optional
from thunder_fighter.constants import FONT_NAME, FONT_SIZE_MEDIUM, WHITE
from thunder_fighter.utils.logger import logger


class ScoringSystem:
    """分数管理系统类"""
    
    def __init__(self):
        self.score = 0
        self.level = 1
        self.score_multiplier = 1.0
        self.achievement_callbacks: List[Callable] = []
        
        # Display related
        self.font = None
        self.text = None
        self.rect = None
        
        self._init_display()
        self.update_display()
    
    def _init_display(self):
        """初始化显示相关组件"""
        # Use resource manager to load font with caching
        from thunder_fighter.utils.resource_manager import get_resource_manager
        
        resource_manager = get_resource_manager()
        
        try:
            # Use original font size with Chinese character support
            self.font = resource_manager.load_font(FONT_NAME, FONT_SIZE_MEDIUM, system_font=True)
        except Exception:
            self.font = resource_manager.load_font(None, FONT_SIZE_MEDIUM, system_font=True)
    
    def add_score(self, points: int, source: str = ""):
        """添加分数"""
        actual_points = int(points * self.score_multiplier)
        self.score += actual_points
        logger.info(f"Score added: {actual_points} from {source}")
        self.update_display()
        self._check_level_up()
        self._check_achievements()
    
    def update_score(self, points: int):
        """更新分数（兼容原有接口）"""
        self.add_score(points)
    
    def get_score(self) -> int:
        """获取当前分数"""
        return self.score
    
    def get_level(self) -> int:
        """获取当前等级"""
        return self.level
    
    def set_multiplier(self, multiplier: float):
        """设置分数倍数"""
        self.score_multiplier = multiplier
        logger.info(f"Score multiplier set to: {multiplier}")
    
    def reset(self):
        """重置分数和等级"""
        self.score = 0
        self.level = 1
        self.score_multiplier = 1.0
        self.update_display()
        logger.info("Scoring system reset")
    
    def _check_level_up(self):
        """检查是否升级"""
        # 每1000分升一级
        new_level = (self.score // 1000) + 1
        if new_level > self.level:
            old_level = self.level
            self.level = new_level
            logger.info(f"Level up! {old_level} -> {new_level}")
            self._trigger_level_up_callbacks(old_level, new_level)
    
    def _check_achievements(self):
        """检查成就"""
        # 触发成就回调
        for callback in self.achievement_callbacks:
            try:
                callback(self.score, self.level)
            except Exception as e:
                logger.error(f"Error in achievement callback: {e}")
    
    def add_achievement_callback(self, callback: Callable):
        """添加成就回调函数"""
        self.achievement_callbacks.append(callback)
    
    def _trigger_level_up_callbacks(self, old_level: int, new_level: int):
        """触发升级回调"""
        # 可以在这里添加升级时的特殊效果
        pass
    
    # Display methods (compatible with original Score class)
    def update_display(self):
        """更新分数显示"""
        from thunder_fighter.localization import _
        score_text = _("SCORE_DISPLAY", self.score)
        self.text = self.font.render(score_text, True, WHITE)
        self.rect = self.text.get_rect()
        self.rect.topleft = (10, 10)
    
    def draw(self, screen: pygame.Surface):
        """显示分数"""
        if self.text:
            screen.blit(self.text, self.rect)
    
    @property
    def value(self) -> int:
        """兼容原有Score类的value属性"""
        return self.score
    
    def update(self, points: int):
        """兼容原有Score类的update方法"""
        self.add_score(points)


# 兼容性函数：创建传统Score类实例
def create_legacy_score():
    """创建兼容原有Score类的实例"""
    return ScoringSystem()


# 兼容性别名
Score = ScoringSystem