import pygame
import os
import pygame

from thunder_fighter.utils.logger import logger
from thunder_fighter.constants import ASSETS_DIR

class SoundManager:
    """Manage all game sounds and music"""
    
    def __init__(self):
        self._initialized = False
        self._init_pygame_mixer()
        
        # Sound effect volume (0.0 to 1.0)
        self.sound_volume = 0.5
        # Music volume (0.0 to 1.0)
        self.music_volume = 0.3
        
        # Sound effects dictionary
        self.sounds = {}
        self.volume = 0.5  # Default volume at 50%
        self.is_muted = False
        
        self.sound_enabled = True
        self.music_enabled = True
        
        # Load sounds after initialization
        if self._initialized:
            self._load_sounds()
        
    def _init_pygame_mixer(self):
        """Initialize pygame.mixer with proper error handling"""
        self._initialized = False  # Assume failure until success
        try:
            if not pygame.get_init():
                pygame.init()
            if pygame.mixer.get_init():
                self._initialized = True
                return
            
            # Try different initialization parameters for better compatibility
            try:
                pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
                pygame.mixer.init()
            except Exception as init_error:
                # If this fails, re-raise the exception to be caught by outer try-catch
                logger.warning(f"High quality mixer init failed: {init_error}")
                try:
                    # Fallback to lower quality settings
                    pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
                    pygame.mixer.init()
                except Exception as fallback_error:
                    logger.error(f"Fallback mixer init also failed: {fallback_error}")
                    raise fallback_error
            
            # Verify mixer is actually initialized
            if not pygame.mixer.get_init():
                raise pygame.error("Mixer initialization completed but get_init() returns False")
            
            # Set reasonable number of channels for sound effects
            pygame.mixer.set_num_channels(8)
            
            self._initialized = True
            logger.info("Sound manager initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize pygame.mixer: {e}")
            self._initialized = False # Explicitly set to false on error
        
    def _load_sounds(self):
        """Load all sound effects from the assets/sounds directory."""
        sounds_dir = os.path.join(ASSETS_DIR, 'sounds')
        if not os.path.isdir(sounds_dir):
            logger.warning(f"Sounds directory not found: {sounds_dir}")
            return
        
        logger.debug(f"Loading sounds from: {sounds_dir}")
        
        # Define sound effect files
        sound_files = {
            # 'player_shoot': 'player_shoot.wav',  # Commented out as file doesn't exist
            'enemy_explosion': 'enemy_explosion.wav',
            'player_hit': 'player_hit.wav',
            'item_pickup': 'item_pickup.wav',
            'boss_death': 'boss_death.wav',
            'player_death': 'player_death.wav'
        }
        
        # Load sound effects
        for sound_name, file_name in sound_files.items():
            file_path = os.path.join(sounds_dir, file_name)
            if os.path.exists(file_path):
                try:
                    self.sounds[sound_name] = pygame.mixer.Sound(file_path)
                    self.sounds[sound_name].set_volume(self.sound_volume)
                    logger.debug(f"Loaded sound: {sound_name} from {file_path}")
                except Exception as e:
                    logger.error(f"Failed to load sound {sound_name}: {e}")
            else:
                logger.warning(f"Sound file not found: {file_path}")
    
    def play_sound(self, sound_name):
        """Play the specified sound effect"""
        if not self._initialized or not pygame.mixer.get_init():
            logger.warning("Sound manager not ready, attempting to recover.")
            self.reinitialize()
            if not self._initialized:
                logger.error("Recovery failed. Cannot play sound.")
                return

        if not self.sound_enabled:
            return
            
        if sound_name in self.sounds:
            try:
                # Check if mixer is still working
                if not pygame.mixer.get_init():
                    logger.warning("pygame.mixer not initialized, attempting to reinitialize")
                    self._init_pygame_mixer()
                    if not self._initialized:
                        return
                
                # Play the sound
                self.sounds[sound_name].play()
                logger.debug(f"Played sound: {sound_name}")
                
            except Exception as e:
                logger.error(f"Error playing sound {sound_name}: {e}")
                # Try to reinitialize on error
                self.reinitialize()
        else:
            logger.warning(f"Sound not found: {sound_name}")
    
    def play_music(self, music_file: str, loops: int = -1) -> None:
        """
        Play background music.

        Args:
            music_file (str): The name of the music file to play.
            loops (int): The number of times to repeat the music. -1 means loop indefinitely.
        """
        if not self._initialized:
            logger.warning("Sound manager not initialized, cannot play music")
            return
            
        if not self.music_enabled:
            return
            
        music_path = os.path.join(ASSETS_DIR, 'music', music_file)
        if not os.path.exists(music_path):
            logger.warning(f"Music file not found: {music_path}")
            return
        
        # Try to play music with retry mechanism
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Check if mixer is still working
                if not pygame.mixer.get_init():
                    logger.warning("pygame.mixer not initialized, attempting to reinitialize")
                    self._init_pygame_mixer()
                    if not self._initialized:
                        return
                
                # Stop current music if playing
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(loops)
                logger.info(f"Playing background music: {music_file}")
                return  # Success, exit retry loop
                
            except Exception as e:
                logger.error(f"Error playing background music (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    # Try to reinitialize for next attempt
                    self._init_pygame_mixer()
                    import time
                    time.sleep(0.1)  # Brief delay before retry
                else:
                    logger.error("Failed to play background music after all retries")
    
    def stop_music(self):
        """Stop background music"""
        try:
            pygame.mixer.music.stop()
            logger.debug("Background music stopped.")
        except Exception as e:
            logger.error(f"Error stopping music: {e}")
    
    def fadeout_music(self, time_ms):
        """Fade out background music over specified time"""
        try:
            pygame.mixer.music.fadeout(time_ms)
            logger.debug(f"Music fading out over {time_ms}ms")
        except Exception as e:
            logger.error(f"Error fading out music: {e}")
    
    def set_sound_volume(self, volume):
        """Set sound effect volume"""
        self.sound_volume = max(0.0, min(1.0, volume))
        
        # Update volume for all loaded sound effects
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)
            
        logger.debug(f"Sound volume set to: {self.sound_volume}")
    
    def set_music_volume(self, volume):
        """Set background music volume"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
        logger.debug(f"Music volume set to: {self.music_volume}")
    
    def pause_music(self):
        """Pause background music"""
        pygame.mixer.music.pause()
        logger.debug("Music paused.")
    
    def unpause_music(self):
        """Resume background music"""
        pygame.mixer.music.unpause()
        logger.debug("Music resumed.")
    
    def toggle_sound(self):
        """Toggle sound effects on/off"""
        self.sound_enabled = not self.sound_enabled
        logger.info(f"Sound effects {'enabled' if self.sound_enabled else 'disabled'}")
        
        # Sound effects and background music should be independent
        # Do not stop music when disabling sound effects
    
    def toggle_music(self):
        """Toggle background music on/off"""
        self.music_enabled = not self.music_enabled
        logger.info(f"Background music {'enabled' if self.music_enabled else 'disabled'}")
        
        if not self.music_enabled:
            self.stop_music()
        else:
            # Resume playing background music
            self.play_music('background_music.mp3')
    
    def is_healthy(self):
        """Check if the sound system is working properly"""
        if not self._initialized:
            return False
        
        try:
            # Check if pygame.mixer is still initialized
            mixer_init = pygame.mixer.get_init()
            if not mixer_init:
                return False
            
            # Check if we have loaded sounds (allow empty sounds dict during testing)
            # Only fail if sounds should be loaded but aren't
            if hasattr(self, 'sounds') and self.sounds is None:
                return False
            
            # Check if background music should be playing but isn't
            # Only check this if music is enabled AND we have sounds loaded (not in test mode)
            if (self.music_enabled and 
                hasattr(self, 'sounds') and 
                len(self.sounds) > 0 and 
                not pygame.mixer.music.get_busy()):
                logger.warning("Background music should be playing but isn't")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error checking sound system health: {e}")
            return False
    
    def reinitialize(self):
        """Reinitialize the sound system"""
        logger.info("Reinitializing sound system...")
        
        # Stop all current audio
        try:
            pygame.mixer.stop()
            pygame.mixer.music.stop()
        except:
            pass
        
        # Quit and reinitialize mixer
        try:
            pygame.mixer.quit()
        except:
            pass
            
        self._init_pygame_mixer()
        if self._initialized:
            # Clear existing sounds before reloading
            self.sounds.clear()
            self._load_sounds()
            logger.info("Sound system reinitialized successfully")
            
            # Restart background music if it should be playing
            if self.music_enabled:
                self.play_music('background_music.mp3')
        else:
            logger.error("Failed to reinitialize sound system")
    
    def ensure_music_playing(self):
        """Ensure background music is playing if it should be"""
        if not self.music_enabled or not self._initialized:
            return
        
        try:
            # Check if music should be playing but isn't
            if not pygame.mixer.music.get_busy():
                logger.info("Background music stopped unexpectedly, restarting...")
                self.play_music('background_music.mp3')
        except Exception as e:
            logger.error(f"Error ensuring music is playing: {e}")
            # Try to recover
            self.reinitialize()

# Global sound manager instance
sound_manager = SoundManager() 