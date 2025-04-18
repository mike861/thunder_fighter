import pytest
import pygame
import random
from unittest.mock import MagicMock, patch, call
from thunder_fighter.utils.collisions import (
    check_bullet_enemy_collisions,
    check_bullet_boss_collisions,
    check_enemy_player_collisions,
    check_items_player_collisions
)
from thunder_fighter.sprites.enemy import Enemy
from thunder_fighter.sprites.bullets import Bullet
from thunder_fighter.sprites.boss import Boss
from thunder_fighter.utils.score import Score

# Fixtures to create mock sprites
@pytest.fixture
def mock_enemy():
    enemy = MagicMock(spec=Enemy)
    enemy.rect = pygame.Rect(50, 50, 30, 30)
    enemy.level = 1
    # Mock the alive() method, needed if groupcollide removes the sprite
    enemy.alive.return_value = True
    return enemy

@pytest.fixture
def mock_bullet():
    bullet = MagicMock(spec=Bullet)
    bullet.rect = pygame.Rect(55, 55, 5, 10)
    return bullet

@pytest.fixture
def mock_groups():
    # Use MagicMock instead of real pygame.sprite.Group
    enemies = MagicMock()
    bullets = MagicMock()
    all_sprites = MagicMock()
    items_group = MagicMock()
    return enemies, bullets, all_sprites, items_group

@pytest.fixture
def mock_score():
    score = MagicMock(spec=Score)
    score.value = 0
    score.update = MagicMock()
    return score

# Fixture for boss
@pytest.fixture
def mock_boss():
    boss = MagicMock(spec=Boss)
    boss.rect = pygame.Rect(200, 100, 100, 100)
    boss.health = 100
    boss.damage_flash = 0
    return boss

# Test cases for check_bullet_enemy_collisions
@patch('pygame.sprite.groupcollide')
@patch('thunder_fighter.utils.collisions.Explosion')
@patch('thunder_fighter.sprites.items.create_random_item')
def test_bullet_hits_enemy_no_item(mock_create_item, mock_explosion, mock_groupcollide,
                                    mock_enemy, mock_bullet, mock_groups, mock_score):
    """Test case where a bullet hits an enemy, but score is not enough for an item."""
    enemies, bullets, all_sprites, items_group = mock_groups
    
    # Simulate groupcollide finding one hit
    mock_groupcollide.return_value = {mock_enemy: [mock_bullet]}

    last_score_checkpoint = 0
    score_threshold = 200

    result = check_bullet_enemy_collisions(
        enemies, bullets, all_sprites, mock_score,
        last_score_checkpoint, score_threshold, items_group
    )

    # Assertions
    mock_groupcollide.assert_called_once_with(enemies, bullets, True, True)
    mock_score.update.assert_called_once_with(10 + mock_enemy.level * 2) # 10 + 1*2 = 12
    mock_explosion.assert_called_once_with(mock_enemy.rect.center, 40)
    all_sprites.add.assert_called_with(mock_explosion.return_value) # Check if explosion was added
    mock_create_item.assert_not_called() # Item should not be created

    assert result['enemy_hit'] is True
    assert result['enemy_count'] == 1
    assert result['generated_item'] is False
    assert result['score_checkpoint'] == last_score_checkpoint # Checkpoint remains the same

@patch('pygame.sprite.groupcollide')
@patch('thunder_fighter.utils.collisions.Explosion')
@patch('thunder_fighter.sprites.items.create_random_item')
@patch('thunder_fighter.utils.collisions.logger') # Patch logger if needed
def test_bullet_hits_enemy_triggers_item(mock_logger, mock_create_item, mock_explosion, mock_groupcollide,
                                           mock_enemy, mock_bullet, mock_groups, mock_score):
    """Test case where a bullet hits an enemy, and the score reaches the threshold for an item."""
    enemies, bullets, all_sprites, items_group = mock_groups
    
    # Simulate groupcollide finding one hit
    mock_groupcollide.return_value = {mock_enemy: [mock_bullet]}

    # Set initial score and checkpoint
    mock_score.value = 190
    last_score_checkpoint = 0
    score_threshold = 200

    # Mock score update to reflect the change
    def score_side_effect(value):
        mock_score.value += value
    mock_score.update.side_effect = score_side_effect

    result = check_bullet_enemy_collisions(
        enemies, bullets, all_sprites, mock_score,
        last_score_checkpoint, score_threshold, items_group
    )

    # Assertions
    mock_groupcollide.assert_called_once_with(enemies, bullets, True, True)
    expected_score_increase = 10 + mock_enemy.level * 2 # 12
    mock_score.update.assert_called_once_with(expected_score_increase)
    assert mock_score.value == 190 + expected_score_increase # 202

    mock_explosion.assert_called_once_with(mock_enemy.rect.center, 40)
    all_sprites.add.assert_called_with(mock_explosion.return_value)

    # Assert item creation
    expected_game_time = min(10, (mock_score.value // score_threshold) // 2) # 202 // 200 = 1, 1 // 2 = 0.5 -> min(10, 0) = 0
    mock_create_item.assert_called_once_with(expected_game_time, all_sprites, items_group)

    assert result['enemy_hit'] is True
    assert result['enemy_count'] == 1
    assert result['generated_item'] is True
    assert result['score_checkpoint'] == 1 # Checkpoint should be updated to 1 (202 // 200)

@patch('pygame.sprite.groupcollide')
@patch('thunder_fighter.utils.collisions.Explosion')
@patch('thunder_fighter.sprites.items.create_random_item')
def test_no_collision(mock_create_item, mock_explosion, mock_groupcollide,
                      mock_groups, mock_score):
    """Test case where no collision occurs."""
    enemies, bullets, all_sprites, items_group = mock_groups
    last_score_checkpoint = 0
    score_threshold = 200

    # Simulate groupcollide finding no hits
    mock_groupcollide.return_value = {}

    result = check_bullet_enemy_collisions(
        enemies, bullets, all_sprites, mock_score,
        last_score_checkpoint, score_threshold, items_group
    )

    # Assertions
    mock_groupcollide.assert_called_once_with(enemies, bullets, True, True)
    mock_score.update.assert_not_called()
    mock_explosion.assert_not_called()
    mock_create_item.assert_not_called()

    assert result['enemy_hit'] is False
    assert result['enemy_count'] == 0
    assert result['generated_item'] is False
    assert result['score_checkpoint'] == last_score_checkpoint

@patch('pygame.sprite.groupcollide', side_effect=Exception("Test Exception"))
@patch('thunder_fighter.utils.collisions.logger')
def test_collision_check_exception(mock_logger, mock_groupcollide,
                                   mock_groups, mock_score):
    """Test exception handling in collision check."""
    enemies, bullets, all_sprites, items_group = mock_groups
    last_score_checkpoint = 0
    score_threshold = 200

    result = check_bullet_enemy_collisions(
        enemies, bullets, all_sprites, mock_score,
        last_score_checkpoint, score_threshold, items_group
    )

    # Assertions
    mock_groupcollide.assert_called_once_with(enemies, bullets, True, True)
    mock_logger.error.assert_called_once()
    assert "Error in bullet-enemy collision check" in mock_logger.error.call_args[0][0]

    assert result['enemy_hit'] is False
    assert result['enemy_count'] == 0
    assert result['generated_item'] is False
    assert result['score_checkpoint'] == last_score_checkpoint

# Tests for check_bullet_boss_collisions
@patch('pygame.sprite.spritecollide')
@patch('pygame.sprite.collide_mask')
@patch('thunder_fighter.utils.collisions.Explosion')
@patch('random.randint')
def test_bullet_hits_boss_not_defeated(mock_randint, mock_explosion, mock_collide_mask, 
                                       mock_spritecollide, mock_boss, mock_bullet, mock_groups):
    """Test where bullets hit boss but don't defeat it."""
    _, bullets, all_sprites, _ = mock_groups
    
    # Configure mocks
    mock_spritecollide.return_value = [mock_bullet]  # One bullet hit
    
    # 模拟damage方法返回False（未被击败）
    mock_boss.damage.return_value = False
    
    result = check_bullet_boss_collisions(mock_boss, bullets, all_sprites)
    
    # Assertions
    mock_spritecollide.assert_called_once_with(mock_boss, bullets, True, pygame.sprite.collide_mask)
    mock_boss.damage.assert_called_with(10)  # 应该调用damage(10)
    mock_explosion.assert_called_once_with(mock_bullet.rect.center, 20)
    all_sprites.add.assert_called_with(mock_explosion.return_value)
    
    # Check result dict
    assert result['boss_hit'] is True
    assert result['boss_defeated'] is False
    assert result['damage'] == 10

@patch('pygame.sprite.spritecollide')
@patch('pygame.sprite.collide_mask')
@patch('thunder_fighter.utils.collisions.Explosion')
@patch('random.randint')
def test_bullet_defeats_boss(mock_randint, mock_explosion, mock_collide_mask, 
                             mock_spritecollide, mock_boss, mock_bullet, mock_groups):
    """Test where bullets defeat the boss."""
    _, bullets, all_sprites, _ = mock_groups
    
    # Configure mocks
    mock_spritecollide.return_value = [mock_bullet]  # One bullet hit
    
    # 模拟damage方法返回True（被击败）
    mock_boss.damage.return_value = True
    
    # Mock random positions for explosions - need 20 values (10 x-positions and 10 y-positions)
    random_positions = []
    for _ in range(10):
        random_positions.append(random.randint(100, 300))  # x position
        random_positions.append(random.randint(50, 200))   # y position
    mock_randint.side_effect = random_positions
    
    result = check_bullet_boss_collisions(mock_boss, bullets, all_sprites)
    
    # Assertions
    mock_spritecollide.assert_called_once_with(mock_boss, bullets, True, pygame.sprite.collide_mask)
    mock_boss.damage.assert_called_with(10)  # 应该调用damage(10)
    
    # Check result dict
    assert result['boss_hit'] is True
    assert result['boss_defeated'] is True
    assert result['damage'] == 10
    
    # Should create multiple explosions for boss defeat
    assert mock_explosion.call_count >= 2  # At least 2 explosions created (一个子弹击中爆炸，一个Boss被击败爆炸)
    assert all_sprites.add.call_count >= 2  # At least 2 sprites added

@patch('pygame.sprite.spritecollide')
def test_no_boss_bullet_collision(mock_spritecollide, mock_groups):
    """Test where no bullets hit the boss."""
    _, bullets, all_sprites, _ = mock_groups
    
    # Configure mocks
    mock_spritecollide.return_value = []  # No bullets hit
    
    result = check_bullet_boss_collisions(None, bullets, all_sprites)
    
    # Assertions
    mock_spritecollide.assert_not_called()  # Should not call spritecollide if boss is None
    
    # Check result dict - should indicate no hit when boss is None
    assert result['boss_hit'] is False
    assert result['boss_defeated'] is False
    assert result['damage'] == 0

# Tests for check_enemy_player_collisions
@pytest.fixture
def mock_player():
    player = MagicMock()
    player.rect = pygame.Rect(300, 400, 50, 50)
    player.health = 100
    return player

@patch('pygame.sprite.spritecollide')
@patch('thunder_fighter.utils.collisions.Explosion')
def test_enemy_hits_player(mock_explosion, mock_spritecollide, 
                           mock_player, mock_enemy, mock_groups):
    """Test where an enemy collides with the player."""
    enemies, _, all_sprites, _ = mock_groups
    
    # Configure mocks
    mock_spritecollide.return_value = [mock_enemy]  # One enemy hit
    
    result = check_enemy_player_collisions(mock_player, enemies, all_sprites)
    
    # Assertions
    mock_spritecollide.assert_called_once_with(mock_player, enemies, True)
    assert mock_player.health == 100 - (15 + mock_enemy.level * 1)  # Base damage 15 + level
    mock_explosion.assert_called_once_with(mock_enemy.rect.center, 40)
    all_sprites.add.assert_called_with(mock_explosion.return_value)
    
    # Check result dict
    assert result['was_hit'] is True
    assert result['game_over'] is False
    assert result['damage'] == 15 + mock_enemy.level * 1

@patch('pygame.sprite.spritecollide')
@patch('thunder_fighter.utils.collisions.Explosion')
def test_enemy_hits_player_game_over(mock_explosion, mock_spritecollide, 
                                     mock_player, mock_enemy, mock_groups):
    """Test where an enemy collision kills the player."""
    enemies, _, all_sprites, _ = mock_groups
    
    # Configure mocks
    mock_spritecollide.return_value = [mock_enemy]  # One enemy hit
    mock_player.health = 10  # Player has low health
    
    result = check_enemy_player_collisions(mock_player, enemies, all_sprites)
    
    # Assertions
    mock_spritecollide.assert_called_once_with(mock_player, enemies, True)
    assert mock_player.health <= 0  # Health should be reduced to 0 or below
    mock_explosion.assert_called_once_with(mock_enemy.rect.center, 40)
    all_sprites.add.assert_called_with(mock_explosion.return_value)
    
    # Check result dict
    assert result['was_hit'] is True
    assert result['game_over'] is True
    assert result['damage'] == 15 + mock_enemy.level * 1

@patch('pygame.sprite.spritecollide')
def test_no_enemy_player_collision(mock_spritecollide, mock_player, mock_groups):
    """Test where no enemies hit the player."""
    enemies, _, all_sprites, _ = mock_groups
    
    # Configure mocks
    mock_spritecollide.return_value = []  # No enemies hit
    
    result = check_enemy_player_collisions(mock_player, enemies, all_sprites)
    
    # Assertions
    mock_spritecollide.assert_called_once_with(mock_player, enemies, True)
    assert mock_player.health == 100  # Health should remain unchanged
    
    # Check result dict
    assert result['was_hit'] is False
    assert result['game_over'] is False
    assert result['damage'] == 0

# Tests for check_items_player_collisions
@pytest.fixture
def mock_health_item():
    item = MagicMock()
    item.rect = pygame.Rect(300, 400, 30, 30)
    item.type = 'health'
    return item

@pytest.fixture
def mock_bullet_speed_item():
    item = MagicMock()
    item.rect = pygame.Rect(300, 400, 30, 30)
    item.type = 'bullet_speed'
    item.speed_increase = 2
    return item

@patch('pygame.sprite.spritecollide')
def test_player_collects_health_item(mock_spritecollide, mock_player, mock_health_item, mock_groups):
    """Test where player collects a health item."""
    _, _, _, items = mock_groups
    
    # Configure mocks
    mock_spritecollide.return_value = [mock_health_item]  # One health item
    mock_player.health = 60  # Player has less than max health
    
    result = check_items_player_collisions(mock_player, items, mock_groups[2])
    
    # Assertions
    mock_spritecollide.assert_called_once_with(mock_player, items, True)
    assert mock_player.health == 85  # Health should increase by 25
    
    # Check result dict
    assert result['item_collected'] is True
    assert 'health' in result['item_types']

@patch('pygame.sprite.spritecollide')
def test_player_collects_bullet_speed_item(mock_spritecollide, mock_player, 
                                          mock_bullet_speed_item, mock_groups):
    """Test where player collects a bullet speed item."""
    _, _, _, items = mock_groups
    
    # Configure mocks
    mock_spritecollide.return_value = [mock_bullet_speed_item]
    mock_player.increase_bullet_speed = MagicMock(return_value=12)  # Mock the method
    
    result = check_items_player_collisions(mock_player, items, mock_groups[2])
    
    # Assertions
    mock_spritecollide.assert_called_once_with(mock_player, items, True)
    mock_player.increase_bullet_speed.assert_called_once_with(mock_bullet_speed_item.speed_increase)
    
    # Check result dict
    assert result['item_collected'] is True
    assert 'bullet_speed' in result['item_types']

@patch('pygame.sprite.spritecollide')
def test_no_item_collision(mock_spritecollide, mock_player, mock_groups):
    """Test where no items are collected."""
    _, _, _, items = mock_groups
    
    # Configure mocks
    mock_spritecollide.return_value = []  # No items hit
    
    result = check_items_player_collisions(mock_player, items, mock_groups[2])
    
    # Assertions
    mock_spritecollide.assert_called_once_with(mock_player, items, True)
    
    # Check result dict
    assert result['item_collected'] is False
    assert result['item_types'] == []
