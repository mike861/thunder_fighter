"""
分数managementsystem

统一managementgame分数、level、成就等related逻辑.
从utils/score.py重构而来.
"""

import pygame
from typing import Dict, List, Callable, Optional
from thunder_fighter.constants import FONT_NAME, FONT_SIZE_MEDIUM, WHITE
from thunder_fighter.utils.logger import logger


class ScoringSystem:
    """fractionmanagementsystemclass"""
    
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
        """initializedisplayrelatedcomponent"""
        # Use resource manager to load font with caching
        from thunder_fighter.utils.resource_manager import get_resource_manager
        
        resource_manager = get_resource_manager()
        
        try:
            # Use original font size with Chinese character support
            self.font = resource_manager.load_font(FONT_NAME, FONT_SIZE_MEDIUM, system_font=True)
        except Exception:
            self.font = resource_manager.load_font(None, FONT_SIZE_MEDIUM, system_font=True)
    
    def add_score(self, points: int, source: str = ""):
        """addfraction"""
        actual_points = int(points * self.score_multiplier)
        self.score += actual_points
        logger.info(f"Score added: {actual_points} from {source}")
        self.update_display()
        self._check_level_up()
        self._check_achievements()
    
    def update_score(self, points: int):
        """updatefraction(compatible原有interface)"""
        self.add_score(points)
    
    def get_score(self) -> int:
        """getcurrentfraction"""
        return self.score
    
    def get_level(self) -> int:
        """getcurrentlevel"""
        return self.level
    
    def set_multiplier(self, multiplier: float):
        """settingsfraction倍数"""
        self.score_multiplier = multiplier
        logger.info(f"Score multiplier set to: {multiplier}")
    
    def reset(self):
        """resetfraction和level"""
        self.score = 0
        self.level = 1
        self.score_multiplier = 1.0
        self.update_display()
        logger.info("Scoring system reset")
    
    def _check_level_up(self):
        """checkwhetherupgrade"""
        # 每1000分升一级
        new_level = (self.score // 1000) + 1
        if new_level > self.level:
            old_level = self.level
            self.level = new_level
            logger.info(f"Level up! {old_level} -> {new_level}")
            self._trigger_level_up_callbacks(old_level, new_level)
    
    def _check_achievements(self):
        """check成就"""
        # trigger成就回调
        for callback in self.achievement_callbacks:
            try:
                callback(self.score, self.level)
            except Exception as e:
                logger.error(f"Error in achievement callback: {e}")
    
    def add_achievement_callback(self, callback: Callable):
        """add成就回调function"""
        self.achievement_callbacks.append(callback)
    
    def _trigger_level_up_callbacks(self, old_level: int, new_level: int):
        """triggerupgrade回调"""
        # 可以在这里addupgrade时specialeffect
        pass
    
    # Display methods (compatible with original Score class)
    def update_display(self):
        """updatefractiondisplay"""
        from thunder_fighter.localization import _
        score_text = _("SCORE_DISPLAY", self.score)
        self.text = self.font.render(score_text, True, WHITE)
        self.rect = self.text.get_rect()
        self.rect.topleft = (10, 10)
    
    def draw(self, screen: pygame.Surface):
        """displayfraction"""
        if self.text:
            screen.blit(self.text, self.rect)
    
    @property
    def value(self) -> int:
        """compatible原有Scoreclassvalueattribute"""
        return self.score
    
    def update(self, points: int):
        """compatible原有Scoreclassupdatemethod"""
        self.add_score(points)


# Compatibilityfunction:createtraditionScoreclassinstance
def create_legacy_score():
    """createcompatible原有Scoreclassinstance"""
    return ScoringSystem()


# Compatibilityalias
Score = ScoringSystem