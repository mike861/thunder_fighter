"""
Game with State Management System

This is an enhanced version of the main Game class that integrates
the state management system for better code organization and maintainability.
"""

import pygame
import time
import random
import sys
from thunder_fighter.constants import (
    WIDTH, HEIGHT, FPS, WHITE, GREEN, DARK_GRAY,
    BASE_ENEMY_COUNT, SCORE_THRESHOLD, BOSS_SPAWN_INTERVAL,
    FONT_NAME, FONT_SIZE_LARGE, FONT_SIZE_MEDIUM, FONT_SIZE_SMALL,
    TEXT_TIME, TEXT_ENEMIES, TEXT_HIGH_LEVEL_ENEMIES, TEXT_BULLET_INFO,
    TEXT_ENEMY_LEVEL_DETAIL, TEXT_GAME_TITLE, MAX_GAME_LEVEL, PLAYER_HEALTH,
    PLAYER_INITIAL_WINGMEN, INITIAL_GAME_LEVEL
)
from thunder_fighter.sprites.player import Player
from thunder_fighter.sprites.enemy import Enemy
from thunder_fighter.sprites.boss import Boss
from thunder_fighter.sprites.items import HealthItem, create_random_item
from thunder_fighter.graphics.background import DynamicBackground
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
from thunder_fighter.utils.sound_manager import SoundManager
from thunder_fighter.graphics.ui_manager import PlayerUIManager
from thunder_fighter.graphics.effects import flash_manager
from thunder_fighter.localization import change_language, _
from thunder_fighter.utils.config_manager import config_manager

# Import state management system
from thunder_fighter.state import (
    GameStateManager,
    StateMachine,
    StateFactory
)


class GameWithStateManagement:
    """
    Enhanced Game class with integrated state management system.
    
    This version uses a state machine to manage game states and provides
    better separation of concerns between game logic and state transitions.
    """
    
    def __init__(self):
        """Initialize the game with state management."""
        # Initialize pygame
        pygame.init()
        
        # Apply display configuration
        display_config = config_manager.display
        if display_config.fullscreen:
            self.screen = pygame.display.set_mode((display_config.width, display_config.height), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        
        pygame.display.set_caption(TEXT_GAME_TITLE)
        self.clock = pygame.time.Clock()
        
        # Font for dev mode enemy level display
        self.dev_font = pygame.font.Font(None, 18) if config_manager.debug.dev_mode else None
        
        # Initialize state management system
        self.state_manager = GameStateManager()
        self.state_machine = StateMachine()
        
        # Create and add all game states
        states = StateFactory.create_all_states(self)
        for state in states:
            self.state_machine.add_state(state)
        
        # Set initial state
        self.state_machine.set_current_state("playing")
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.boss_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.missiles = pygame.sprite.Group()
        
        # Enemy level tracking
        self.enemy_levels = {i: 0 for i in range(11)}
        
        # Create player with difficulty modifiers
        difficulty_multipliers = config_manager.get_difficulty_multipliers()
        
        # Initialize sound manager first
        self.sound_manager = SoundManager(config_manager.sound)
        
        self.player = Player(self, self.all_sprites, self.bullets, self.missiles, self.enemies, self.sound_manager)
        # Apply difficulty-based speed modifier
        self.player.speed = int(self.player.speed * difficulty_multipliers['player_speed'])
        self.all_sprites.add(self.player)
        
        # Add initial wingmen based on configuration
        for _ in range(PLAYER_INITIAL_WINGMEN):
            self.player.add_wingman()
        
        # Create enemies
        for i in range(BASE_ENEMY_COUNT):
            self.spawn_enemy()
        
        # Create dynamic background
        self.background = DynamicBackground()
        
        # Create score with difficulty multiplier
        self.score = Score()
        self.score_multiplier = difficulty_multipliers['score_multiplier']
        
        # Item spawn related variables
        self.last_score_checkpoint = 0
        self.item_spawn_timer = time.time()
        self.item_spawn_interval = 30
        
        self.target_enemy_count = BASE_ENEMY_COUNT
        
        # Boss related variables
        self.boss = None
        self.boss_spawn_timer = time.time()
        self.boss_active = False
        self.boss_defeated = False
        
        # Game time and enemy spawn related variables
        self.game_start_time = time.time()
        self.enemy_spawn_timer = time.time()
        
        # Legacy game state variables (for compatibility)
        self.running = True
        self.paused = False
        self.game_level = INITIAL_GAME_LEVEL
        self.game_won = False
        
        # Constants needed by states
        self.BOSS_SPAWN_INTERVAL = BOSS_SPAWN_INTERVAL
        self.SCORE_THRESHOLD = SCORE_THRESHOLD
        
        # Initialize state manager with current values
        self.sync_state_manager()
        
        # Play background music
        self.sound_manager.play_music('background_music.mp3')
        
        # Initialize UI manager
        self.ui_manager = PlayerUIManager(self.screen, self.player, self)
        
        self.update_ui_state()
        
        logger.info("Game with state management initialized.")
        logger.info(f"Difficulty: {config_manager.gameplay.difficulty}")
        logger.info(f"Difficulty multipliers: {difficulty_multipliers}")
        logger.info(f"Initial state: {self.state_machine.get_current_state_name()}")
    
    def sync_state_manager(self):
        """Sync the state manager with current game values."""
        state = self.state_manager.get_state()
        state.running = self.running
        state.paused = self.paused
        state.level = self.game_level
        state.score = self.score.value
        state.game_won = self.game_won
        state.game_over = self.player.health <= 0
        state.player_health = self.player.health
        state.player_max_health = PLAYER_HEALTH
        state.player_bullet_paths = self.player.bullet_paths
        state.player_bullet_speed = self.player.bullet_speed
        state.player_speed = self.player.speed
        state.player_wingmen = len(self.player.wingmen_list)
        state.enemy_count = len(self.enemies)
        state.target_enemy_count = self.target_enemy_count
        state.boss_active = self.boss_active
        if self.boss and self.boss.alive():
            state.boss_health = self.boss.health
            state.boss_max_health = self.boss.max_health
            state.boss_level = self.boss.level
            state.boss_mode = self.boss.shoot_pattern
        state.item_spawn_interval = self.item_spawn_interval
    
    def update_ui_state(self):
        """Update UI state from state manager."""
        state = self.state_manager.get_state()
        
        self.ui_manager.update_game_state(
            level=state.level,
            paused=state.paused,
            game_time=state.game_time,
            victory=state.game_won,
            defeat=state.game_over
        )
        
        # Update persistent info with current score
        self.ui_manager.persistent_info['score'] = state.score
        
        self.ui_manager.update_player_info(
            health=state.player_health,
            max_health=state.player_max_health,
            bullet_paths=state.player_bullet_paths,
            bullet_speed=state.player_bullet_speed,
            speed=state.player_speed,
            wingmen=state.player_wingmen
        )
        
        if state.boss_active and self.boss and self.boss.alive():
            self.ui_manager.update_boss_info(
                active=True,
                health=state.boss_health,
                max_health=state.boss_max_health,
                level=state.boss_level,
                mode=state.boss_mode
            )
        else:
            self.ui_manager.update_boss_info(active=False)
    
    def _check_sound_system(self):
        """Check and fix sound system if needed"""
        if not self.sound_manager.is_healthy():
            logger.warning("Sound system unhealthy, attempting to fix...")
            self.sound_manager.reinitialize()
        else:
            # Even if system is healthy, ensure music is playing
            self.sound_manager.ensure_music_playing()
    
    def spawn_enemy(self, game_time=0, game_level=1):
        """Spawn a new enemy"""
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
        """Spawn a Boss"""
        if not self.boss_active and self.boss is None:
            try:
                # Boss等级是游戏等级的1/2，最小为1级
                boss_level = max(1, (self.game_level + 1) // 2)
                    
                self.boss = Boss(self.all_sprites, self.boss_bullets, boss_level, self.game_level, self.player)
                self.all_sprites.add(self.boss)
                self.boss_active = True
                self.boss_spawn_timer = time.time()
                
                logger.debug(f"Boss spawned at: ({self.boss.rect.centerx}, {self.boss.rect.centery})")
                logger.debug(f"Boss dimensions: {self.boss.rect.width}x{self.boss.rect.height}")
                
                self.ui_manager.show_boss_appeared(boss_level)
                self.sync_state_manager()
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
        """Handle game events and delegate to state machine."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                # Handle global events
                if event.key == pygame.K_m:
                    self.sound_manager.toggle_music()
                    if self.sound_manager.music_enabled:
                        self.sound_manager.play_music('background_music.mp3')
                elif event.key == pygame.K_s:
                    self.sound_manager.toggle_sound()
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    current_volume = self.sound_manager.sound_volume
                    self.sound_manager.set_sound_volume(current_volume + 0.1)
                    self.sound_manager.set_music_volume(current_volume + 0.1)
                    logger.debug(f"Volume increased to {self.sound_manager.sound_volume:.1f}")
                elif event.key == pygame.K_MINUS:
                    current_volume = self.sound_manager.sound_volume
                    self.sound_manager.set_sound_volume(current_volume - 0.1)
                    self.sound_manager.set_music_volume(current_volume - 0.1)
                    logger.debug(f"Volume decreased to {self.sound_manager.sound_volume:.1f}")
                elif event.key == pygame.K_l:
                    current_lang = 'en' if self.ui_manager.current_language == 'zh' else 'zh'
                    change_language(current_lang)
                    self.ui_manager.current_language = current_lang
                    language_name = "English" if current_lang == 'en' else "中文"
                    self.ui_manager.add_notification(f"Language changed to {language_name}", "achievement")
                    logger.debug(f"Language changed to: {language_name}")
            
            # Delegate event to current state
            self.state_machine.handle_event(event)
    
    def update(self):
        """Update game state using state machine."""
        # Calculate delta time
        dt = self.clock.get_time() / 1000.0  # Convert to seconds
        
        # Update state manager
        self.state_manager.update()
        self.sync_state_manager()
        
        # Update UI
        self.update_ui_state()
        self.ui_manager.update()
        
        # Update flash effects
        flash_manager.update()
        
        # Check sound system health periodically (every 2 seconds)
        if hasattr(self, '_last_sound_check'):
            if time.time() - self._last_sound_check > 2:
                self._check_sound_system()
                self._last_sound_check = time.time()
        else:
            self._last_sound_check = time.time()
        
        # Update state machine (this will call the current state's update method)
        self.state_machine.update(dt)
        
        # Update sprites if game logic should run
        if self.state_manager.should_update_game_logic():
            self.background.update()
            self.all_sprites.update()
            
            # Handle collisions
            game_time = (time.time() - self.game_start_time) / 60.0
            self.handle_collisions(game_time)
            
            # Reset boss defeat processing flag after delay
            if hasattr(self, '_boss_defeat_reset_time') and time.time() >= self._boss_defeat_reset_time:
                if hasattr(self, '_boss_defeat_processed'):
                    delattr(self, '_boss_defeat_processed')
                delattr(self, '_boss_defeat_reset_time')
        
        # Sync legacy state variables
        state = self.state_manager.get_state()
        self.paused = state.paused
        self.game_won = state.game_won
        self.game_level = state.level
    
    def handle_collisions(self, game_time):
        """Handle all collision detection"""
        hit_result = check_bullet_enemy_collisions(
            self.enemies, self.bullets, self.all_sprites, self.score, 
            self.last_score_checkpoint, SCORE_THRESHOLD, self.items, self.player
        )
        self.last_score_checkpoint = hit_result['score_checkpoint']
        if hit_result.get('generated_item'):
            self.ui_manager.show_score_milestone(self.score.value)

        check_missile_enemy_collisions(self.missiles, self.enemies, self.all_sprites, self.score)

        check_items_player_collisions(self.items, self.player, self.ui_manager, self.sound_manager)
        
        if check_enemy_player_collisions(self.player, self.enemies, self.all_sprites)['was_hit']:
            if self.player.health <= 0:
                self.state_machine.transition_to("game_over")

        if check_enemy_bullet_player_collisions(self.player, self.enemy_bullets, self.all_sprites)['was_hit']:
            if self.player.health <= 0:
                self.state_machine.transition_to("game_over")

        if self.boss and self.boss.alive():
            boss_hit_result = check_bullet_boss_collisions(self.boss, self.bullets, self.all_sprites)
            if boss_hit_result['boss_defeated']:
                self.handle_boss_defeated()

            if check_boss_bullet_player_collisions(self.player, self.boss_bullets, self.all_sprites)['was_hit']:
                if self.player.health <= 0:
                    self.state_machine.transition_to("game_over")
            
            check_missile_enemy_collisions(self.missiles, pygame.sprite.GroupSingle(self.boss), self.all_sprites, self.score)

            if self.boss and self.boss.health <= 0:
                self.handle_boss_defeated()
    
    def handle_boss_defeated(self):
        """Handle boss defeat: level up, clear enemies, and show effects"""
        if not hasattr(self, '_boss_defeat_processed'):
            self._boss_defeat_processed = True
            
            # Store boss level for scoring before removing boss
            boss_level = self.boss.level if self.boss else 1
            
            # Remove boss
            self.boss_defeated = True
            if self.boss:
                self.boss.kill()
            self.boss_active = False
            self.boss = None
            self.ui_manager.update_boss_info(active=False)
            
            # Check if this is the final boss (level 10)
            if self.game_level >= MAX_GAME_LEVEL:
                # Game victory!
                self.game_won = True
                logger.info(f"Final boss defeated at level {self.game_level}! Game won!")
                
                # Add final boss score bonus
                final_boss_bonus = boss_level * 1000
                self.score.update(final_boss_bonus)
                
                # Show victory screen
                self.ui_manager.show_victory_screen(self.score.value)
                
                # Play victory sound and fade out music
                self.sound_manager.play_sound('boss_death.wav')
                self.sound_manager.fadeout_music(3000)
                
                # Transition to victory state
                self.state_machine.transition_to("victory")
                return
            
            # Level up the game (only if not at max level)
            old_level = self.game_level
            if self.game_level < MAX_GAME_LEVEL:
                self.game_level += 1
                logger.info(f"Boss defeated! Game level up from {old_level} to {self.game_level}")
                
                # Trigger level transition state
                self.state_machine.transition_to("level_transition")
            
            # Clear all enemies on screen
            enemies_cleared = len(self.enemies)
            for enemy in self.enemies:
                enemy.kill()
            self.enemies.empty()
            
            # Clear enemy bullets
            for bullet in self.enemy_bullets:
                bullet.kill()
            self.enemy_bullets.empty()
            
            # Clear boss bullets
            for bullet in self.boss_bullets:
                bullet.kill()
            self.boss_bullets.empty()
            
            # Add score bonus for boss defeat
            boss_score_bonus = boss_level * 500
            self.score.update(boss_score_bonus)
            
            # Show victory effects and notifications
            self.ui_manager.show_level_up_effects(old_level, self.game_level, enemies_cleared, boss_score_bonus)
            
            # Play victory sound
            self.sound_manager.play_sound('boss_death.wav')
            
            # Reset boss spawn timer for next boss
            self.boss_spawn_timer = time.time()
            
            # Reset enemy spawn timer
            self.enemy_spawn_timer = time.time()
            
            # Update item spawn interval for new level
            self.item_spawn_interval = max(15, 30 - self.game_level)
            
            # Reset the defeat processing flag after a delay (handled in main event loop)
            self._boss_defeat_reset_time = time.time() + 3.0
    
    def level_up(self):
        """Increase game difficulty level based on score (only for early levels)"""
        if self.game_level < MAX_GAME_LEVEL:
            old_level = self.game_level
            self.game_level += 1
            self.enemy_spawn_timer = time.time()
            self.item_spawn_interval = max(15, 30 - self.game_level)
            logger.info(f"Score-based level up from {old_level} to {self.game_level}")
            self.ui_manager.show_score_level_up(self.game_level)
            
            # Use state manager for level transitions
            self.state_manager.level_up(self.game_level)
    
    def game_over(self):
        """Handle game over."""
        logger.info("Game Over")
        self.state_machine.transition_to("game_over")
    
    def render(self):
        """Render game screen"""
        # Draw dynamic background
        self.background.draw(self.screen)
        
        self.all_sprites.draw(self.screen)
        
        # 如果boss存在且存活，绘制跟随boss移动的血条
        if self.boss and self.boss.alive():
            self.boss.draw_health_bar(self.screen)
        
        # Get current state for rendering decisions
        current_state = self.state_machine.get_current_state_name()
        
        # Draw UI based on current state
        if current_state == "victory":
            self.ui_manager.draw_victory_screen(self.score.value, MAX_GAME_LEVEL)
        elif current_state == "game_over":
            self.ui_manager.draw_game_over_screen(self.score.value, self.game_level, (time.time() - self.game_start_time) / 60.0)
        elif current_state == "paused":
            # Draw normal UI first, then pause overlay
            self.ui_manager.draw_player_stats()
            self.ui_manager.draw_game_info()
            self.ui_manager.draw_notifications()
            self.ui_manager.draw_pause_screen()
        else:
            # Normal game rendering
            self.ui_manager.draw_player_stats()
            self.ui_manager.draw_game_info()
            self.ui_manager.draw_notifications()
        
        # Draw developer info if enabled
        if config_manager.debug.dev_mode and current_state in ["playing", "level_transition"]:
            fps = self.clock.get_fps()
            player_pos = self.player.rect.center
            enemy_count = len(self.enemies)
            self.ui_manager.draw_dev_info(fps, enemy_count, self.target_enemy_count, player_pos)

            # Draw level text next to each enemy
            for enemy in self.enemies:
                level_text = f"L{enemy.get_level()}"
                text_surf = self.dev_font.render(level_text, True, WHITE)
                self.screen.blit(text_surf, (enemy.rect.right + 2, enemy.rect.top))
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop with state management."""
        logger.info("Starting game loop with state management")
        
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.render()
            
            # Check if we should exit
            current_state = self.state_machine.get_current_state_name()
            if current_state in ["victory", "game_over"]:
                # These states handle their own exit logic
                continue
        
        logger.info("Game loop ended")
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = GameWithStateManagement()
    game.run() 