import pygame
import os
from thunder_fighter.utils.logger import logger

class SoundManager:
    """管理所有游戏音效和音乐"""
    
    def __init__(self):
        # 确保pygame.mixer已初始化
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
                logger.info("Sound system initialized.")
            except pygame.error as e:
                logger.error(f"Failed to initialize sound system: {e}")
                self.sound_enabled = False
                return
                
        self.sound_enabled = True
        self.music_enabled = True
        
        # 音效音量 (0.0 to 1.0)
        self.sound_volume = 0.5
        # 音乐音量 (0.0 to 1.0)
        self.music_volume = 0.3
        
        # 音效字典
        self.sounds = {}
        
        # 加载所有音效
        self._load_sounds()
        
    def _load_sounds(self):
        """加载所有音效文件"""
        if not self.sound_enabled:
            return
            
        # 音效目录 (相对于项目根目录)
        sound_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'sounds')
        
        # 确保目录存在
        if not os.path.exists(sound_dir):
            try:
                os.makedirs(sound_dir)
                logger.info(f"Created sound directory: {sound_dir}")
            except OSError as e:
                logger.error(f"Failed to create sound directory: {e}")
                return
        
        # 定义音效文件
        sound_files = {
            'player_shoot': 'player_shoot.wav',
            'player_hit': 'player_hit.wav',
            'player_death': 'player_death.wav',
            'enemy_explosion': 'enemy_explosion.wav',
            'boss_death': 'boss_death.wav',
            'item_pickup': 'item_pickup.wav'
        }
        
        # 加载音效
        for key, filename in sound_files.items():
            file_path = os.path.join(sound_dir, filename)
            try:
                if os.path.exists(file_path):
                    self.sounds[key] = pygame.mixer.Sound(file_path)
                    self.sounds[key].set_volume(self.sound_volume)
                    logger.debug(f"Loaded sound: {key} from {file_path}")
                else:
                    logger.warning(f"Sound file not found: {file_path}")
            except pygame.error as e:
                logger.error(f"Failed to load sound '{key}': {e}")
    
    def play_sound(self, sound_key):
        """播放指定音效"""
        if not self.sound_enabled or sound_key not in self.sounds:
            return
            
        try:
            self.sounds[sound_key].play()
        except pygame.error as e:
            logger.error(f"Error playing sound '{sound_key}': {e}")
    
    def play_background_music(self, music_file):
        """播放背景音乐"""
        if not self.sound_enabled or not self.music_enabled:
            return
            
        # 音乐文件路径
        music_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'music')
        music_path = os.path.join(music_dir, music_file)
        
        # 检查文件是否存在
        if not os.path.exists(music_path):
            logger.warning(f"Music file not found: {music_path}")
            return
            
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1)  # -1表示循环播放
            logger.info(f"Playing background music: {music_file}")
        except pygame.error as e:
            logger.error(f"Failed to play background music: {e}")
    
    def stop_music(self):
        """停止背景音乐"""
        if not self.sound_enabled or not pygame.mixer.get_init():
            return
            
        try:
            pygame.mixer.music.stop()
            logger.debug("Background music stopped")
        except pygame.error as e:
            logger.error(f"Error stopping music: {e}")
    
    def set_sound_volume(self, volume):
        """设置音效音量"""
        self.sound_volume = max(0.0, min(1.0, volume))
        
        # 更新所有已加载音效的音量
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)
            
        logger.debug(f"Sound volume set to {self.sound_volume}")
    
    def set_music_volume(self, volume):
        """设置背景音乐音量"""
        if not self.sound_enabled:
            return
            
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
        logger.debug(f"Music volume set to {self.music_volume}")
    
    def toggle_sound(self):
        """切换音效开关"""
        if not pygame.mixer.get_init():
            return
            
        self.sound_enabled = not self.sound_enabled
        logger.debug(f"Sound {'enabled' if self.sound_enabled else 'disabled'}")
        
        # 如果关闭音效，同时也停止背景音乐
        if not self.sound_enabled:
            self.stop_music()
    
    def toggle_music(self):
        """切换背景音乐开关"""
        if not pygame.mixer.get_init():
            return
            
        self.music_enabled = not self.music_enabled
        
        if not self.music_enabled:
            self.stop_music()
        else:
            # 重新播放背景音乐
            logger.deubg(f"Music {'enabled' if self.music_enabled else 'disabled'}")

# 全局音效管理器实例
sound_manager = SoundManager() 