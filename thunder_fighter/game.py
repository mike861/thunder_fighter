import pygame
import time
import random
import sys
from thunder_fighter.constants import (
    WIDTH, HEIGHT, FPS, WHITE, GREEN, DARK_GRAY,
    BASE_ENEMY_COUNT, SCORE_THRESHOLD, BOSS_SPAWN_INTERVAL,
    FONT_NAME, FONT_SIZE_LARGE, FONT_SIZE_MEDIUM, FONT_SIZE_SMALL,
    TEXT_TIME, TEXT_ENEMIES, TEXT_HIGH_LEVEL_ENEMIES, TEXT_BULLET_INFO,
    TEXT_ENEMY_LEVEL_DETAIL, TEXT_GAME_TITLE
)
from thunder_fighter.sprites.player import Player
from thunder_fighter.sprites.enemy import Enemy
from thunder_fighter.sprites.boss import Boss
from thunder_fighter.sprites.items import HealthItem, create_random_item
from thunder_fighter.utils.stars import create_stars
from thunder_fighter.utils.score import Score
from thunder_fighter.utils.collisions import (
    check_bullet_enemy_collisions,
    check_bullet_boss_collisions,
    check_enemy_player_collisions,
    check_boss_bullet_player_collisions,
    check_enemy_bullet_player_collisions,
    check_items_player_collisions
)
from thunder_fighter.graphics.renderers import draw_health_bar
from thunder_fighter.utils.logger import logger
from thunder_fighter.utils.sound_manager import sound_manager

class Game:
    def __init__(self):
        # 初始化pygame
        pygame.init()
        
        # 创建游戏窗口
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TEXT_GAME_TITLE)
        self.clock = pygame.time.Clock()
        
        # 创建精灵组
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.boss_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()  # 新增敌人子弹组
        self.items = pygame.sprite.Group()  # 所有道具组
        
        # 敌人等级追踪
        self.enemy_levels = {i: 0 for i in range(11)}  # 每个级别的敌人数量
        
        # 创建玩家
        self.player = Player(self.all_sprites, self.bullets)
        self.all_sprites.add(self.player)
        
        # 创建敌人
        for i in range(BASE_ENEMY_COUNT):
            self.spawn_enemy()
        
        # 创建背景星星
        self.stars = create_stars(50)
        
        # 创建分数
        self.score = Score()
        
        # 初始化字体
        try:
            self.font_large = pygame.font.SysFont(FONT_NAME, FONT_SIZE_LARGE)
            self.font_medium = pygame.font.SysFont(FONT_NAME, FONT_SIZE_MEDIUM)
            self.font_small = pygame.font.SysFont(FONT_NAME, FONT_SIZE_SMALL)
        except pygame.error as e:
            logger.error(f"Failed to load system font '{FONT_NAME}'. Using default. Error: {e}")
            self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE + 6)
            self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM + 4)
            self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL + 2)
        
        # 道具生成相关变量
        self.last_score_checkpoint = 0
        self.item_spawn_timer = time.time()
        self.item_spawn_interval = 30  # 每30秒可能生成一个随机道具
        
        # Boss相关变量
        self.boss = None  # 直接初始化为None，更明确
        self.boss_spawn_timer = time.time()  # 记录游戏开始时间
        self.boss_active = False
        self.boss_defeated = False
        
        # 游戏时间和敌人生成相关变量
        self.game_start_time = time.time()
        self.enemy_spawn_timer = time.time()
        
        # 游戏状态
        self.running = True
        self.paused = False  # 游戏暂停状态
        
        # 播放背景音乐
        sound_manager.play_background_music('background_music.mp3')
        
        logger.info("Game initialization complete.")
    
    def spawn_enemy(self, game_time=0):
        """生成新敌人"""
        try:
            enemy = Enemy(game_time, self.all_sprites, self.enemy_bullets)
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)
            
            # 记录敌人等级
            level = enemy.get_level()
            self.enemy_levels[level] += 1
            
            # 添加调试输出
            logger.debug(f"Spawned enemy level {level} (can_shoot: {enemy.can_shoot})")
            
            return enemy
        except Exception as e:
            logger.error(f"Error spawning enemy: {e}", exc_info=True)
            return None
    
    def spawn_boss(self):
        """生成Boss"""
        if not self.boss_active and self.boss is None:
            try:
                # 计算游戏进行时间（分钟）
                game_time = (time.time() - self.game_start_time) / 60.0
                
                # 根据游戏时间决定Boss等级
                if game_time < 3:
                    boss_level = 1
                elif game_time < 7:
                    boss_level = 2
                else:
                    boss_level = 3
                    
                # 创建相应等级的Boss
                self.boss = Boss(self.all_sprites, self.boss_bullets, boss_level)
                self.all_sprites.add(self.boss)
                self.boss_active = True
                self.boss_spawn_timer = time.time()  # 重置计时器
                
                # 记录Boss初始位置和大小，便于调试
                logger.debug(f"Boss spawned at: ({self.boss.rect.centerx}, {self.boss.rect.centery})")
                logger.debug(f"Boss dimensions: {self.boss.rect.width}x{self.boss.rect.height}")
                
                # 通知玩家Boss出现
                logger.info(f"Level {boss_level} Boss has appeared!")
            except Exception as e:
                logger.error(f"Error spawning boss: {e}", exc_info=True)
        else:
            logger.warning("Attempted to spawn boss while one is already active or present.")
    
    def spawn_random_item(self, game_time):
        """Generate a random item"""
        try:
            # Pass all required parameters to create_random_item
            create_random_item(game_time, self.all_sprites, self.items)
            # Item is already added to groups inside create_random_item
            logger.debug(f"Random item spawned at game time {game_time:.1f}m")
        except Exception as e:
            logger.error(f"Error spawning random item: {e}", exc_info=True)
    
    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                # 暂停/恢复游戏 (P键)
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                    if self.paused:
                        logger.info("Game paused")
                        # 暂停时降低音乐音量
                        sound_manager.set_music_volume(max(0.1, sound_manager.music_volume / 2))
                    else:
                        logger.info("Game resumed")
                        # 恢复时恢复音乐音量
                        sound_manager.set_music_volume(min(1.0, sound_manager.music_volume * 2))
                # 音效控制快捷键
                elif event.key == pygame.K_m:
                    # 切换背景音乐
                    sound_manager.toggle_music()
                    # 如果重新启用，播放背景音乐
                    if sound_manager.music_enabled and sound_manager.sound_enabled:
                        sound_manager.play_background_music('background_music.mp3')
                elif event.key == pygame.K_s:
                    # 切换音效
                    sound_manager.toggle_sound()
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    # 增加音量
                    current_volume = sound_manager.sound_volume
                    sound_manager.set_sound_volume(current_volume + 0.1)
                    sound_manager.set_music_volume(current_volume + 0.1)
                    logger.info(f"Volume increased to {sound_manager.sound_volume:.1f}")
                elif event.key == pygame.K_MINUS:
                    # 减小音量
                    current_volume = sound_manager.sound_volume
                    sound_manager.set_sound_volume(current_volume - 0.1)
                    sound_manager.set_music_volume(current_volume - 0.1)
                    logger.info(f"Volume decreased to {sound_manager.sound_volume:.1f}")
    
    def update(self):
        """更新游戏状态"""
        # 计算游戏进行时间（分钟）
        game_time = (time.time() - self.game_start_time) / 60.0
        
        # 更新星星
        for star in self.stars:
            star.update()
        
        # 检查是否需要生成Boss
        current_time = time.time()
        if not self.boss_active and current_time - self.boss_spawn_timer >= BOSS_SPAWN_INTERVAL:
            # 重置Boss被击败标志，允许生成新Boss
            self.boss_defeated = False
            self.spawn_boss()
        
        # 根据游戏时间定期检查并生成敌人
        current_time = time.time()
        
        # 计算当前应该有的敌人数量
        target_enemy_count = int(BASE_ENEMY_COUNT + game_time * 3)  # 每分钟增加3个敌人上限
        
        # 敌人生成间隔随时间缩短
        spawn_interval = max(0.2, 1.0 - game_time * 0.05)  # 最小0.2秒
        
        # 检查是否需要生成新敌人
        if current_time - self.enemy_spawn_timer >= spawn_interval and len(self.enemies) < target_enemy_count:
            new_enemy = self.spawn_enemy(game_time)
            self.enemy_spawn_timer = current_time
        
        # 定期检查是否生成随机道具
        if current_time - self.item_spawn_timer >= self.item_spawn_interval:
            # 概率随游戏时间增长
            if random.random() < min(0.3 + game_time * 0.05, 0.8):  # 最高80%概率
                self.spawn_random_item(game_time)
            self.item_spawn_timer = current_time
            # 道具生成间隔随时间缩短
            self.item_spawn_interval = max(15, 30 - game_time)  # 最小15秒
        
        # 更新所有精灵
        self.all_sprites.update()
        
        # 当敌人死亡时，更新等级记录
        for enemy in list(self.enemies):
            if not enemy.alive():
                level = getattr(enemy, 'level', 0)
                if level in self.enemy_levels:
                    self.enemy_levels[level] -= 1
        
        # 检测碰撞
        # 子弹击中敌人
        hit_result = check_bullet_enemy_collisions(
            self.enemies, self.bullets, self.all_sprites, self.score,
            self.last_score_checkpoint, SCORE_THRESHOLD, self.items
        )
        
        if hit_result['enemy_hit']:
            # 播放敌人爆炸音效
            sound_manager.play_sound('enemy_explosion')
            
        self.last_score_checkpoint = hit_result['score_checkpoint']
        
        # 子弹击中Boss
        if self.boss_active and self.boss:
            # 添加日志，输出当前Boss的状态和位置信息，帮助调试
            boss_rect = getattr(self.boss, 'rect', None)
            if boss_rect:
                logger.debug(f"Boss position: ({boss_rect.centerx}, {boss_rect.centery}), health: {self.boss.health}")
                
            # 传递单个Boss实例而不是Group
            boss_result = check_bullet_boss_collisions(self.boss, self.bullets, self.all_sprites)
            
            if boss_result['boss_hit']:
                # 有子弹击中了Boss
                logger.debug(f"Boss hit! Damage: {boss_result['damage']}, Health remaining: {self.boss.health}")
                sound_manager.play_sound('enemy_explosion')  # 使用敌人爆炸音效
                
            if boss_result['boss_defeated']:
                # Boss被击败
                logger.info(f"Boss defeated!")
                self.boss_active = False
                self.boss_defeated = True
                self.boss = None  # 清除Boss实例引用
                self.score.update(100)  # Boss奖励100分
                # 播放击败Boss音效
                sound_manager.play_sound('boss_death')
        
        # 敌人撞到玩家
        player_collision = check_enemy_player_collisions(self.player, self.enemies, self.all_sprites)
        if player_collision['was_hit']:
            # 播放玩家受伤音效
            sound_manager.play_sound('player_hit')
            
        if player_collision['game_over']:
            # 玩家死亡
            sound_manager.play_sound('player_death')
            self.running = False
        
        # Boss子弹击中玩家
        if self.boss_active:
            boss_bullet_hit = check_boss_bullet_player_collisions(self.player, self.boss_bullets, self.all_sprites)
            if boss_bullet_hit['was_hit']:
                # 播放玩家受伤音效
                sound_manager.play_sound('player_hit')
                
            if boss_bullet_hit['game_over']:
                # 玩家死亡
                sound_manager.play_sound('player_death')
                self.running = False
        
        # 敌人子弹击中玩家
        enemy_bullet_hit = check_enemy_bullet_player_collisions(self.player, self.enemy_bullets, self.all_sprites)
        if enemy_bullet_hit['was_hit']:
            # 播放玩家受伤音效
            sound_manager.play_sound('player_hit')
            
        if enemy_bullet_hit['game_over']:
            # 玩家死亡
            sound_manager.play_sound('player_death')
            self.running = False
        
        # 玩家拾取道具
        item_pickup = check_items_player_collisions(self.player, self.items, self.all_sprites)
        if item_pickup['item_collected']:
            # 播放道具拾取音效
            sound_manager.play_sound('item_pickup')
    
    def render(self):
        """渲染游戏画面"""
        # 绘制背景（太空黑色）
        self.screen.fill((10, 10, 20))  # 深蓝黑色的太空
        
        # 绘制星星
        for star in self.stars:
            star.draw(self.screen)
        
        # 绘制所有精灵
        self.all_sprites.draw(self.screen)
        
        # 绘制Boss血条
        if self.boss_active:
            self.boss.draw_health_bar(self.screen)
        
        # 绘制分数
        self.score.draw(self.screen)
        
        # 绘制生命值条
        draw_health_bar(self.screen, WIDTH - 110, 10, 100, 20, self.player.health, 100)
        
        # 绘制游戏时间
        game_time = (time.time() - self.game_start_time) / 60.0
        time_text = self.font_medium.render(TEXT_TIME.format(int(game_time)), True, WHITE)
        self.screen.blit(time_text, (10, 50))
        
        # 绘制敌人数量和级别信息
        target_enemy_count = int(BASE_ENEMY_COUNT + game_time * 3)
        enemy_text = self.font_medium.render(TEXT_ENEMIES.format(len(self.enemies), target_enemy_count), True, WHITE)
        self.screen.blit(enemy_text, (10, 90))
        
        # 绘制敌人等级分布
        # 计算当前高级敌人(5级以上)的数量
        high_level_enemies = sum(self.enemy_levels[i] for i in range(5, 11))
        level_text = self.font_medium.render(TEXT_HIGH_LEVEL_ENEMIES.format(high_level_enemies), True, WHITE)
        self.screen.blit(level_text, (10, 130))
        
        # 绘制玩家子弹信息
        bullet_info = self.font_medium.render(
            TEXT_BULLET_INFO.format(self.player.bullet_paths, self.player.bullet_speed), 
            True, WHITE
        )
        self.screen.blit(bullet_info, (WIDTH - 220, 50))
        
        # 在开发模式下显示更详细的敌人等级分布
        if pygame.key.get_pressed()[pygame.K_F3]:  # F3键查看详细数据
            y_offset = 170
            for level in range(11):
                count = self.enemy_levels[level]
                if count > 0:
                    level_detail = self.font_small.render(TEXT_ENEMY_LEVEL_DETAIL.format(level, count), True, WHITE)
                    self.screen.blit(level_detail, (15, y_offset))
                    y_offset += 20
                    
        # 绘制暂停界面
        if self.paused:
            # 创建半透明覆盖层
            pause_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pause_overlay.fill((0, 0, 0, 150))  # 半透明黑色
            self.screen.blit(pause_overlay, (0, 0))
            
            # 绘制暂停文本
            pause_text = self.font_large.render("GAME PAUSED", True, WHITE)
            text_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
            self.screen.blit(pause_text, text_rect)
            
            # 绘制提示文本
            tip_text = self.font_medium.render("Press P to resume", True, WHITE)
            tip_rect = tip_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
            self.screen.blit(tip_text, tip_rect)
            
            controls_text = self.font_small.render("ESC: Quit  M: Music  S: Sound", True, WHITE)
            controls_rect = controls_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
            self.screen.blit(controls_text, controls_rect)
        
        # 更新显示
        pygame.display.flip()
    
    def run(self):
        """运行游戏主循环"""
        logger.info("Starting main game loop...")
        while self.running:
            # 设置帧率
            self.clock.tick(FPS)
            
            # 处理事件
            self.handle_events()
            
            # 只有在非暂停状态下才更新游戏状态
            if not self.paused:
                self.update()
            
            # 渲染游戏画面
            self.render()
        
        logger.info("Exiting game loop.")
        # 停止背景音乐
        sound_manager.stop_music()
        pygame.quit()
        sys.exit() # Ensure clean exit

if __name__ == '__main__':
    try:
        game = Game()
        game.run()
    except Exception as e:
        # Catch unexpected errors during game setup or run
        logger.critical(f"Critical error during game execution: {e}", exc_info=True)
        pygame.quit()
        sys.exit(1) # Indicate error exit 