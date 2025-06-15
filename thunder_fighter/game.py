import pygame
import time
import random
import sys
from thunder_fighter.constants import (
    WIDTH, HEIGHT, FPS, WHITE, GREEN, DARK_GRAY,
    BASE_ENEMY_COUNT, SCORE_THRESHOLD, BOSS_SPAWN_INTERVAL,
    FONT_NAME, FONT_SIZE_LARGE, FONT_SIZE_MEDIUM, FONT_SIZE_SMALL,
    TEXT_TIME, TEXT_ENEMIES, TEXT_HIGH_LEVEL_ENEMIES, TEXT_BULLET_INFO,
    TEXT_ENEMY_LEVEL_DETAIL, TEXT_GAME_TITLE, MAX_GAME_LEVEL, PLAYER_HEALTH
)
from thunder_fighter.sprites.player import Player
from thunder_fighter.sprites.enemy import Enemy
from thunder_fighter.sprites.boss import Boss
from thunder_fighter.sprites.items import HealthItem, create_random_item
from thunder_fighter.utils.stars import create_stars, Star
from thunder_fighter.utils.score import Score
from thunder_fighter.utils.collisions import (
    check_bullet_enemy_collisions,
    check_bullet_boss_collisions,
    check_enemy_player_collisions,
    check_boss_bullet_player_collisions,
    check_enemy_bullet_player_collisions,
    check_items_player_collisions,
    check_missile_enemy_collisions
)
from thunder_fighter.graphics.renderers import draw_health_bar
from thunder_fighter.utils.logger import logger
from thunder_fighter.utils.sound_manager import sound_manager
from thunder_fighter.graphics.ui_manager import PlayerUIManager
from thunder_fighter.localization import change_language, _

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
        self.enemy_bullets = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.missiles = pygame.sprite.Group()
        
        # 敌人等级追踪
        self.enemy_levels = {i: 0 for i in range(11)}
        
        # 创建玩家
        self.player = Player(self, self.all_sprites, self.bullets, self.missiles, self.enemies)
        self.all_sprites.add(self.player)
        self.player.add_wingman()
        
        # 创建敌人
        for i in range(BASE_ENEMY_COUNT):
            self.spawn_enemy()
        
        # 创建背景星星
        self.stars = create_stars(50)
        
        # 创建分数
        self.score = Score()
        
        # 道具生成相关变量
        self.last_score_checkpoint = 0
        self.item_spawn_timer = time.time()
        self.item_spawn_interval = 30
        
        # Boss相关变量
        self.boss = None
        self.boss_spawn_timer = time.time()
        self.boss_active = False
        self.boss_defeated = False
        
        # 游戏时间和敌人生成相关变量
        self.game_start_time = time.time()
        self.enemy_spawn_timer = time.time()
        
        # 游戏状态
        self.running = True
        self.paused = False
        self.game_level = 1
        self.game_won = False
        
        # 播放背景音乐
        sound_manager.play_background_music('background_music.mp3')
        
        # 初始化UI管理器
        self.ui_manager = PlayerUIManager(self.screen, self.player, self)
        
        self.update_ui_state()
        
        logger.info("Game initialization complete.")

    def update_ui_state(self):
        self.ui_manager.update_game_state(
            level=self.game_level,
            paused=self.paused,
            game_time=(time.time() - self.game_start_time) / 60.0,
            victory=self.game_won,
            defeat=self.player.health <= 0
        )
        self.ui_manager.update_player_info(
            health=self.player.health,
            max_health=PLAYER_HEALTH,
            bullet_paths=self.player.bullet_paths,
            bullet_speed=self.player.bullet_speed,
            speed=self.player.speed,
            wingmen=len(self.player.wingmen_list)
        )
        if self.boss and self.boss.alive():
             self.ui_manager.update_boss_info(
                    active=True,
                    health=self.boss.health,
                    max_health=self.boss.max_health,
                    level=self.boss.level,
                    mode=self.boss.shoot_pattern
                )
        else:
            self.ui_manager.update_boss_info(active=False)

    
    def spawn_enemy(self, game_time=0, game_level=1):
        """生成新敌人"""
        try:
            enemy = Enemy(game_time, game_level, self.all_sprites, self.enemy_bullets)
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)
            
            level = enemy.get_level()
            self.enemy_levels[level] += 1
            logger.debug(f"Spawned enemy level {level} (can_shoot: {enemy.can_shoot})")
            
            return enemy
        except Exception as e:
            logger.error(f"Error spawning enemy: {e}", exc_info=True)
            return None
    
    def spawn_boss(self):
        """生成Boss"""
        if not self.boss_active and self.boss is None:
            try:
                game_time = (time.time() - self.game_start_time) / 60.0
                
                if game_time < 3:
                    boss_level = 1
                elif game_time < 7:
                    boss_level = 2
                else:
                    boss_level = 3
                    
                self.boss = Boss(self.all_sprites, self.boss_bullets, boss_level, self.game_level)
                self.all_sprites.add(self.boss)
                self.boss_active = True
                self.boss_spawn_timer = time.time()
                
                logger.debug(f"Boss spawned at: ({self.boss.rect.centerx}, {self.boss.rect.centery})")
                logger.debug(f"Boss dimensions: {self.boss.rect.width}x{self.boss.rect.height}")
                
                self.ui_manager.show_boss_appeared(boss_level)
                self.update_ui_state()
                
                logger.debug(f"Level {boss_level} Boss has appeared! (Game Level: {self.game_level})")
            except Exception as e:
                logger.error(f"Error spawning boss: {e}", exc_info=True)
        else:
            logger.warning("Attempted to spawn boss while one is already active or present.")
    
    def spawn_random_item(self, game_time):
        """Generate a random item"""
        try:
            item = create_random_item(game_time, self.game_level, self.all_sprites, self.items, self.player)
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
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                    self.update_ui_state()
                    
                    if self.paused:
                        logger.debug("Game paused")
                        sound_manager.set_music_volume(max(0.1, sound_manager.music_volume / 2))
                    else:
                        logger.debug("Game resumed")
                        sound_manager.set_music_volume(min(1.0, sound_manager.music_volume * 2))
                elif event.key == pygame.K_m:
                    sound_manager.toggle_music()
                    if sound_manager.music_enabled and sound_manager.sound_enabled:
                        sound_manager.play_background_music('background_music.mp3')
                elif event.key == pygame.K_s:
                    sound_manager.toggle_sound()
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    current_volume = sound_manager.sound_volume
                    sound_manager.set_sound_volume(current_volume + 0.1)
                    sound_manager.set_music_volume(current_volume + 0.1)
                    logger.debug(f"Volume increased to {sound_manager.sound_volume:.1f}")
                elif event.key == pygame.K_MINUS:
                    current_volume = sound_manager.sound_volume
                    sound_manager.set_sound_volume(current_volume - 0.1)
                    sound_manager.set_music_volume(current_volume - 0.1)
                    logger.debug(f"Volume decreased to {sound_manager.sound_volume:.1f}")
                elif event.key == pygame.K_l:
                    current_lang = 'en' if self.ui_manager.current_language == 'zh' else 'zh'
                    change_language(current_lang)
                    self.ui_manager.current_language = current_lang
                    language_name = "English" if current_lang == 'en' else "中文"
                    self.ui_manager.add_notification(f"Language changed to {language_name}", "achievement")
                    logger.debug(f"Language changed to: {language_name}")
    
    def update(self):
        """更新游戏状态"""
        game_time = (time.time() - self.game_start_time) / 60.0
        
        self.update_ui_state()
        self.ui_manager.update()

        if self.paused:
            return
        
        self.all_sprites.update()
        
        if len(self.enemies) < BASE_ENEMY_COUNT + self.game_level:
            if time.time() - self.enemy_spawn_timer > 1:
                self.spawn_enemy(game_time, self.game_level)
                self.enemy_spawn_timer = time.time()
        
        if time.time() - self.boss_spawn_timer > BOSS_SPAWN_INTERVAL:
            if not self.boss or not self.boss.alive():
                self.spawn_boss()
        
        if time.time() - self.item_spawn_timer > self.item_spawn_interval:
             self.spawn_random_item(game_time)
             self.item_spawn_timer = time.time()
        
        self.handle_collisions(game_time)
        
        if self.score.value // SCORE_THRESHOLD >= self.game_level:
            self.level_up()

        if self.player.health <= 0 and not self.game_won:
            self.game_over()

    def handle_collisions(self, game_time):
        """处理所有碰撞检测"""
        hit_result = check_bullet_enemy_collisions(
            self.enemies, self.bullets, self.all_sprites, self.score, 
            self.last_score_checkpoint, SCORE_THRESHOLD, self.items, self.player
        )
        self.last_score_checkpoint = hit_result['score_checkpoint']
        if hit_result.get('generated_item'):
            self.ui_manager.show_score_milestone(self.score.value)

        check_missile_enemy_collisions(self.missiles, self.enemies, self.all_sprites, self.score)

        check_items_player_collisions(self.items, self.player, self.ui_manager)
        
        if check_enemy_player_collisions(self.player, self.enemies, self.all_sprites)['was_hit']:
            if self.player.health <= 0: self.game_over()

        if check_enemy_bullet_player_collisions(self.player, self.enemy_bullets, self.all_sprites)['was_hit']:
             if self.player.health <= 0: self.game_over()

        if self.boss and self.boss.alive():
            boss_hit_result = check_bullet_boss_collisions(self.boss, self.bullets, self.all_sprites)
            if boss_hit_result['boss_defeated']:
                self.boss_defeated = True
                self.boss.kill()
                self.boss_active = False
                self.boss = None
                self.ui_manager.update_boss_info(active=False)

            if check_boss_bullet_player_collisions(self.player, self.boss_bullets, self.all_sprites)['was_hit']:
                if self.player.health <= 0: self.game_over()
            
            check_missile_enemy_collisions(self.missiles, pygame.sprite.GroupSingle(self.boss), self.all_sprites, self.score)

            if self.boss and self.boss.health <= 0: #Re-check boss after missile collision
                self.boss_defeated = True
                self.boss.kill()
                self.boss_active = False
                self.boss = None
                self.ui_manager.update_boss_info(active=False)

    def level_up(self):
        """提升游戏难度等级"""
        if self.game_level < MAX_GAME_LEVEL:
            self.game_level += 1
            self.enemy_spawn_timer = time.time()
            self.item_spawn_interval = max(15, 30 - self.game_level)
            logger.info(f"Game level up! New level: {self.game_level}")
            self.ui_manager.add_notification(f"Level Up! Level {self.game_level}", "achievement")

    def game_over(self):
        logger.info("Game Over")
        self.running = False

    def render(self):
        """渲染游戏画面"""
        self.screen.fill(DARK_GRAY)
        for star in self.stars:
            star.draw(self.screen)
        
        self.all_sprites.draw(self.screen)
        
        self.ui_manager.draw_player_stats()
        self.ui_manager.draw_game_info()
        self.ui_manager.draw_notifications()
        
        if self.boss_active:
            self.ui_manager.draw_boss_status()
            
        if self.game_won:
            self.ui_manager.show_victory_screen(self.score.value)
        elif self.player.health <= 0:
            self.ui_manager.draw_game_over_screen(self.score.value, self.game_level, (time.time() - self.game_start_time) / 60.0)

        if self.paused:
            self.ui_manager.draw_pause_screen()

        pygame.display.flip()

    def run(self):
        """游戏主循环"""
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.render()
            
            if self.game_level > MAX_GAME_LEVEL and not self.game_won:
                self.game_won = True
                sound_manager.fadeout_music(3000)
                time.sleep(3)
                self.running = False
                
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 