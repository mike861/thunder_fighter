import pytest
import pygame
import time
from unittest.mock import MagicMock, patch, call
from thunder_fighter.game import Game

@pytest.fixture
def mock_pygame():
    with patch('thunder_fighter.game.pygame') as mock:
        # Mock display and surface
        mock.display.set_mode.return_value = MagicMock()
        mock.display.set_caption = MagicMock()
        
        # Mock constants
        mock.QUIT = pygame.QUIT
        mock.KEYDOWN = pygame.KEYDOWN
        mock.K_p = pygame.K_p
        mock.K_ESCAPE = pygame.K_ESCAPE
        mock.K_m = pygame.K_m
        mock.K_s = pygame.K_s
        mock.K_PLUS = pygame.K_PLUS
        mock.K_EQUALS = pygame.K_EQUALS
        mock.K_MINUS = pygame.K_MINUS
        
        # Mock clock
        mock.time.Clock.return_value = MagicMock()
        
        # Mock sprite groups
        mock.sprite.Group.return_value = MagicMock()
        
        # Mock font initialization
        mock.font.init.return_value = None
        mock.font.SysFont.return_value = MagicMock()
        mock.font.Font.return_value = MagicMock()
        
        # Mock blend modes
        mock.BLEND_ALPHA_SDL2 = pygame.BLEND_ALPHA_SDL2
        
        yield mock

@pytest.fixture
def mock_time():
    with patch('thunder_fighter.game.time') as mock:
        mock.time.return_value = 0.0
        yield mock

@pytest.fixture
def mock_player():
    with patch('thunder_fighter.game.Player') as mock:
        mock.return_value = MagicMock()
        yield mock

@pytest.fixture
def mock_enemy():
    with patch('thunder_fighter.game.Enemy') as mock:
        mock.return_value = MagicMock()
        mock.return_value.get_level.return_value = 1
        yield mock

@pytest.fixture
def mock_boss():
    with patch('thunder_fighter.game.Boss') as mock:
        mock.return_value = MagicMock()
        yield mock

@pytest.fixture
def mock_sound_manager():
    with patch('thunder_fighter.game.sound_manager') as mock:
        # Set up properties needed for tests
        mock.music_volume = 0.5
        mock.sound_volume = 0.5
        mock.music_enabled = True
        mock.sound_enabled = True
        yield mock

@pytest.fixture
def mock_score():
    with patch('thunder_fighter.game.Score') as mock:
        mock.return_value = MagicMock()
        mock.return_value.value = 0
        yield mock

@pytest.fixture
def mock_collision_checks():
    with patch('thunder_fighter.game.check_bullet_enemy_collisions') as mock_bullet_enemy, \
         patch('thunder_fighter.game.check_bullet_boss_collisions') as mock_bullet_boss, \
         patch('thunder_fighter.game.check_enemy_player_collisions') as mock_enemy_player, \
         patch('thunder_fighter.game.check_boss_bullet_player_collisions') as mock_boss_bullet, \
         patch('thunder_fighter.game.check_enemy_bullet_player_collisions') as mock_enemy_bullet, \
         patch('thunder_fighter.game.check_items_player_collisions') as mock_items_player:
        
        # Configure default return values
        mock_bullet_enemy.return_value = {
            'enemy_hit': False,
            'score_checkpoint': 0,
            'enemy_count': 0,
            'generated_item': False
        }
        
        mock_bullet_boss.return_value = {
            'boss_hit': False,
            'boss_defeated': False,
            'damage': 0
        }
        
        mock_enemy_player.return_value = {
            'was_hit': False,
            'game_over': False,
            'damage': 0
        }
        
        mock_boss_bullet.return_value = {
            'was_hit': False,
            'game_over': False,
            'damage': 0
        }
        
        mock_enemy_bullet.return_value = {
            'was_hit': False,
            'game_over': False,
            'damage': 0
        }
        
        mock_items_player.return_value = {
            'item_collected': False,
            'item_types': []
        }
        
        yield (mock_bullet_enemy, mock_bullet_boss, mock_enemy_player, 
              mock_boss_bullet, mock_enemy_bullet, mock_items_player)

@patch('thunder_fighter.game.create_stars')
def test_game_initialization(mock_create_stars, mock_pygame, mock_time, 
                            mock_player, mock_sound_manager, mock_score):
    """Test that the Game class initializes properly."""
    # Create game instance
    game = Game()
    
    # Check that pygame was initialized
    mock_pygame.init.assert_called_once()
    
    # Check that display was set up
    mock_pygame.display.set_mode.assert_called_once()
    mock_pygame.display.set_caption.assert_called_once()
    
    # Check that clock was created
    mock_pygame.time.Clock.assert_called_once()
    
    # Check that sprite groups were created
    assert mock_pygame.sprite.Group.call_count >= 6  # At least 6 groups
    
    # Check that player was created
    mock_player.assert_called_once()
    
    # Check that score was created
    mock_score.assert_called_once()
    
    # Check that stars were created
    mock_create_stars.assert_called_once()
    
    # Check that fonts were initialized
    assert mock_pygame.font.SysFont.call_count >= 1 or mock_pygame.font.Font.call_count >= 1
    
    # Check that background music was played
    mock_sound_manager.play_background_music.assert_called_once_with('background_music.mp3')
    
    # Check initial game state
    assert game.running is True
    assert game.paused is False
    assert game.game_level == 1
    assert game.game_won is False
    assert game.boss is None
    assert game.boss_active is False

@patch('thunder_fighter.game.pygame.event')
def test_handle_events_quit_game(mock_event, mock_pygame, mock_time, 
                               mock_player, mock_score):
    """Test that quit events are properly handled."""
    # Create a game instance
    game = Game()
    
    # Mock a QUIT event
    mock_event.get.return_value = [
        MagicMock(type=pygame.QUIT)
    ]
    
    # Handle events
    game.handle_events()
    
    # Check that the game is no longer running
    assert game.running is False

@patch('thunder_fighter.game.pygame.event')
def test_handle_events_pause_game(mock_event, mock_pygame, mock_time, 
                                 mock_player, mock_sound_manager, mock_score):
    """Test that pause events are properly handled."""
    # Create a game instance
    game = Game()
    
    # Mock a key press event for pausing (P key)
    mock_event.get.return_value = [
        MagicMock(type=pygame.KEYDOWN, key=pygame.K_p)
    ]
    
    # Handle events
    game.handle_events()
    
    # Check that the game is paused
    assert game.paused is True
    
    # Check that music volume was lowered
    mock_sound_manager.set_music_volume.assert_called_once()
    
    # Handle events again to unpause
    mock_event.get.return_value = [
        MagicMock(type=pygame.KEYDOWN, key=pygame.K_p)
    ]
    game.handle_events()
    
    # Check that game is no longer paused
    assert game.paused is False
    
    # Check that music volume was restored
    assert mock_sound_manager.set_music_volume.call_count == 2

@patch('thunder_fighter.game.pygame.event')
def test_handle_events_escape_key(mock_event, mock_pygame, mock_time, 
                                mock_player, mock_score):
    """Test that escape key properly exits the game."""
    # Create a game instance
    game = Game()
    
    # Mock a key press event for exiting (ESC key)
    mock_event.get.return_value = [
        MagicMock(type=pygame.KEYDOWN, key=pygame.K_ESCAPE)
    ]
    
    # Handle events
    game.handle_events()
    
    # Check that the game is no longer running
    assert game.running is False

@patch('thunder_fighter.game.time.time')
def test_spawn_enemy(mock_time, mock_enemy, mock_pygame, mock_score):
    """Test that enemies are spawned with correct properties."""
    # Create a game instance
    game = Game()
    
    # Get the initial call count to Enemy constructor
    initial_call_count = mock_enemy.call_count
    
    # Configure mock to return a game time value
    mock_time.side_effect = [0, 120]  # First call for game_start_time, second call for current time
    game.game_start_time = 0  # Explicitly set for testing
    
    # Spawn an enemy
    enemy = game.spawn_enemy()
    
    # Check that exactly one more enemy was created
    assert mock_enemy.call_count == initial_call_count + 1
    
    # Check that the enemy was added to the sprite groups
    game.all_sprites.add.assert_any_call(mock_enemy.return_value)
    game.enemies.add.assert_any_call(mock_enemy.return_value)
    
    # Check that enemy level was recorded properly
    # Since the beginning there's already a count for level 1, we need to check if it's at least 1
    assert game.enemy_levels[1] >= 1 