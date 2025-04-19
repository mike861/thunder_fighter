import pytest
import pygame
import random
from unittest.mock import MagicMock, patch, call
from thunder_fighter.sprites.boss import Boss

@pytest.fixture
def mock_pygame():
    with patch('thunder_fighter.sprites.boss.pygame') as mock, \
         patch('thunder_fighter.sprites.boss.ptime') as mock_ptime:
        # 模拟pygame属性和方法
        mock.Rect = pygame.Rect
        # 创建真实的Surface而不是MagicMock
        mock.Surface = pygame.Surface
        mock.SRCALPHA = pygame.SRCALPHA
        # 确保mask.from_surface返回真实的掩码对象
        mock.mask.from_surface = pygame.mask.from_surface
        # 设置pygame.time
        mock_ptime.get_ticks.return_value = 0
        mock.math.Vector2.return_value = MagicMock()
        # 返回两个mock
        yield mock, mock_ptime

@pytest.fixture
def mock_random():
    with patch('thunder_fighter.sprites.boss.random') as mock:
        # 默认返回值，可以在测试中根据需要更改
        mock.random.return_value = 0.5
        mock.randint.return_value = 50
        mock.choice.return_value = 1
        mock.uniform.return_value = 0.5
        # 重要：确保choices返回整数而不是MagicMock
        mock.choices.return_value = [1]  # 确保返回列表中包含整数
        yield mock

@pytest.fixture
def mock_sprites_group():
    return MagicMock()

@pytest.fixture
def mock_bullets_group():
    return MagicMock()

@pytest.fixture
def mock_create_boss_ship():
    with patch('thunder_fighter.sprites.boss.create_boss_ship') as mock:
        # 返回真实的Surface对象而不是MagicMock
        mock.return_value = pygame.Surface((100, 100))
        yield mock

def test_boss_initialization(mock_pygame, mock_random, mock_sprites_group, mock_bullets_group, mock_create_boss_ship):
    """测试Boss初始化是否正确设置属性"""
    # 解构mock_pygame为mock_pg和mock_ptime
    mock_pg, mock_ptime = mock_pygame
    # 测试不同的boss等级和游戏级别
    boss_level = 2
    game_level = 3
    
    boss = Boss(mock_sprites_group, mock_bullets_group, boss_level, game_level)
    
    # 检查基本属性是否已创建
    assert hasattr(boss, 'image')
    assert hasattr(boss, 'rect')
    assert hasattr(boss, 'mask')
    assert hasattr(boss, 'health')
    assert hasattr(boss, 'max_health')
    
    # 确保Boss的属性与等级相关
    assert boss.level == boss_level
    assert boss.health > 0
    
    # 更高等级的Boss应该更强
    higher_level_boss = Boss(mock_sprites_group, mock_bullets_group, boss_level + 1, game_level)
    assert higher_level_boss.health > boss.health
    
    # 更高游戏级别应该增加Boss难度
    higher_game_level_boss = Boss(mock_sprites_group, mock_bullets_group, boss_level, game_level + 2)
    assert higher_game_level_boss.health >= boss.health

def test_boss_shooting(mock_pygame, mock_random, mock_sprites_group, mock_bullets_group, mock_create_boss_ship):
    """测试Boss射击行为"""
    # 解构mock_pygame为mock_pg和mock_ptime
    mock_pg, mock_ptime = mock_pygame
    # 替代方法：不使用@patch装饰器，改为直接替换shoot方法
    boss = Boss(mock_sprites_group, mock_bullets_group, 2, 3)
    boss.shoot_delay = 1000
    boss.last_shot = 0
    
    # 设置Boss位置，确保已经进入屏幕且满足射击条件
    boss.rect.top = 50
    
    # 保存原始方法并用模拟替换
    original_shoot = boss.shoot
    boss.shoot = MagicMock()
    
    # 模拟时间经过，允许射击
    mock_ptime.get_ticks.return_value = 1500
    
    # 验证初始攻击模式
    assert boss.shoot_pattern == "normal"
    
    # 更新Boss状态
    boss.update()
    
    # 验证是否尝试调用射击方法
    boss.shoot.assert_called_once()
    
    # 确保最后射击时间已更新
    assert boss.last_shot == 1500
    
    # 测试不同攻击模式下的射击行为
    # 先清除之前的调用记录
    boss.shoot.reset_mock()
    
    # 设置为激进模式
    boss.shoot_pattern = "aggressive"
    boss.last_shot = 1500  # Ensure last_shot is set to the current mock time
    
    # 模拟时间经过，允许再次射击
    mock_ptime.get_ticks.return_value = 3000
    boss.update()
    
    # 验证在激进模式下是否射击
    boss.shoot.assert_called_once()
    
    # 最后测试最终模式
    boss.shoot.reset_mock()
    
    boss.shoot_pattern = "final"
    boss.last_shot = 3000  # Update last_shot to current mock time
    mock_ptime.get_ticks.return_value = 4500
    boss.update()
    
    # 验证最终模式下的射击
    boss.shoot.assert_called_once()
    
    # 恢复原始方法
    boss.shoot = original_shoot

def test_boss_movement_patterns(mock_pygame, mock_random, mock_sprites_group, mock_bullets_group, mock_create_boss_ship):
    """测试Boss的移动模式"""
    # 解构mock_pygame为mock_pg和mock_ptime
    mock_pg, mock_ptime = mock_pygame
    boss = Boss(mock_sprites_group, mock_bullets_group, 2, 3)
    
    # 手动设置初始位置和移动参数
    boss.rect.y = 50  # 确保Boss已入场
    initial_x = boss.rect.centerx
    initial_y = boss.rect.centery
    
    # 设置方向和速度
    boss.direction = 1
    boss.base_speedx = 5  # 使用较大的速度值确保移动效果明显
    
    # 更新Boss状态
    boss.update()
    
    # Y坐标应该保持相对稳定（可能在一定范围内波动）
    assert abs(boss.rect.centery - initial_y) < 50
    
    # 检查是否在水平方向上移动
    # 由于方向为1，speedx为正，所以x坐标应该增加
    assert boss.rect.centerx > initial_x
    
    # 重置位置，然后测试方向变化
    boss.rect.centerx = initial_x
    boss.direction = -1
    boss.update()
    
    # 方向为-1，speedx为负，所以x坐标应该减少
    assert boss.rect.centerx < initial_x
    
    # 测试边界反弹
    # 将Boss移动到屏幕左边界附近
    boss.rect.left = 10
    boss.direction = -1  # 向左移动
    boss.speedx = boss.base_speedx * boss.direction  # 确保speedx是负值
    
    boss.update()
    
    # 应该反向移动（方向改变为正）
    assert boss.direction > 0
    
    # 将Boss移动到屏幕右边界附近
    boss.rect.right = 790  # 假设屏幕宽度为800
    boss.direction = 1  # 向右移动
    boss.speedx = boss.base_speedx * boss.direction  # 确保speedx是正值
    
    boss.update()
    
    # 应该反向移动（方向改变为负）
    assert boss.direction < 0

def test_boss_damage_and_health(mock_pygame, mock_random, mock_sprites_group, mock_bullets_group, mock_create_boss_ship):
    """测试Boss受伤和生命值减少"""
    # 解构mock_pygame为mock_pg和mock_ptime
    mock_pg, mock_ptime = mock_pygame
    boss = Boss(mock_sprites_group, mock_bullets_group, 2, 3)
    initial_health = boss.health
    
    # 模拟受伤
    is_defeated = boss.damage(20)
    
    # 验证生命值减少
    assert boss.health == initial_health - 20
    assert boss.damage_flash > 0  # 应该有伤害闪烁效果
    assert is_defeated is False  # Boss还没被击败
    
    # 模拟致命伤害
    boss.kill = MagicMock()
    is_defeated = boss.damage(boss.health + 10)
    
    # 验证Boss被摧毁
    assert is_defeated is True
    boss.kill.assert_called_once()

def test_boss_attack_pattern_changes(mock_pygame, mock_random, mock_sprites_group, mock_bullets_group, mock_create_boss_ship):
    """测试Boss根据生命值改变攻击模式"""
    # 解构mock_pygame为mock_pg和mock_ptime
    mock_pg, mock_ptime = mock_pygame
    boss = Boss(mock_sprites_group, mock_bullets_group, 3, 3)
    initial_health = boss.health
    initial_shoot_pattern = boss.shoot_pattern
    
    # 记录初始攻击状态
    initial_shoot_delay = boss.shoot_delay
    
    # 造成大量伤害，使生命值降至50%以下
    boss.damage(initial_health // 2 + 1)
    
    # 更新状态以触发攻击模式变化
    boss.update()
    
    # 验证攻击模式是否改变
    # 通常，当Boss生命值较低时，攻击会更频繁或更激烈
    current_shoot_delay = boss.shoot_delay
    assert current_shoot_delay <= initial_shoot_delay
    
    # 验证攻击模式是否改变
    assert boss.shoot_pattern != initial_shoot_pattern

def test_boss_dynamic_difficulty(mock_pygame, mock_random, mock_sprites_group, mock_bullets_group, mock_create_boss_ship):
    """测试不同游戏级别下Boss的难度调整"""
    # 解构mock_pygame为mock_pg和mock_ptime
    mock_pg, mock_ptime = mock_pygame
    # 比较不同游戏级别下相同等级Boss的属性
    boss_level = 2
    
    easy_game_boss = Boss(mock_sprites_group, mock_bullets_group, boss_level, 1)
    medium_game_boss = Boss(mock_sprites_group, mock_bullets_group, boss_level, 5)
    hard_game_boss = Boss(mock_sprites_group, mock_bullets_group, boss_level, 10)
    
    # 验证更高游戏级别的Boss更强
    assert medium_game_boss.health >= easy_game_boss.health
    assert hard_game_boss.health >= medium_game_boss.health
    
    # 验证攻击速度随游戏级别增加
    assert medium_game_boss.shoot_delay <= easy_game_boss.shoot_delay
    assert hard_game_boss.shoot_delay <= medium_game_boss.shoot_delay 