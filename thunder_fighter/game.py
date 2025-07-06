"""
Refactored Game Class

Enhanced version of the main Game class that integrates all architectural improvements:
- Input management system
- Event-driven architecture
- Factory pattern for entity creation
- Resource management system
- UI system decoupling
"""

import pygame
import time
import random
import sys
from typing import List, Optional
from thunder_fighter.constants import (
    WIDTH, HEIGHT, FPS, WHITE, GREEN, DARK_GRAY,
    BASE_ENEMY_COUNT, SCORE_THRESHOLD, BOSS_SPAWN_INTERVAL,
    TEXT_GAME_TITLE, MAX_GAME_LEVEL, PLAYER_HEALTH,
    PLAYER_INITIAL_WINGMEN, INITIAL_GAME_LEVEL
)
from thunder_fighter.sprites.player import Player
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
from thunder_fighter.utils.logger import logger
from thunder_fighter.utils.sound_manager import SoundManager
from thunder_fighter.utils.resource_manager import get_resource_manager
from thunder_fighter.graphics.ui_manager import UIManager
from thunder_fighter.graphics.effects import flash_manager
from thunder_fighter.localization import change_language, _
from thunder_fighter.utils.config_manager import config_manager

# Import input management system
from thunder_fighter.input import InputManager, InputEvent, InputEventType

# Import event system
from thunder_fighter.events import EventSystem, GameEventType, GameEvent

# Import factory systems
from thunder_fighter.entities import (
    EnemyFactory,
    BossFactory,
    ItemFactory,
    ProjectileFactory
)

# Import pause manager
from thunder_fighter.utils.pause_manager import PauseManager


class RefactoredGame:
    """
    Refactored Game class with full architectural improvements.
    
    This version implements:
    - Event-driven input handling
    - Centralized resource management
    - Factory pattern for entity creation
    - Decoupled UI system
    - Event-driven game logic
    """
    
    def __init__(self):
        """Initialize the refactored game."""
        # Initialize pygame
        pygame.init()
        
        # Initialize resource manager
        self.resource_manager = get_resource_manager()
        self.resource_manager.preload_common_assets()
        
        # Apply display configuration
        display_config = config_manager.display
        if display_config.fullscreen:
            self.screen = pygame.display.set_mode(
                (display_config.width, display_config.height), 
                pygame.FULLSCREEN
            )
        else:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        
        pygame.display.set_caption(TEXT_GAME_TITLE)
        self.clock = pygame.time.Clock()
        
        # Initialize event system
        self.event_system = EventSystem()
        self._setup_event_listeners()
        
        # Initialize input management
        self.input_manager = InputManager()
        self._setup_input_callbacks()
        
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
        
        # Initialize factories
        self.enemy_factory = EnemyFactory()
        self.boss_factory = BossFactory()
        self.item_factory = ItemFactory()
        self.projectile_factory = ProjectileFactory()
        
        # Create player with difficulty modifiers
        difficulty_multipliers = config_manager.get_difficulty_multipliers()
        
        # Initialize sound manager
        self.sound_manager = SoundManager(config_manager.sound)
        
        # Create player
        self.player = Player(
            self, self.all_sprites, self.bullets, 
            self.missiles, self.enemies, self.sound_manager
        )
        # Apply difficulty-based speed modifier
        self.player.speed = int(self.player.speed * difficulty_multipliers['player_speed'])
        self.all_sprites.add(self.player)
        
        # Add initial wingmen
        for _ in range(PLAYER_INITIAL_WINGMEN):
            self.player.add_wingman()
        
        # Create dynamic background
        self.background = DynamicBackground()
        
        # Create score with difficulty multiplier
        self.score = Score()
        self.score_multiplier = difficulty_multipliers['score_multiplier']
        
        # Game state variables
        self.running = True
        self.game_level = INITIAL_GAME_LEVEL
        self.game_won = False
        self.game_over = False  # New: game over state flag
        
        # Initialize pause manager
        self.pause_manager = PauseManager(cooldown_ms=200)
        self.paused = False  # Keep for backward compatibility
        
        # Set initial background level
        self.background.set_level(self.game_level)
        
        # Timing variables - set these BEFORE creating initial enemies
        self.game_start_time = time.time()
        self.enemy_spawn_timer = time.time()
        self.item_spawn_timer = time.time()
        self.boss_spawn_timer = time.time()
        
        # macOS keyboard focus recovery
        self.last_input_validation_time = time.time()
        self.input_validation_interval = 10.0  # Check every 10 seconds (reduced frequency)
        
        # Create initial enemies using factory (after game_start_time is set)
        for i in range(BASE_ENEMY_COUNT):
            self._spawn_enemy_via_factory()
        
        # Game configuration
        self.target_enemy_count = BASE_ENEMY_COUNT
        self.item_spawn_interval = 30
        self.last_score_checkpoint = 0
        
        # Boss state
        self.boss = None
        self.boss_active = False
        self.boss_defeated = False
        
        # Initialize UI manager with event system integration
        self.ui_manager = UIManager(self.screen, self.player, self)
        self._setup_ui_event_listeners()
        
        # Play background music
        music_path = self.resource_manager.get_music_path('background_music.mp3')
        if music_path:
            self.sound_manager.play_music('background_music.mp3')
        
        # Initial state update
        self._update_ui_state()
        
        logger.info("RefactoredGame initialized with all architectural improvements")
        logger.info(f"Difficulty: {config_manager.gameplay.difficulty}")
        logger.info(f"Resource cache stats: {self.resource_manager.get_cache_stats()}")
    
    def _restart_game(self):
        """Restart the game to initial state."""
        logger.info("Restarting game")
        
        # Reset game state
        self.game_over = False
        self.game_won = False
        self.pause_manager.reset()  # Reset pause manager
        self.paused = False  # Keep for backward compatibility
        self.game_level = INITIAL_GAME_LEVEL
        
        # Reset timing
        self.game_start_time = time.time()
        self.enemy_spawn_timer = time.time()
        self.item_spawn_timer = time.time()
        self.boss_spawn_timer = time.time()
        
        # Reset score
        self.score.reset()
        self.last_score_checkpoint = 0
        
        # Clear all sprites except player
        for sprite in self.all_sprites:
            if sprite != self.player:
                sprite.kill()
        
        # Reset player
        self.player.health = PLAYER_HEALTH
        self.player.rect.centerx = WIDTH // 2
        self.player.rect.bottom = HEIGHT - 50
        self.player.bullet_paths = 1
        self.player.bullet_speed = 7
        self.player.speed = 5
        self.player.wingmen_list.clear()
        
        # Add initial wingmen
        for _ in range(PLAYER_INITIAL_WINGMEN):
            self.player.add_wingman()
        
        # Reset boss state
        self.boss = None
        self.boss_active = False
        self.boss_defeated = False
        
        # Reset background
        self.background.set_level(self.game_level)
        
        # Reset UI state
        self.ui_manager.reset_game_state()
        
        # Create initial enemies
        for i in range(BASE_ENEMY_COUNT):
            self._spawn_enemy_via_factory()
        
        # Reset configuration
        self.target_enemy_count = BASE_ENEMY_COUNT
        self.item_spawn_interval = 30
        
        # Play background music
        music_path = self.resource_manager.get_music_path('background_music.mp3')
        if music_path:
            self.sound_manager.play_music('background_music.mp3')
        
        logger.info("Game restarted successfully")
    
    def _setup_event_listeners(self):
        """Set up event system listeners."""
        # Game state events
        self.event_system.register_listener(
            GameEventType.PLAYER_DIED, 
            self._handle_player_died
        )
        self.event_system.register_listener(
            GameEventType.BOSS_DEFEATED, 
            self._handle_boss_defeated_event
        )
        self.event_system.register_listener(
            GameEventType.LEVEL_UP, 
            self._handle_level_up_event
        )
        self.event_system.register_listener(
            GameEventType.GAME_WON, 
            self._handle_game_won_event
        )
        
        # Entity events
        self.event_system.register_listener(
            GameEventType.ENEMY_SPAWNED, 
            self._handle_enemy_spawned
        )
        self.event_system.register_listener(
            GameEventType.ITEM_COLLECTED, 
            self._handle_item_collected
        )
        
        logger.debug("Event listeners set up")
    
    def _setup_input_callbacks(self):
        """Set up input event callbacks."""
        # Movement
        self.input_manager.add_event_callback(
            InputEventType.MOVE_UP, 
            self._handle_movement_input
        )
        self.input_manager.add_event_callback(
            InputEventType.MOVE_DOWN, 
            self._handle_movement_input
        )
        self.input_manager.add_event_callback(
            InputEventType.MOVE_LEFT, 
            self._handle_movement_input
        )
        self.input_manager.add_event_callback(
            InputEventType.MOVE_RIGHT, 
            self._handle_movement_input
        )
        
        # Actions
        self.input_manager.add_event_callback(
            InputEventType.SHOOT, 
            self._handle_shoot_input
        )
        self.input_manager.add_event_callback(
            InputEventType.LAUNCH_MISSILE, 
            self._handle_missile_input
        )
        
        # Game controls
        self.input_manager.add_event_callback(
            InputEventType.PAUSE, 
            self._handle_pause_input
        )
        self.input_manager.add_event_callback(
            InputEventType.QUIT, 
            self._handle_quit_input
        )
        
        # Audio controls
        self.input_manager.add_event_callback(
            InputEventType.TOGGLE_MUSIC, 
            self._handle_audio_input
        )
        self.input_manager.add_event_callback(
            InputEventType.TOGGLE_SOUND, 
            self._handle_audio_input
        )
        self.input_manager.add_event_callback(
            InputEventType.VOLUME_UP, 
            self._handle_audio_input
        )
        self.input_manager.add_event_callback(
            InputEventType.VOLUME_DOWN, 
            self._handle_audio_input
        )
        
        # UI controls
        self.input_manager.add_event_callback(
            InputEventType.CHANGE_LANGUAGE, 
            self._handle_ui_input
        )
        
        logger.debug("Input callbacks set up")
    
    def _setup_ui_event_listeners(self):
        """Set up UI event listeners for decoupled UI updates."""
        # Player state changes
        self.event_system.register_listener(
            GameEventType.PLAYER_HEALTH_CHANGED, 
            self._handle_ui_player_health_changed
        )
        self.event_system.register_listener(
            GameEventType.PLAYER_STATS_CHANGED, 
            self._handle_ui_player_stats_changed
        )
        
        # Game state changes
        self.event_system.register_listener(
            GameEventType.SCORE_CHANGED, 
            self._handle_ui_score_changed
        )
        self.event_system.register_listener(
            GameEventType.LEVEL_UP, 
            self._handle_ui_level_changed
        )
        
        # Boss state changes
        self.event_system.register_listener(
            GameEventType.BOSS_SPAWNED, 
            self._handle_ui_boss_spawned
        )
        self.event_system.register_listener(
            GameEventType.BOSS_DEFEATED, 
            self._handle_ui_boss_defeated
        )
        
        logger.debug("UI event listeners set up")
    
    def _spawn_enemy_via_factory(self, game_time: Optional[float] = None, 
                                game_level: Optional[int] = None) -> bool:
        """Spawn an enemy using the factory pattern."""
        if game_time is None:
            game_time = (time.time() - self.game_start_time) / 60.0
        if game_level is None:
            game_level = self.game_level
        
        try:
            enemy = self.enemy_factory.create_for_level(
                game_level, game_time, self.all_sprites, self.enemy_bullets
            )
            
            if enemy:
                self.all_sprites.add(enemy)
                self.enemies.add(enemy)
                
                # Track enemy level
                level = enemy.get_level()
                self.enemy_levels[level] += 1
                
                # Emit event
                self.event_system.dispatch_event(GameEvent(
                    GameEventType.ENEMY_SPAWNED,
                    {'enemy': enemy, 'level': level, 'game_time': game_time}
                ))
                
                logger.debug(f"Factory spawned enemy level {level}")
                return True
        except Exception as e:
            logger.error(f"Error spawning enemy via factory: {e}", exc_info=True)
        
        return False
    
    def _spawn_boss_via_factory(self) -> bool:
        """Spawn a boss using the factory pattern."""
        if self.boss_active or self.boss:
            return False
        
        try:
            boss_level = max(1, (self.game_level + 1) // 2)
            
            self.boss = self.boss_factory.create_from_preset(
                "standard",
                all_sprites=self.all_sprites, 
                boss_bullets=self.boss_bullets,
                boss_level=boss_level, 
                game_level=self.game_level, 
                player=self.player
            )
            
            if self.boss:
                self.all_sprites.add(self.boss)
                self.boss_active = True
                self.boss_spawn_timer = time.time()
                
                # Emit event
                self.event_system.dispatch_event(GameEvent(
                    GameEventType.BOSS_SPAWNED,
                    {'boss': self.boss, 'level': boss_level}
                ))
                
                logger.debug(f"Factory spawned boss level {boss_level}")
                return True
        except Exception as e:
            logger.error(f"Error spawning boss via factory: {e}", exc_info=True)
        
        return False
    
    def _spawn_item_via_factory(self, game_time: float) -> bool:
        """Spawn an item using the factory pattern."""
        try:
            item = self.item_factory.create_random_item(
                self.all_sprites, self.items, self.player
            )
            
            if item:
                # Emit event
                self.event_system.dispatch_event(GameEvent(
                    GameEventType.ITEM_SPAWNED,
                    {'item': item, 'game_time': game_time}
                ))
                
                logger.debug(f"Factory spawned item at game time {game_time:.1f}m")
                return True
        except Exception as e:
            logger.error(f"Error spawning item via factory: {e}", exc_info=True)
        
        return False
    
    # Input event handlers
    def _handle_movement_input(self, event: InputEvent):
        """Handle movement input events."""
        if self.paused or self.game_won:
            return
        
        direction = event.get_data('direction')
        pressed = event.get_data('pressed', True)
        
        # Apply movement to player
        if direction == 'up':
            self.player.speedy = -self.player.speed if pressed else 0
        elif direction == 'down':
            self.player.speedy = self.player.speed if pressed else 0
        elif direction == 'left':
            self.player.speedx = -self.player.speed if pressed else 0
        elif direction == 'right':
            self.player.speedx = self.player.speed if pressed else 0
    
    def _handle_shoot_input(self, event: InputEvent):
        """Handle shooting input events."""
        if self.paused or self.game_won:
            return
        
        pressed = event.get_data('pressed', True)
        continuous = event.get_data('continuous', False)
        
        if pressed:
            self.player.shoot()
    
    def _handle_missile_input(self, event: InputEvent):
        """Handle missile launch input events."""
        if self.paused or self.game_won:
            return
        
        self.player.launch_missile()
    
    def _handle_pause_input(self, event: InputEvent):
        """Handle pause input events using PauseManager."""
        # Use PauseManager for toggle logic
        if not self.pause_manager.toggle_pause():
            # Blocked by cooldown
            return
        
        # Update backward compatibility flag
        self.paused = self.pause_manager.is_paused
        
        # Check for state synchronization issues
        input_manager_paused = self.input_manager.is_paused()
        if self.paused != input_manager_paused:
            logger.warning(f"Pause state mismatch detected: game={self.paused}, input_manager={input_manager_paused}")
            # Force synchronization - trust game state
            if self.paused:
                self.input_manager.pause()
            else:
                self.input_manager.resume()
            logger.info(f"Pause state synchronized: both now set to {self.paused}")
        
        if self.paused:
            logger.info("Game paused via input")
            
            # Reduce audio volume
            self.sound_manager.set_music_volume(
                max(0.0, self.sound_manager.music_volume / 2)
            )
            
            # Pause input processing (only allow pause/system events)
            self.input_manager.pause()
        else:
            logger.info("Game resumed via input")
            
            # Restore audio volume
            self.sound_manager.set_music_volume(
                min(1.0, self.sound_manager.music_volume * 2)
            )
            
            # Resume input processing
            self.input_manager.resume()
        
        self._update_ui_state()
    
    def get_game_time(self):
        """Get pause-aware game time in minutes."""
        # Use PauseManager to calculate game time
        game_time_seconds = self.pause_manager.calculate_game_time(self.game_start_time)
        return game_time_seconds / 60.0  # Convert to minutes
    
    def _validate_input_state(self):
        """Validate input state to recover from macOS screenshot interference."""
        current_time = time.time()
        
        # Only check periodically to avoid performance impact
        if current_time - self.last_input_validation_time < self.input_validation_interval:
            return
            
        self.last_input_validation_time = current_time
        
        # Force validation of input handler state
        try:
            self.input_manager.input_handler.force_key_state_validation()
            logger.debug("Periodic input state validation completed")
        except Exception as e:
            logger.warning(f"Input state validation failed: {e}")
    
    def _handle_quit_input(self, event: InputEvent):
        """Handle quit input events."""
        self.running = False
        logger.debug("Game quit via input")
    
    def _handle_audio_input(self, event: InputEvent):
        """Handle audio control input events."""
        audio_action = event.get_data('audio_action')
        
        if audio_action == 'toggle_music':
            self.sound_manager.toggle_music()
            if self.sound_manager.music_enabled:
                music_path = self.resource_manager.get_music_path('background_music.mp3')
                if music_path:
                    self.sound_manager.play_music('background_music.mp3')
        elif audio_action == 'toggle_sound':
            self.sound_manager.toggle_sound()
        elif audio_action == 'volume_up':
            current_volume = self.sound_manager.sound_volume
            self.sound_manager.set_sound_volume(current_volume + 0.1)
            self.sound_manager.set_music_volume(current_volume + 0.1)
            logger.debug(f"Volume increased to {self.sound_manager.sound_volume:.1f}")
        elif audio_action == 'volume_down':
            current_volume = self.sound_manager.sound_volume
            self.sound_manager.set_sound_volume(current_volume - 0.1)
            self.sound_manager.set_music_volume(current_volume - 0.1)
            logger.debug(f"Volume decreased to {self.sound_manager.sound_volume:.1f}")
    
    def _handle_ui_input(self, event: InputEvent):
        """Handle UI control input events."""
        action = event.get_data('ui_action')
        
        if action == 'change_language':
            current_lang = 'en' if self.ui_manager.current_language == 'zh' else 'zh'
            change_language(current_lang)
            self.ui_manager.current_language = current_lang
            language_name = "English" if current_lang == 'en' else "中文"
            self.ui_manager.add_notification(f"Language changed to {language_name}", "achievement")
            logger.debug(f"Language changed to: {language_name}")
    
    # Game event handlers
    def _handle_player_died(self, event: GameEvent):
        """Handle player death event."""
        logger.info("Player died - triggering game over")
        self.game_over = True
        
        # Play game over sound and fade out music
        if hasattr(self, 'sound_manager'):
            self.sound_manager.play_sound('player_death.wav')
            self.sound_manager.fadeout_music(2000)
    
    def _handle_boss_defeated_event(self, event: GameEvent):
        """Handle boss defeated event."""
        boss_data = event.data
        boss_level = boss_data.get('level', 1)
        
        # Check if this is the final boss
        if self.game_level >= MAX_GAME_LEVEL:
            self.event_system.dispatch_event(GameEvent(
                GameEventType.GAME_WON,
                {'final_score': self.score.value, 'level': self.game_level}
            ))
        else:
            # Level up
            self.event_system.dispatch_event(GameEvent(
                GameEventType.LEVEL_UP,
                {'old_level': self.game_level, 'new_level': self.game_level + 1}
            ))
    
    def _handle_level_up_event(self, event: GameEvent):
        """Handle level up event."""
        level_data = event.data
        old_level = level_data.get('old_level', self.game_level)
        new_level = level_data.get('new_level', self.game_level + 1)
        
        self.game_level = new_level
        
        # Update background for new level
        self.background.set_level(new_level)
        
        # Clear enemies and bullets
        enemies_cleared = len(self.enemies)
        for enemy in self.enemies:
            enemy.kill()
        self.enemies.empty()
        
        for bullet in self.enemy_bullets:
            bullet.kill()
        self.enemy_bullets.empty()
        
        for bullet in self.boss_bullets:
            bullet.kill()
        self.boss_bullets.empty()
        
        # Update spawn intervals
        self.item_spawn_interval = max(15, 30 - self.game_level)
        
        # Reset timers
        self.boss_spawn_timer = time.time()
        self.enemy_spawn_timer = time.time()
        
        logger.info(f"Level up: {old_level} -> {new_level}, cleared {enemies_cleared} enemies")
    
    def _handle_game_won_event(self, event: GameEvent):
        """Handle game won event."""
        game_data = event.data
        final_score = game_data.get('final_score', self.score.value)
        
        self.game_won = True
        logger.info(f"Game won! Final score: {final_score}")
        
        # Show victory screen
        self.ui_manager.show_victory_screen(final_score)
        
        # Play victory sound and fade out music
        self.sound_manager.play_sound('boss_death.wav')
        self.sound_manager.fadeout_music(3000)
    
    def _handle_enemy_spawned(self, event: GameEvent):
        """Handle enemy spawned event."""
        enemy_data = event.data
        enemy = enemy_data.get('enemy')
        level = enemy_data.get('level', 1)
        
        logger.debug(f"Enemy spawned: level {level}")
    
    def _handle_item_collected(self, event: GameEvent):
        """Handle item collected event."""
        item_data = event.data
        item_type = item_data.get('item_type', 'unknown')
        
        # Update UI
        self.ui_manager.show_item_collected(item_type)
        
        # Emit player stats changed event
        self.event_system.dispatch_event(GameEvent(
            GameEventType.PLAYER_STATS_CHANGED,
            {
                'health': self.player.health,
                'bullet_paths': self.player.bullet_paths,
                'bullet_speed': self.player.bullet_speed,
                'speed': self.player.speed,
                'wingmen': len(self.player.wingmen_list)
            }
        ))
    
    # UI event handlers
    def _handle_ui_player_health_changed(self, event: GameEvent):
        """Handle player health changed event for UI updates."""
        health_data = event.data
        self.ui_manager.update_player_info(
            health=health_data.get('health'),
            max_health=health_data.get('max_health', PLAYER_HEALTH)
        )
    
    def _handle_ui_player_stats_changed(self, event: GameEvent):
        """Handle player stats changed event for UI updates."""
        stats_data = event.data
        self.ui_manager.update_player_info(
            health=stats_data.get('health'),
            bullet_paths=stats_data.get('bullet_paths'),
            bullet_speed=stats_data.get('bullet_speed'),
            speed=stats_data.get('speed'),
            wingmen=stats_data.get('wingmen')
        )
    
    def _handle_ui_score_changed(self, event: GameEvent):
        """Handle score changed event for UI updates."""
        score_data = event.data
        new_score = score_data.get('score', self.score.value)
        self.ui_manager.persistent_info['score'] = new_score
    
    def _handle_ui_level_changed(self, event: GameEvent):
        """Handle level changed event for UI updates."""
        level_data = event.data
        new_level = level_data.get('new_level', self.game_level)
        self.ui_manager.update_game_state(level=new_level)
    
    def _handle_ui_boss_spawned(self, event: GameEvent):
        """Handle boss spawned event for UI updates."""
        boss_data = event.data
        boss = boss_data.get('boss')
        level = boss_data.get('level', 1)
        
        if boss:
            self.ui_manager.update_boss_info(
                active=True,
                health=boss.health,
                max_health=boss.max_health,
                level=level,
                mode=getattr(boss, 'shoot_pattern', 'normal')
            )
        
        self.ui_manager.show_boss_appeared(level)
    
    def _handle_ui_boss_defeated(self, event: GameEvent):
        """Handle boss defeated event for UI updates."""
        self.ui_manager.update_boss_info(active=False)
    
    def _update_ui_state(self):
        """Update UI state."""
        game_time = self.get_game_time()
        
        self.ui_manager.update_game_state(
            level=self.game_level,
            paused=self.paused,
            game_time=game_time,
            victory=self.game_won,
            defeat=self.player.health <= 0
        )
        
        self.ui_manager.persistent_info['score'] = self.score.value
        
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
                level=getattr(self.boss, 'level', 1),
                mode=getattr(self.boss, 'shoot_pattern', 'normal')
            )
        else:
            self.ui_manager.update_boss_info(active=False)
    
    def handle_events(self):
        """Handle pygame events using the input management system."""
        pygame_events = pygame.event.get()
        
        # Handle game over state events separately 
        if self.game_over:
            for event in pygame_events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Exit game
                        self.running = False
                    elif event.key == pygame.K_r:
                        # Restart game
                        self._restart_game()
                elif event.type == pygame.QUIT:
                    self.running = False
            return
        
        # Process events through input manager for normal gameplay
        input_events = self.input_manager.update(pygame_events)
        
        # Process game events
        self.event_system.process_events()
    
    def update(self):
        """Update game state."""
        game_time = self.get_game_time()
        
        # Update UI
        self._update_ui_state()
        self.ui_manager.update()
        
        # Update flash effects
        flash_manager.update()
        
        # Note: Periodic input validation disabled due to performance impact
        # Use F1 key to manually reset input state if needed after macOS screenshot
        # self._validate_input_state()
        
        # Check sound system health
        if hasattr(self, '_last_sound_check'):
            if time.time() - self._last_sound_check > 2:
                self._check_sound_system()
                self._last_sound_check = time.time()
        else:
            self._last_sound_check = time.time()
        
        # Skip updates if paused, game won, or game over
        if self.paused or self.game_won or self.game_over:
            return
        
        # Update background
        self.background.update()
        
        # Update sprites
        self.all_sprites.update()
        
        # Enemy spawning logic
        self.target_enemy_count = BASE_ENEMY_COUNT + (self.game_level - 1) // 2
        
        if len(self.enemies) < self.target_enemy_count:
            if time.time() - self.enemy_spawn_timer > 2:
                self._spawn_enemy_via_factory(game_time, self.game_level)
                self.enemy_spawn_timer = time.time()
        
        # Boss spawning logic
        if self.game_level > 1 and time.time() - self.boss_spawn_timer > BOSS_SPAWN_INTERVAL:
            if not self.boss or not self.boss.alive():
                self._spawn_boss_via_factory()
        
        # Item spawning logic
        if time.time() - self.item_spawn_timer > self.item_spawn_interval:
            self._spawn_item_via_factory(game_time)
            self.item_spawn_timer = time.time()
        
        # Handle collisions
        self._handle_collisions(game_time)
        
        # Score-based level up (only for early levels)
        if self.game_level <= 1 and self.score.value // SCORE_THRESHOLD >= self.game_level:
            self.event_system.dispatch_event(GameEvent(
                GameEventType.LEVEL_UP,
                {'old_level': self.game_level, 'new_level': self.game_level + 1}
            ))
            # Process events immediately to ensure level up is handled
            self.event_system.process_events()
        
        # Check game over condition
        if self.player.health <= 0 and not self.game_won and not self.game_over:
            self.event_system.dispatch_event(GameEvent(
                GameEventType.PLAYER_DIED,
                {'final_score': self.score.value, 'level': self.game_level}
            ))
    
    def _handle_collisions(self, game_time: float):
        """Handle collision detection."""
        # Bullet-enemy collisions
        hit_result = check_bullet_enemy_collisions(
            self.enemies, self.bullets, self.all_sprites, self.score,
            self.last_score_checkpoint, SCORE_THRESHOLD, self.items, self.player
        )
        self.last_score_checkpoint = hit_result['score_checkpoint']
        
        if hit_result.get('generated_item'):
            self.ui_manager.show_score_milestone(self.score.value)
        
        # Emit score change event
        self.event_system.dispatch_event(GameEvent(
            GameEventType.SCORE_CHANGED,
            {'score': self.score.value}
        ))
        
        # Missile-enemy collisions
        check_missile_enemy_collisions(self.missiles, self.enemies, self.all_sprites, self.score)
        
        # Item-player collisions
        check_items_player_collisions(self.items, self.player, self.ui_manager, self.sound_manager)
        
        # Enemy-player collisions
        enemy_hit = check_enemy_player_collisions(self.player, self.enemies, self.all_sprites)
        if enemy_hit['was_hit']:
            self.event_system.dispatch_event(GameEvent(
                GameEventType.PLAYER_HEALTH_CHANGED,
                {'health': self.player.health, 'max_health': PLAYER_HEALTH}
            ))
            
            if self.player.health <= 0:
                self.event_system.dispatch_event(GameEvent(
                    GameEventType.PLAYER_DIED,
                    {'final_score': self.score.value, 'level': self.game_level}
                ))
        
        # Enemy bullet-player collisions
        bullet_hit = check_enemy_bullet_player_collisions(self.player, self.enemy_bullets, self.all_sprites)
        if bullet_hit['was_hit']:
            self.event_system.dispatch_event(GameEvent(
                GameEventType.PLAYER_HEALTH_CHANGED,
                {'health': self.player.health, 'max_health': PLAYER_HEALTH}
            ))
            
            if self.player.health <= 0:
                self.event_system.dispatch_event(GameEvent(
                    GameEventType.PLAYER_DIED,
                    {'final_score': self.score.value, 'level': self.game_level}
                ))
        
        # Boss collisions
        if self.boss and self.boss.alive():
            # Bullet-boss collisions
            boss_hit_result = check_bullet_boss_collisions(self.boss, self.bullets, self.all_sprites)
            if boss_hit_result['boss_defeated']:
                self.event_system.dispatch_event(GameEvent(
                    GameEventType.BOSS_DEFEATED,
                    {'boss': self.boss, 'level': getattr(self.boss, 'level', 1)}
                ))
                
                # Clean up boss
                self.boss_defeated = True
                if self.boss:
                    self.boss.kill()
                self.boss_active = False
                self.boss = None
            
            # Boss bullet-player collisions
            boss_bullet_hit = check_boss_bullet_player_collisions(self.player, self.boss_bullets, self.all_sprites)
            if boss_bullet_hit['was_hit']:
                self.event_system.dispatch_event(GameEvent(
                    GameEventType.PLAYER_HEALTH_CHANGED,
                    {'health': self.player.health, 'max_health': PLAYER_HEALTH}
                ))
                
                if self.player.health <= 0:
                    self.event_system.dispatch_event(GameEvent(
                        GameEventType.PLAYER_DIED,
                        {'final_score': self.score.value, 'level': self.game_level}
                    ))
            
            # Missile-boss collisions
            check_missile_enemy_collisions(
                self.missiles, pygame.sprite.GroupSingle(self.boss), 
                self.all_sprites, self.score
            )
            
            # Re-check boss health after missile hits
            if self.boss and self.boss.health <= 0:
                self.event_system.dispatch_event(GameEvent(
                    GameEventType.BOSS_DEFEATED,
                    {'boss': self.boss, 'level': getattr(self.boss, 'level', 1)}
                ))
                
                # Clean up boss
                self.boss_defeated = True
                if self.boss:
                    self.boss.kill()
                self.boss_active = False
                self.boss = None
    
    def _check_sound_system(self):
        """Check and fix sound system if needed."""
        if not self.sound_manager.is_healthy():
            logger.warning("Sound system unhealthy, attempting to fix...")
            self.sound_manager.reinitialize()
        else:
            self.sound_manager.ensure_music_playing()
    
    def render(self):
        """Render the game."""
        # Draw background
        self.background.draw(self.screen)
        
        # Draw sprites
        self.all_sprites.draw(self.screen)
        
        # Draw boss health bar if active
        if self.boss and self.boss.alive():
            self.boss.draw_health_bar(self.screen)
        
        # Draw UI
        self.ui_manager.draw_player_stats()
        self.ui_manager.draw_game_info()
        self.ui_manager.draw_notifications()
        
        # Draw developer info if enabled
        if config_manager.debug.dev_mode:
            fps = self.clock.get_fps()
            player_pos = self.player.rect.center
            enemy_count = len(self.enemies)
            self.ui_manager.draw_dev_info(fps, enemy_count, self.target_enemy_count, player_pos)
            
            # Draw level text next to enemies
            dev_font = self.resource_manager.load_font(None, 18)
            for enemy in self.enemies:
                level_text = f"L{enemy.get_level()}"
                text_surf = dev_font.render(level_text, True, WHITE)
                self.screen.blit(text_surf, (enemy.rect.right + 2, enemy.rect.top))
        
        # Draw special screens
        if self.game_won:
            self.ui_manager.draw_victory_screen(self.score.value, MAX_GAME_LEVEL)
        elif self.game_over or self.player.health <= 0:
            game_time = self.get_game_time()
            self.ui_manager.draw_game_over_screen(self.score.value, self.game_level, game_time)
        
        if self.paused:
            self.ui_manager.draw_pause_screen()
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        logger.info("Starting refactored game loop")
        
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.render()
            
            # Exit if victory achieved and player wants to quit
            if self.game_won:
                continue
        
        logger.info("Game loop ended")
        pygame.quit()
        sys.exit() 