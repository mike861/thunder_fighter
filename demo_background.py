#!/usr/bin/env python3
"""
Dynamic Background Demo
演示新的动态背景系统效果
"""

import pygame
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from thunder_fighter.graphics.background import DynamicBackground
from thunder_fighter.constants import WIDTH, HEIGHT, FPS, WHITE

def main():
    """Run background demo"""
    pygame.init()
    
    # Create window
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Thunder Fighter - Dynamic Background Demo")
    clock = pygame.time.Clock()
    
    # Create background
    background = DynamicBackground()
    
    # Demo font
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    
    print("🎮 动态背景演示启动")
    print("=" * 40)
    print("✨ 特效展示:")
    print("  🌟 多层星空 (3层视差)")
    print("  ✨ 星星闪烁动画")
    print("  🌌 星云云团效果")
    print("  🪐 背景行星")
    print("  🎨 动态渐变背景")
    print()
    print("🎯 按 ESC 退出演示")
    
    running = True
    demo_time = 0
    
    while running:
        dt = clock.tick(FPS)
        demo_time += dt
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Update background
        background.update()
        
        # Draw background
        background.draw(screen)
        
        # Draw demo info
        title_text = font.render("Dynamic Background Demo", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, 50))
        screen.blit(title_text, title_rect)
        
        # Draw feature list
        features = [
            "🌟 Multi-layer Stars (Parallax Effect)",
            "✨ Twinkling Animation",
            "🌌 Nebula Clouds",
            "🪐 Background Planets",
            "🎨 Animated Gradient"
        ]
        
        for i, feature in enumerate(features):
            feature_text = small_font.render(feature, True, WHITE)
            screen.blit(feature_text, (20, 100 + i * 30))
        
        # Draw time
        time_text = small_font.render(f"Demo Time: {demo_time // 1000:.1f}s", True, WHITE)
        screen.blit(time_text, (WIDTH - 200, HEIGHT - 30))
        
        # Draw exit hint
        exit_text = small_font.render("Press ESC to exit", True, WHITE)
        screen.blit(exit_text, (20, HEIGHT - 30))
        
        pygame.display.flip()
    
    pygame.quit()
    print("\n✅ 演示结束")
    print("💡 现在您可以运行完整游戏体验新的背景效果！")
    print("   python main.py")

if __name__ == "__main__":
    main() 