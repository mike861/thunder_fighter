import pytest
import pygame
import random
from unittest.mock import MagicMock, patch, call
from thunder_fighter.sprites.items import (
    HealthItem, BulletSpeedItem, BulletPathItem, PlayerSpeedItem, 
    create_random_item
)

@pytest.fixture
def mock_pygame():
    with patch('thunder_fighter.sprites.items.pygame') as mock, \
         patch('thunder_fighter.sprites.items.math') as mock_math:
        # 模拟pygame属性和方法
        mock.Rect = pygame.Rect
        mock.Surface.return_value = MagicMock()
        mock.mask.from_surface.return_value = MagicMock()
        mock.time.get_ticks.return_value = 0
        mock.SRCALPHA = pygame.SRCALPHA
        mock.draw = MagicMock()
        
        # 模拟math函数
        mock_math.sin.return_value = 0.5
        mock_math.radians.return_value = 0.5
        
        yield mock, mock_math

@pytest.fixture
def mock_random():
    with patch('thunder_fighter.sprites.items.random') as mock:
        # 默认返回值，可以在测试中根据需要更改
        mock.random.return_value = 0.5
        mock.randint.return_value = 400  # x坐标
        mock.choice.return_value = 'health'  # 默认选择健康道具
        mock.uniform.return_value = 0.5
        yield mock

@pytest.fixture
def mock_sprites_group():
    return MagicMock()

@pytest.fixture
def mock_items_group():
    return MagicMock()

def test_health_item_initialization(mock_pygame, mock_random):
    """测试生命值道具初始化"""
    # 配置随机位置
    mock_random.randrange.return_value = 400
    
    health_item = HealthItem()
    
    # 检查基本属性
    assert health_item.type == 'health'
    assert hasattr(health_item, 'image')
    assert hasattr(health_item, 'rect')
    assert hasattr(health_item, 'speedy')
    
    # 检查位置
    assert health_item.rect.x == 400

def test_bullet_speed_item_initialization(mock_pygame, mock_random):
    """测试子弹速度道具初始化"""
    # 配置随机位置和值
    mock_random.randrange.return_value = 400
    mock_random.randint.return_value = 2  # 速度增加值
    
    bullet_speed_item = BulletSpeedItem()
    
    # 检查基本属性
    assert bullet_speed_item.type == 'bullet_speed'
    assert hasattr(bullet_speed_item, 'speed_increase')
    assert bullet_speed_item.speed_increase > 0
    assert hasattr(bullet_speed_item, 'image')
    assert hasattr(bullet_speed_item, 'rect')
    
    # 检查位置
    assert bullet_speed_item.rect.x == 400

def test_bullet_path_item_initialization(mock_pygame, mock_random):
    """测试子弹弹道道具初始化"""
    # 配置随机位置
    mock_random.randrange.return_value = 400
    
    bullet_path_item = BulletPathItem()
    
    # 检查基本属性
    assert bullet_path_item.type == 'bullet_path'
    assert hasattr(bullet_path_item, 'image')
    assert hasattr(bullet_path_item, 'rect')
    
    # 检查位置
    assert bullet_path_item.rect.x == 400

def test_player_speed_item_initialization(mock_pygame, mock_random):
    """测试玩家速度道具初始化"""
    # 配置随机位置
    mock_random.randrange.return_value = 400
    
    player_speed_item = PlayerSpeedItem()
    
    # 检查基本属性
    assert player_speed_item.type == 'player_speed'
    assert hasattr(player_speed_item, 'speed_increase')
    assert player_speed_item.speed_increase > 0
    assert hasattr(player_speed_item, 'image')
    assert hasattr(player_speed_item, 'rect')
    
    # 检查位置
    assert player_speed_item.rect.x == 400

def test_item_movement(mock_pygame, mock_random):
    """测试道具移动行为"""
    # 解构mock_pygame
    mock_pg, mock_math = mock_pygame
    
    # 配置随机值
    mock_random.randrange.return_value = 400
    mock_random.choice.return_value = 1
    
    # 模拟math.sin和math.radians
    mock_math.sin.return_value = 0.5
    mock_math.radians.return_value = 0.5
    
    with patch('thunder_fighter.sprites.items.create_health_item') as mock_create_item:
        mock_create_item.return_value = pygame.Surface((20, 20))
        item = HealthItem()
    
    # 修复direction属性，确保它是整数
    item.direction = 1
    initial_y = item.rect.y
    
    # 更新位置
    item.update()
    
    # 道具应该向下移动
    assert item.rect.y > initial_y
    
    # 测试移出屏幕时的行为
    item.rect.top = 800  # 假设屏幕高度为600
    item.kill = MagicMock()
    
    # 更新位置
    item.update()
    
    # 验证kill方法是否被调用
    item.kill.assert_called_once()

@patch('thunder_fighter.sprites.items.HealthItem')
@patch('thunder_fighter.sprites.items.BulletSpeedItem')
@patch('thunder_fighter.sprites.items.BulletPathItem')
@patch('thunder_fighter.sprites.items.PlayerSpeedItem')
def test_create_random_item(mock_player_speed, mock_bullet_path, 
                          mock_bullet_speed, mock_health, 
                          mock_pygame, mock_random, 
                          mock_sprites_group, mock_items_group):
    """测试随机道具创建"""
    # 调用随机道具创建函数
    game_time = 5  # 游戏时间5分钟
    
    # 配置随机返回值以创建各种道具
    # 测试健康道具创建
    mock_random.random.return_value = 0.1  # 确保落在health道具的概率范围内
    mock_random.randrange.return_value = 400  # 位置

    # 返回健康道具实例
    health_instance = MagicMock()
    health_instance.rect.centerx = 400
    health_instance.rect.centery = 0
    mock_health.return_value = health_instance
    
    create_random_item(game_time, mock_sprites_group, mock_items_group)
    
    # 验证调用
    mock_health.assert_called_once()
    mock_sprites_group.add.assert_called_with(health_instance)
    mock_items_group.add.assert_called_with(health_instance)
    
    # 重置mock以测试子弹速度道具
    mock_sprites_group.reset_mock()
    mock_items_group.reset_mock()
    mock_health.reset_mock()
    
    # 测试子弹速度道具
    mock_random.random.return_value = 0.5  # 确保落在bullet_speed道具的概率范围内
    
    # 返回子弹速度道具实例
    speed_instance = MagicMock()
    speed_instance.rect.centerx = 400
    speed_instance.rect.centery = 0
    mock_bullet_speed.return_value = speed_instance
    
    create_random_item(game_time, mock_sprites_group, mock_items_group)
    
    # 验证调用
    mock_bullet_speed.assert_called_once()
    mock_sprites_group.add.assert_called_with(speed_instance)
    mock_items_group.add.assert_called_with(speed_instance)

def test_item_type_distribution_by_game_time(mock_pygame, mock_random):
    """测试游戏时间对道具类型分布的影响"""
    # 模拟不同游戏时间下道具类型分布
    
    # 配置mock以确保能创建指定类型的道具
    # 使用下面的mock_random.random而不是mock_random.choice
    
    # 游戏早期（1分钟）：生命值道具概率更高
    mock_random.random.return_value = 0.1  # 小于health道具概率
    mock_random.randrange.return_value = 400  # mock位置
    
    # 创建模拟sprite组
    mock_sprites = MagicMock()
    mock_items = MagicMock()
    
    # 创建早期道具
    early_item = create_random_item(1, mock_sprites, mock_items)
    assert early_item.type == 'health'
    
    # 游戏中期（5分钟）：子弹速度道具概率增加
    mock_random.random.return_value = 0.5  # 落在bullet_speed道具概率范围
    
    # 创建中期道具
    mid_item = create_random_item(5, mock_sprites, mock_items)
    assert mid_item.type == 'bullet_speed'
    
    # 游戏后期（10分钟）：子弹路径道具概率增加
    mock_random.random.return_value = 0.8  # 落在bullet_path道具概率范围
    
    # 创建后期道具
    late_item = create_random_item(10, mock_sprites, mock_items)
    assert late_item.type == 'bullet_path' 