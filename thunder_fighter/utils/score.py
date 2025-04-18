import pygame
from thunder_fighter.constants import WHITE, FONT_NAME, FONT_SIZE_LARGE, TEXT_SCORE

class Score:
    """游戏分数类"""
    def __init__(self):
        self.value = 0
        # 尝试加载系统字体，如果失败则使用默认字体
        try:
            self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE_LARGE)
        except:
            self.font = pygame.font.Font(None, FONT_SIZE_LARGE)
        
    def update(self, points):
        """增加分数"""
        self.value += points
        
    def draw(self, surface, x=10, y=10):
        """显示分数"""
        score_text = self.font.render(TEXT_SCORE.format(self.value), True, WHITE)
        surface.blit(score_text, (x, y))
        
    def get_value(self):
        """获取当前分数"""
        return self.value 