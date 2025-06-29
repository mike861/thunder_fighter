"""
Refactored UI Manager

A facade class that coordinates all UI components following the single responsibility principle.
This replaces the monolithic UIManager with a modular approach.
"""

import pygame
from thunder_fighter.constants import WHITE
from thunder_fighter.localization import _
from thunder_fighter.utils.logger import logger
from thunder_fighter.graphics.ui import (
    HealthBarComponent,
    NotificationManager,
    GameInfoDisplay,
    PlayerStatsDisplay,
    BossStatusDisplay,
    ScreenOverlayManager,
    DevInfoDisplay
)


class UIManager:
    """
    Facade class for managing all UI components.
    
    This class delegates responsibilities to specialized components,
    maintaining a clean and modular architecture.
    """
    
    def __init__(self, screen, player, game):
        """
        Initialize the UI manager with all its components.
        
        Args:
            screen: pygame.Surface - Game screen
            player: Player - Player object
            game: Game - Main game object
        """
        self.screen = screen
        self.player = player
        self.game = game
        
        # Initialize fonts
        try:
            self.font_small = pygame.font.Font(None, 24)
            self.font_medium = pygame.font.Font(None, 36)
            self.font_large = pygame.font.Font(None, 48)
        except pygame.error:
            # Fallback for test environments
            from unittest.mock import MagicMock
            self.font_small = self.font_medium = self.font_large = MagicMock()
            self.font_small.render.return_value = MagicMock()
            
        # Create font dictionary for components
        fonts = {
            'small': self.font_small,
            'medium': self.font_medium,
            'large': self.font_large
        }
        
        # Initialize UI components
        self.notification_manager = NotificationManager(screen)
        self.game_info_display = GameInfoDisplay(screen, self.font_small)
        self.player_stats_display = PlayerStatsDisplay(screen, self.font_small)
        self.boss_status_display = BossStatusDisplay(screen, self.font_small)
        self.screen_overlay_manager = ScreenOverlayManager(screen, fonts)
        self.dev_info_display = DevInfoDisplay(screen, self.font_small)
        
        # Game state tracking
        self.game_state = {
            'level': 1,
            'paused': False,
            'game_time': 0,
            'victory': False,
            'defeat': False
        }
        
        # Persistent info for display
        self.persistent_info = {}
        
        # Current language
        self.current_language = 'en'
        
        logger.info("Refactored UIManager initialized with modular components")
        
    # Delegating methods to NotificationManager
    def add_notification(self, text, notification_type="normal"):
        """Add a notification."""
        self.notification_manager.add(text, notification_type)
        
    def show_item_collected(self, item_type):
        """Display item collection notification."""
        if item_type == 'health':
            self.add_notification(_("HEALTH_RESTORED"), "achievement")
        elif item_type == 'bullet_speed':
            self.add_notification(_("BULLET_SPEED_INCREASED"), "achievement")
        elif item_type == 'bullet_path':
            bullet_paths = self.player_stats_display.player_info['bullet_paths']
            self.add_notification(_("BULLET_PATHS_INCREASED", bullet_paths), "achievement")
        elif item_type == 'player_speed':
            self.add_notification(_("MOVEMENT_SPEED_INCREASED"), "achievement")
            
    def show_score_milestone(self, score):
        """Display score milestone notification."""
        self.add_notification(_("SCORE_MILESTONE", score), "achievement")
        
    def show_boss_defeated(self, boss_level, score_reward):
        """Display Boss defeated notification."""
        self.add_notification(_("BOSS_DEFEATED", boss_level, score_reward), "achievement")
        
    def show_boss_appeared(self, boss_level):
        """Display Boss appeared notification."""
        self.add_notification(_("BOSS_APPEARED", boss_level), "warning")
        
    def show_score_level_up(self, new_level):
        """Display score-based level up notification."""
        self.add_notification(_("SCORE_LEVEL_UP", new_level), "achievement")
        
    def show_level_up_effects(self, old_level, new_level, enemies_cleared, score_bonus):
        """Display level up effects and information."""
        # Add level up notification
        level_up_text = _("LEVEL_UP", old_level, new_level)
        self.add_notification(level_up_text, "achievement")
        
        # Add cleared enemies notification
        if enemies_cleared > 0:
            cleared_text = _("ENEMIES_CLEARED", enemies_cleared)
            self.add_notification(cleared_text, "normal")
        
        # Add score bonus notification
        if score_bonus > 0:
            bonus_text = _("BOSS_BONUS", score_bonus)
            self.add_notification(bonus_text, "achievement")
        
        # Show stage complete notification
        stage_text = _("STAGE_COMPLETE")
        self.add_notification(stage_text, "achievement")
        
        logger.info(f"Level up effects shown: {old_level} → {new_level}, cleared {enemies_cleared} enemies, bonus {score_bonus}")
        
    def show_victory_screen(self, final_score):
        """Show victory screen when game is won."""
        # Set victory state
        self.game_state['victory'] = True
        
        # Only add victory notifications once
        if not hasattr(self, '_victory_notifications_added'):
            self._victory_notifications_added = True
            # Add victory notifications
            self.add_notification(_("FINAL_BOSS_DEFEATED"), "achievement")
            self.add_notification(_("GAME_COMPLETED"), "achievement")
            
            logger.info(f"Victory screen shown with final score: {final_score}")
            
    # Delegating methods to BossStatusDisplay
    def update_boss_info(self, active, health=None, max_health=None, level=None, mode=None):
        """Update Boss status information."""
        old_mode = self.boss_status_display.boss_info.get('mode', 'normal')
        self.boss_status_display.update_info(active, health, max_health, level, mode)
        
        # Check mode changes and display notifications
        if mode is not None and mode != old_mode:
            if mode == "aggressive" and old_mode == "normal":
                self.add_notification(_("BOSS_ENTERED_AGGRESSIVE"), "warning")
            elif mode == "final":
                self.add_notification(_("BOSS_ENTERED_FINAL"), "warning")
                
    # Delegating methods to PlayerStatsDisplay
    def update_player_info(self, health=None, max_health=None, bullet_paths=None, 
                          bullet_speed=None, speed=None, wingmen=None):
        """Update player status information."""
        self.player_stats_display.update_info(
            health, max_health, bullet_paths, bullet_speed, speed, wingmen
        )
        
    # Game state management
    def update_game_state(self, level=None, paused=None, game_time=None, victory=None, defeat=None):
        """Update game state."""
        # Check level changes
        if level is not None and level != self.game_state['level']:
            self.screen_overlay_manager.start_level_change_animation(level)
            self.game_state['level'] = level
        
        if paused is not None:
            self.game_state['paused'] = paused
        if game_time is not None:
            self.game_state['game_time'] = game_time
        if victory is not None:
            if victory and not self.game_state['victory']:
                self.add_notification(_("VICTORY"), "achievement")
            self.game_state['victory'] = victory
        if defeat is not None:
            if defeat and not self.game_state['defeat']:
                self.add_notification(_("GAME_OVER"), "warning")
            self.game_state['defeat'] = defeat
            
    def update(self):
        """Update all UI components."""
        self.notification_manager.update()
        self.screen_overlay_manager.update()
        
    def reset_game_state(self):
        """Reset game state to initial values."""
        self.game_state = {
            'level': 1,
            'paused': False,
            'game_time': 0,
            'victory': False,
            'defeat': False
        }
        self.persistent_info = {}
        
        # Reset component states
        self.notification_manager.clear_all()
        
        # Reset player and boss info displays
        if hasattr(self, 'player_stats_display'):
            self.player_stats_display.reset()
        if hasattr(self, 'boss_status_display'):
            self.boss_status_display.reset()
        
    def draw(self, score, level, game_time, enemy_count=None, target_enemy_count=None, max_level=None):
        """
        Draw all UI elements.
        
        Args:
            score: Current score
            level: Game level
            game_time: Game time (seconds)
            enemy_count: Current enemy count
            target_enemy_count: Target enemy count
            max_level: Maximum level number
        """
        # Update persistent info
        self.persistent_info['score'] = score
        
        # Draw special screens if active
        if self.game_state['victory']:
            self.draw_victory_screen(score, max_level or level)
            return
            
        if self.game_state['defeat']:
            self.draw_game_over_screen(score, level, game_time)
            return
        
        # Draw normal game UI
        self.game_info_display.draw(score, level, game_time)
        self.player_stats_display.draw()
        self.boss_status_display.draw()
        self.notification_manager.draw()
        
        # Draw developer info if enabled
        if enemy_count is not None and self.player:
            player_pos = (self.player.rect.centerx, self.player.rect.centery)
            fps = self.game.clock.get_fps() if hasattr(self.game, 'clock') else 0
            self.dev_info_display.draw(fps, enemy_count, target_enemy_count or 0, player_pos)
        
        # Draw overlays
        self.screen_overlay_manager.draw_level_change_animation()
        self.screen_overlay_manager.draw_pause_screen(self.game_state['paused'])
        
    # Convenience methods that delegate to components
    def draw_health_bar(self, x, y, width, height, current, maximum, 
                       border_color=WHITE, fill_color=(0, 255, 0), background_color=(60, 60, 60)):
        """Draw a health bar (delegates to HealthBarComponent)."""
        health_bar = HealthBarComponent(self.screen, self.font_small)
        health_bar.draw(x, y, width, height, current, maximum, 
                       border_color, fill_color, background_color)
        
    def draw_player_stats(self):
        """Draw player stats (delegates to PlayerStatsDisplay)."""
        self.player_stats_display.draw()
        
    def draw_boss_status(self):
        """Draw boss status (delegates to BossStatusDisplay)."""
        self.boss_status_display.draw()
        
    def draw_victory_screen(self, final_score, max_level):
        """Draw victory screen (delegates to ScreenOverlayManager)."""
        self.screen_overlay_manager.draw_victory_screen(
            final_score, max_level, self.game_state['game_time']
        )
        
    def draw_game_over_screen(self, final_score, level_reached, game_time):
        """Draw game over screen (delegates to ScreenOverlayManager)."""
        self.screen_overlay_manager.draw_game_over_screen(
            final_score, level_reached, game_time
        )
        
    def draw_pause_screen(self):
        """Draw pause screen (delegates to ScreenOverlayManager)."""
        self.screen_overlay_manager.draw_pause_screen(self.game_state['paused'])
        
    def draw_game_info(self):
        """Draw game information (delegates to GameInfoDisplay)."""
        score = self.persistent_info.get('score', 0)
        level = self.game_state.get('level', 1)
        game_time = self.game_state.get('game_time', 0)
        self.game_info_display.draw(score, level, game_time)
        
    def draw_notifications(self):
        """Draw notifications (delegates to NotificationManager)."""
        self.notification_manager.draw()
        
    def draw_dev_info(self, fps, enemy_count, target_enemy_count, player_pos):
        """Draw developer info (delegates to DevInfoDisplay)."""
        self.dev_info_display.draw(fps, enemy_count, target_enemy_count, player_pos)
        
    # Backwards compatibility
    @property
    def notifications(self):
        """Get current notifications (for backwards compatibility)."""
        return self.notification_manager.notifications
        
    @notifications.setter
    def notifications(self, value):
        """Set notifications (for backwards compatibility)."""
        self.notification_manager.notifications = value
        
    @property
    def boss_info(self):
        """Get boss info (for backwards compatibility)."""
        return self.boss_status_display.boss_info
        
    @property
    def player_info(self):
        """Get player info (for backwards compatibility)."""
        return self.player_stats_display.player_info 