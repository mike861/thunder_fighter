import pygame
import time
from thunder_fighter.constants import WIDTH, HEIGHT, WHITE, YELLOW, RED, GREEN, BLUE, FONT_NAME, FONT_SIZE_SMALL, FONT_SIZE_MEDIUM, FONT_SIZE_LARGE
from thunder_fighter.graphics.effects import Notification, WarningNotification, AchievementNotification
from thunder_fighter.localization import _  # Import the text localization function
import logging
from thunder_fighter.utils.logger import logger
from unittest.mock import MagicMock
from thunder_fighter.utils.config_manager import config_manager

class DummyFont:
    """A dummy font class for use in tests when pygame font isn't available"""
    def __init__(self, *args, **kwargs):
        pass

    def render(self, text, antialias=True, color=(255, 255, 255), background=None):
        # Return a dummy surface with the right methods
        mock_surface = pygame.Surface((1, 1)) if hasattr(pygame, 'Surface') else type('MockSurface', (), {
            'get_rect': lambda self: type('MockRect', (), {
                'center': (0, 0),
                'centerx': 0,
                'centery': 0,
                'width': 1,
                'height': 1,
                'x': 0,
                'y': 0,
                'left': 0,
                'right': 1,
                'top': 0,
                'bottom': 1
            })()
        })()
        return mock_surface

class PlayerUIManager:
    """Manages all player-facing UI interface elements and information display"""
    
    def __init__(self, screen, player, game):
        """
        Initialize UI manager
        
        Args:
            screen: pygame.Surface - Game screen
            player: Player - Player object
            game: Game - Main game object
        """
        self.screen = screen
        self.player = player
        self.game = game
        try:
            self.font_s = pygame.font.Font(None, 24)
            self.font_m = pygame.font.Font(None, 36)
            self.font_l = pygame.font.Font(None, 48)
        except pygame.error:
            # Fallback for test environments where pygame.font is not initialized
            self.font_s = self.font_m = self.font_l = MagicMock()
            self.font_s.render.return_value = MagicMock()
            
        self.font_small = self.font_s # Alias for compatibility
        self.font_medium = self.font_m # Alias for compatibility
        self.font_large = self.font_l # Alias for compatibility
        self.text_color = WHITE
        
        # Health/Boss bar settings
        self.bar_length = 200
        self.bar_height = 20
        self.bar_bg_color = (50, 50, 50)
        self.player_hp_color = (0, 255, 0)
        self.boss_hp_color = (255, 0, 0)

        # Notifications
        self.notifications = []
        self.notification_duration = 2000  # 2 seconds in milliseconds
        
        # Current language
        self.current_language = 'en'
        
        # Temporary notification list
        self.notifications = []
        
        # Persistent game state information display
        self.persistent_info = {}
        
        # Boss status information
        self.boss_info = {
            'active': False,
            'health': 0,
            'max_health': 0,
            'level': 0,
            'mode': 'normal'
        }
        
        # Game state
        self.game_state = {
            'level': 1,
            'paused': False,
            'game_time': 0,
            'victory': False,
            'defeat': False
        }
        
        # Player state
        self.player_info = {
            'health': 100,
            'max_health': 100,
            'bullet_paths': 1,
            'bullet_speed': 7,
            'speed': 5,
            'wingmen': 0
        }
        
        # Recent health/recovery events
        self.recent_hp_changes = []
        
        # Timer for advanced UI animations
        self.animation_timer = time.time()
        
        # Timer for level change animation effect
        self.level_change_timer = 0
        self.level_change_active = False
        
        # Control text blinking effect
        self.blink_timer = 0
        self.show_blink_text = True

    def add_notification(self, text, notification_type="normal"):
        """Add a temporary notification
        
        Args:
            text: Notification text
            notification_type: Notification type, can be "normal", "warning", or "achievement"
        """
        if notification_type == "warning":
            self.notifications.append(WarningNotification(text))
        elif notification_type == "achievement":
            self.notifications.append(AchievementNotification(text))
        else:
            self.notifications.append(Notification(text))
    
    def update_boss_info(self, active, health=None, max_health=None, level=None, mode=None):
        """Update Boss status information
        
        Args:
            active: Whether Boss is alive
            health: Boss current health
            max_health: Boss maximum health
            level: Boss level
            mode: Boss current attack mode
        """
        self.boss_info['active'] = active
        
        if not active:
            return
            
        if health is not None:
            self.boss_info['health'] = health
        if max_health is not None:
            self.boss_info['max_health'] = max_health
        if level is not None:
            self.boss_info['level'] = level
        
        # Check mode changes and display corresponding notifications
        if mode is not None and mode != self.boss_info['mode']:
            old_mode = self.boss_info['mode']
            self.boss_info['mode'] = mode
            
            # Display notifications based on mode changes
            if mode == "aggressive" and old_mode == "normal":
                self.add_notification(_("BOSS_ENTERED_AGGRESSIVE"), "warning")
            elif mode == "final":
                self.add_notification(_("BOSS_ENTERED_FINAL"), "warning")
    
    def update_player_info(self, health=None, max_health=None, bullet_paths=None, bullet_speed=None, speed=None, wingmen=None):
        """Update player status information
        
        Args:
            health: Player current health
            max_health: Player maximum health
            bullet_paths: Player bullet path count
            bullet_speed: Player bullet speed
            speed: Player movement speed
            wingmen: Number of wingmen
        """
        if health is not None:
            self.player_info['health'] = health
        if max_health is not None:
            self.player_info['max_health'] = max_health
        if bullet_paths is not None:
            self.player_info['bullet_paths'] = bullet_paths
        if bullet_speed is not None:
            self.player_info['bullet_speed'] = bullet_speed
        if speed is not None:
            self.player_info['speed'] = speed
        if wingmen is not None:
            self.player_info['wingmen'] = wingmen
    
    def update_game_state(self, level=None, paused=None, game_time=None, victory=None, defeat=None):
        """Update game state
        
        Args:
            level: Current game level
            paused: Whether game is paused
            game_time: Game elapsed time
            victory: Whether game is won
            defeat: Whether game is lost
        """
        # Check level changes
        if level is not None and level != self.game_state['level']:
            self.level_change_active = True
            self.level_change_timer = time.time()
            # self.add_notification(_("ADVANCED_TO_LEVEL", level), "achievement") # This is now handled by level_up or boss_defeated
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
    
    def show_item_collected(self, item_type):
        """Display item collection notification
        
        Args:
            item_type: Type of item collected
        """
        if item_type == 'health':
            self.add_notification(_("HEALTH_RESTORED"), "achievement")
        elif item_type == 'bullet_speed':
            self.add_notification(_("BULLET_SPEED_INCREASED"), "achievement")
        elif item_type == 'bullet_path':
            self.add_notification(_("BULLET_PATHS_INCREASED", self.player_info['bullet_paths']), "achievement")
        elif item_type == 'player_speed':
            self.add_notification(_("MOVEMENT_SPEED_INCREASED"), "achievement")
    
    def show_score_milestone(self, score):
        """Display score milestone notification
        
        Args:
            score: Current score
        """
        self.add_notification(_("SCORE_MILESTONE", score), "achievement")
    
    def show_boss_defeated(self, boss_level, score_reward):
        """Display Boss defeated notification
        
        Args:
            boss_level: Boss level
            score_reward: Score reward gained
        """
        self.add_notification(_("BOSS_DEFEATED", boss_level, score_reward), "achievement")
    
    def show_boss_appeared(self, boss_level):
        """Display Boss appeared notification
        
        Args:
            boss_level: Boss level
        """
        self.add_notification(_("BOSS_APPEARED", boss_level), "warning")

    def show_score_level_up(self, new_level):
        """Display score-based level up notification."""
        self.add_notification(_("SCORE_LEVEL_UP", new_level), "achievement")

    def show_level_up_effects(self, old_level, new_level, enemies_cleared, score_bonus):
        """Display level up effects and information
        
        Args:
            old_level: Previous level
            new_level: New level
            enemies_cleared: Number of enemies cleared
            score_bonus: Score bonus received
        """
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
        """Show victory screen when game is won
        
        Args:
            final_score: Final score achieved
        """
        # Set victory state
        self.game_state['victory'] = True
        
        # Only add victory notifications once
        if not hasattr(self, '_victory_notifications_added'):
            self._victory_notifications_added = True
            # Add victory notifications
            self.add_notification(_("FINAL_BOSS_DEFEATED"), "achievement")
            self.add_notification(_("GAME_COMPLETED"), "achievement")
            
            logger.info(f"Victory screen shown with final score: {final_score}")

    def update(self):
        """Update all UI element states"""
        # Update temporary notifications
        self.notifications = [n for n in self.notifications if n.update()]
        
        # Update blink effect timer
        current_time = time.time()
        if current_time - self.blink_timer > 0.5:  # Switch every 0.5 seconds
            self.blink_timer = current_time
            self.show_blink_text = not self.show_blink_text
        
        # Handle level change animation
        if self.level_change_active:
            if current_time - self.level_change_timer > 3.0:  # Animation lasts 3 seconds
                self.level_change_active = False
                
        # Arrange notification vertical positions to avoid overlap
        self.arrange_notifications()
    
    def arrange_notifications(self):
        """Arrange notifications vertically to avoid overlap"""
        if not self.notifications:
            return
            
        # Group by position type
        top_notifications = []
        center_notifications = []
        bottom_notifications = []
        
        for notification in self.notifications:
            if notification.position == 'top':
                top_notifications.append(notification)
            elif notification.position == 'center':
                center_notifications.append(notification)
            elif notification.position == 'bottom':
                bottom_notifications.append(notification)
        
        # Sort by creation time to display newer messages first
        top_notifications.sort(key=lambda n: n.creation_time, reverse=True)
        center_notifications.sort(key=lambda n: n.creation_time, reverse=True)
        bottom_notifications.sort(key=lambda n: n.creation_time, reverse=True)
        
        # Set top notification positions
        for i, notification in enumerate(top_notifications):
            # Each notification has vertical spacing
            y_position = 80 + i * 40  # Start from top, move down 40 pixels each
            notification.set_y_position(y_position)
        
        # Set center notification positions
        center_y_start = HEIGHT // 2 - (len(center_notifications) * 40) // 2
        for i, notification in enumerate(center_notifications):
            y_position = center_y_start + i * 40
            notification.set_y_position(y_position)
        
        # Set bottom notification positions
        for i, notification in enumerate(bottom_notifications):
            # Arrange from bottom up
            y_position = HEIGHT - 120 - i * 40
            notification.set_y_position(y_position)
    
    def draw_health_bar(self, x, y, width, height, current, maximum, border_color=WHITE, fill_color=GREEN, background_color=(60, 60, 60)):
        """Draw health bar
        
        Args:
            x, y: Position coordinates
            width, height: Width and height
            current: Current value
            maximum: Maximum value
            border_color: Border color
            fill_color: Fill color
            background_color: Background color
        """
        # Draw background
        pygame.draw.rect(self.screen, background_color, (x, y, width, height))
        
        # Calculate fill width
        fill_width = max(0, int(width * current / maximum))
        
        # Draw fill part
        if current > 0:
            # Change color based on health percentage
            if current / maximum < 0.3:
                color = RED  # Red when health is low
            elif current / maximum < 0.6:
                color = YELLOW  # Yellow when health is medium
            else:
                color = fill_color  # Green when health is high
                
            pygame.draw.rect(self.screen, color, (x, y, fill_width, height))
        
        # Draw border
        pygame.draw.rect(self.screen, border_color, (x, y, width, height), 2)
        
        # Display specific value
        value_text = self.font_small.render(f"{current}/{maximum}", True, WHITE)
        text_rect = value_text.get_rect(center=(x + width//2, y + height//2))
        self.screen.blit(value_text, text_rect)
    
    def draw_player_stats(self):
        """Draw detailed player status in top-left corner of screen"""
        x, y = 10, 10
        
        # Draw health bar
        self.draw_health_bar(x, y, 150, 20, self.player_info['health'], self.player_info['max_health'])
        
        # Always display bullet speed
        bullet_speed_text = _("PLAYER_BULLET_SPEED_INFO", self.player_info['bullet_speed'])
        bullet_speed_surf = self.font_small.render(bullet_speed_text, True, WHITE)
        self.screen.blit(bullet_speed_surf, (x, y + 25))

        # Always display movement speed
        speed_text = _("PLAYER_SPEED_INFO", self.player_info['speed'])
        speed_surf = self.font_small.render(speed_text, True, WHITE)
        self.screen.blit(speed_surf, (x, y + 45))

        # Display extra info only in dev mode
        if config_manager.debug.dev_mode:
            # Draw movement speed
            speed_text = _("PLAYER_SPEED_INFO", self.player_info['speed'])
            speed_surf = self.font_small.render(speed_text, True, WHITE)
            self.screen.blit(speed_surf, (x, y + 45))

            # Draw bullet path info
            bullet_path_text = _("PLAYER_BULLET_PATHS_INFO", self.player_info['bullet_paths'])
            bullet_path_surf = self.font_small.render(bullet_path_text, True, WHITE)
            self.screen.blit(bullet_path_surf, (x, y + 65))

            # Draw wingmen information
            wingmen_text = _("PLAYER_WINGMEN_INFO", self.player_info['wingmen'])
            wingmen_surf = self.font_small.render(wingmen_text, True, WHITE)
            self.screen.blit(wingmen_surf, (x, y + 85))

    def draw_player_status(self, x, y):
        # This method seems to be redundant with draw_player_stats, 
        # but we'll keep it for now in case it's used elsewhere.
        # For now, it delegates to the new method.
        self.draw_player_stats()
    
    def draw_notifications(self):
        """Draw all temporary notifications"""
        self.arrange_notifications()
        
        for notification in self.notifications:
            notification.draw(self.screen)

    def draw_boss_status(self):
        """Draws the boss's health bar."""
        if self.game.boss and self.game.boss.alive():
            boss = self.game.boss
            health_percent = boss.health / boss.max_health
            bar_width = self.bar_length * health_percent
            
            # Position the boss bar at the top center
            bar_x = (WIDTH - self.bar_length) / 2
            bar_y = 10 
            
            # Draw the background
            pygame.draw.rect(self.screen, self.bar_bg_color, [bar_x, bar_y, self.bar_length, self.bar_height])
            # Draw the health bar
            pygame.draw.rect(self.screen, self.boss_hp_color, [bar_x, bar_y, bar_width, self.bar_height])
            
            # Draw the text
            boss_health_text = _("BOSS_HEALTH", boss.health, boss.max_health)
            text_surface = self.font_s.render(boss_health_text, True, self.text_color)
            text_rect = text_surface.get_rect(center=(WIDTH / 2, bar_y + self.bar_height / 2))
            self.screen.blit(text_surface, text_rect)

    def draw_game_info(self):
        """Draw game information in top-right corner of screen"""
        x, y = WIDTH - 200, 10
        score_text = _("SCORE", self.persistent_info.get('score', 0))
        level_text = _("LEVEL", self.game_state.get('level', 1))
        time_text = _("TIME", self.game_state.get('game_time', 0))

        score_surf = self.font_small.render(score_text, True, WHITE)
        level_surf = self.font_small.render(level_text, True, WHITE)
        time_surf = self.font_small.render(time_text, True, WHITE)

        self.screen.blit(score_surf, (x, y))
        self.screen.blit(level_surf, (x, y + 25))
        self.screen.blit(time_surf, (x, y + 50))

    def draw_dev_info(self, fps, enemy_count, target_enemy_count, player_pos):
        """Draw developer debug information on the screen."""
        x, y = 10, HEIGHT - 80
        dev_color = (200, 200, 200)  # Light gray

        fps_text = f"FPS: {fps:.2f}"
        enemy_text = f"Enemies: {enemy_count}/{target_enemy_count}"
        player_pos_text = f"Player: ({int(player_pos[0])}, {int(player_pos[1])})"

        fps_surf = self.font_small.render(fps_text, True, dev_color)
        enemy_surf = self.font_small.render(enemy_text, True, dev_color)
        player_pos_surf = self.font_small.render(player_pos_text, True, dev_color)

        self.screen.blit(fps_surf, (x, y))
        self.screen.blit(enemy_surf, (x, y + 20))
        self.screen.blit(player_pos_surf, (x, y + 40))

    def draw_pause_screen(self):
        """Draw pause screen"""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        if not self.game_state['paused']:
            return
            
        # Create semi-transparent overlay
        pause_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pause_overlay.fill((0, 0, 0, 150))  # Semi-transparent black
        self.screen.blit(pause_overlay, (0, 0))
        
        # Draw pause text
        pause_text = self.font_large.render(_("GAME_PAUSED"), True, WHITE)
        text_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        self.screen.blit(pause_text, text_rect)
        
        # Draw tip text
        tip_text = self.font_medium.render(_("RESUME_PROMPT"), True, WHITE)
        tip_rect = tip_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
        self.screen.blit(tip_text, tip_rect)
        
        controls_text = self.font_small.render(_("CONTROLS_INFO"), True, WHITE)
        controls_rect = controls_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        self.screen.blit(controls_text, controls_rect)
    
    def draw_victory_screen(self, final_score, max_level):
        """Draw game victory screen
        
        Args:
            final_score: Final score
            max_level: Maximum level number
        """
        if not self.game_state['victory']:
            return
            
        # Create semi-transparent overlay instead of filling the entire screen
        victory_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        victory_overlay.fill((0, 0, 0, 120))  # Semi-transparent black overlay
        self.screen.blit(victory_overlay, (0, 0))
        
        # Create a victory panel in the center
        panel_width = 400
        panel_height = 300
        panel_x = (WIDTH - panel_width) // 2
        panel_y = (HEIGHT - panel_height) // 2
        
        # Draw victory panel background
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((20, 40, 80, 200))  # Semi-transparent blue panel
        
        # Draw panel border
        pygame.draw.rect(panel_surface, GREEN, (0, 0, panel_width, panel_height), 3)
        
        self.screen.blit(panel_surface, (panel_x, panel_y))
        
        # Draw victory text
        victory_text = self.font_large.render(_("VICTORY"), True, GREEN)
        text_rect = victory_text.get_rect(center=(WIDTH // 2, panel_y + 60))
        self.screen.blit(victory_text, text_rect)
        
        # Draw level cleared information
        level_text = self.font_medium.render(_("LEVEL_CLEARED", max_level), True, WHITE)
        level_rect = level_text.get_rect(center=(WIDTH // 2, panel_y + 120))
        self.screen.blit(level_text, level_rect)
        
        # Draw final score
        score_text = self.font_medium.render(_("FINAL_SCORE", final_score), True, WHITE)
        score_rect = score_text.get_rect(center=(WIDTH // 2, panel_y + 160))
        self.screen.blit(score_text, score_rect)
        
        # Draw survival time
        game_time = self.game_state.get('game_time', 0)
        time_text = self.font_medium.render(_("SURVIVAL_TIME", int(game_time)), True, WHITE)
        time_rect = time_text.get_rect(center=(WIDTH // 2, panel_y + 200))
        self.screen.blit(time_text, time_rect)
        
        # Draw tip text
        if self.show_blink_text:  # Blinking display
            exit_text = self.font_small.render(_("EXIT_PROMPT"), True, YELLOW)
            exit_rect = exit_text.get_rect(center=(WIDTH // 2, panel_y + 250))
            self.screen.blit(exit_text, exit_rect)
    
    def draw_game_over_screen(self, final_score, level_reached, game_time):
        """Draw game over interface
        
        Args:
            final_score: Final score
            level_reached: Level reached
            game_time: Game time (minutes)
        """
        if not self.game_state['defeat']:
            return
            
        # Draw dark red background
        self.screen.fill((40, 10, 10))
        
        # Draw game over text
        gameover_text = self.font_large.render(_("GAME_OVER"), True, RED)
        text_rect = gameover_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
        self.screen.blit(gameover_text, text_rect)
        
        # Draw statistics
        level_text = self.font_medium.render(_("LEVEL_REACHED", level_reached), True, WHITE)
        level_rect = level_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10))
        self.screen.blit(level_text, level_rect)
        
        score_text = self.font_medium.render(_("FINAL_SCORE", final_score), True, WHITE)
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
        self.screen.blit(score_text, score_rect)
        
        time_text = self.font_medium.render(_("SURVIVAL_TIME", int(game_time)), True, WHITE)
        time_rect = time_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70))
        self.screen.blit(time_text, time_rect)
        
        # Draw prompt text
        if self.show_blink_text:  # Blinking display
            exit_text = self.font_small.render(_("EXIT_PROMPT"), True, YELLOW)
            exit_rect = exit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 130))
            self.screen.blit(exit_text, exit_rect)
    
    def draw_level_change_animation(self, level):
        """Draw level change animation
        
        Args:
            level: New level
        """
        if not self.level_change_active:
            return
            
        # Calculate animation duration
        elapsed = time.time() - self.level_change_timer
        if elapsed > 3.0:  # Animation lasts up to 3 seconds
            self.level_change_active = False
            return
            
        # Create semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        # Adjust transparency based on time
        if elapsed < 0.5:  # Fade in
            alpha = int(150 * elapsed / 0.5)
        elif elapsed > 2.5:  # Fade out
            alpha = int(150 * (3.0 - elapsed) / 0.5)
        else:  # Maintain
            alpha = 150
            
        overlay.fill((0, 0, 50, alpha))  # Semi-transparent blue
        self.screen.blit(overlay, (0, 0))
        
        # Draw level change text
        if 0.3 < elapsed < 2.7:  # Display text during this time segment
            level_text = self.font_large.render(_("LEVEL_TEXT", level), True, WHITE)
            text_rect = level_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(level_text, text_rect)
    
    def draw(self, score, level, game_time, enemy_count=None, target_enemy_count=None, max_level=None):
        """Draw all UI elements
        
        Args:
            score: Current score
            level: Game level
            game_time: Game time (minutes)
            enemy_count: Current enemy count
            target_enemy_count: Target enemy count
            max_level: Maximum level number
        """
        # Draw special screen
        if self.game_state['victory']:
            self.draw_victory_screen(score, max_level or level)
            return
            
        if self.game_state['defeat']:
            self.draw_game_over_screen(score, level, game_time)
            return
        
        # Draw top left game information
        self.draw_game_info()
        
        # Draw top right player status
        self.draw_player_status(WIDTH - 200, 10)
        
        # If Boss is active, draw Boss status
        if self.boss_info['active']:
            self.draw_boss_status()
        
        # First update notification arrangement to ensure no overlap
        self.arrange_notifications()
        
        # Draw all notifications
        self.draw_notifications()
        
        # Draw level change animation
        self.draw_level_change_animation(level)
        
        # Draw pause screen
        self.draw_pause_screen() 