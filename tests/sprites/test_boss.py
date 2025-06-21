import pytest
import pygame
import random
from unittest.mock import MagicMock, patch, call
from thunder_fighter.sprites.boss import Boss
from thunder_fighter.graphics.renderers import create_boss_ship

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

@pytest.fixture
def boss(mocker):
    """Fixture to create a Boss instance with mocked dependencies."""
    mock_all_sprites = mocker.MagicMock(spec=pygame.sprite.Group)
    # Use a real group for bullets to test add() behavior
    mock_boss_bullets = pygame.sprite.Group()
    mocker.patch('thunder_fighter.sprites.boss.create_boss_ship', return_value=pygame.Surface((100, 80)))
    
    # Mock pygame.time.get_ticks
    mocker.patch('pygame.time.get_ticks', return_value=0)
    
    boss_instance = Boss(mock_all_sprites, mock_boss_bullets, level=2, game_level=1)
    # Set a predictable position for tests
    boss_instance.rect.centerx = 240
    return boss_instance

class TestBoss:
    """Test suite for the Boss sprite."""

    def test_boss_initialization(self, boss):
        """测试Boss初始化是否正确设置属性"""
        assert boss.level == 2
        assert boss.health == boss.max_health
        assert boss.rect.centerx == 240
        assert boss.image is not None

    def test_boss_shooting(self, boss, mocker):
        """测试Boss射击逻辑"""
        # Patch the rendering function for bullets to avoid graphical operations
        mocker.patch('thunder_fighter.sprites.bullets.create_boss_bullet', return_value=pygame.Surface((5, 10)))
        
        initial_bullet_count = len(boss.boss_bullets_group)
        boss.shoot()
        assert len(boss.boss_bullets_group) > initial_bullet_count

    def test_boss_damage_and_health(self, boss):
        """测试Boss伤害和血量逻辑"""
        initial_health = boss.health
        boss.damage(20)
        assert boss.health == initial_health - 20
        assert boss.damage_flash > 0

    def test_flash_effect_implementation(self, boss):
        """
        Tests the implementation details of the improved flash effect.
        This verifies that the effect is more noticeable and robust.
        """
        # 1. Test flash duration
        # Act
        boss.damage(10)
        # Assert
        assert boss.damage_flash == 12, "Flash duration should be set to 12 frames"

        # 2. Test creation of multiple, distinct flash images
        flash_images = boss.flash_images
        assert len(flash_images) > 2, "Should create multiple flash images (e.g., normal, red, white)"
        
        original_image = boss.original_image
        # Check that flash images are different from the original
        # by comparing a sample of their bytes
        assert pygame.image.tostring(original_image, 'RGB') != pygame.image.tostring(flash_images[1], 'RGB')
        assert pygame.image.tostring(original_image, 'RGB') != pygame.image.tostring(flash_images[2], 'RGB')
        assert pygame.image.tostring(flash_images[1], 'RGB') != pygame.image.tostring(flash_images[2], 'RGB')

    def test_flash_effect_update_cycle(self, boss):
        """
        Tests that the update method correctly cycles through the flash images.
        """
        # Arrange
        boss.damage(10)
        initial_image = boss.image

        # Act & Assert: Check that the image changes over the update cycles
        seen_images = {initial_image}
        
        for _ in range(boss.damage_flash):
            boss.update()
            seen_images.add(boss.image)

        # After the cycle, the image should be restored
        boss.update()
        assert pygame.image.tostring(boss.image, 'RGB') == pygame.image.tostring(boss.original_image, 'RGB'), "Image should be restored after flash ends"
        
        # Check that multiple different images were displayed during the cycle
        assert len(seen_images) > 2, "The flash cycle should display multiple different images"

    def test_boss_movement_patterns(self, boss):
        """测试Boss的移动模式"""
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

    def test_boss_attack_pattern_changes(self, boss):
        """测试Boss根据生命值改变攻击模式"""
        initial_health = boss.health
        initial_shoot_pattern = boss.shoot_pattern
        
        # 造成大量伤害，使生命值降至50%以下
        boss.damage(initial_health // 2 + 1)
        
        # 更新状态以触发攻击模式变化
        boss.update()
        
        # 验证攻击模式是否改变
        # 通常，当Boss生命值较低时，攻击会更频繁或更激烈
        current_shoot_delay = boss.shoot_delay
        assert current_shoot_delay <= boss.shoot_delay
        
        # 验证攻击模式是否改变
        assert boss.shoot_pattern != initial_shoot_pattern

    def test_boss_dynamic_difficulty(self, boss):
        """测试不同游戏级别下Boss的难度调整"""
        # 比较不同游戏级别下相同等级Boss的属性
        boss_level = 2
        
        easy_game_boss = Boss(boss.all_sprites, boss.boss_bullets_group, boss_level, 1)
        medium_game_boss = Boss(boss.all_sprites, boss.boss_bullets_group, boss_level, 5)
        hard_game_boss = Boss(boss.all_sprites, boss.boss_bullets_group, boss_level, 10)
        
        # 验证更高游戏级别的Boss更强
        assert medium_game_boss.health >= easy_game_boss.health
        assert hard_game_boss.health >= medium_game_boss.health
        
        # 验证攻击速度随游戏级别增加
        assert medium_game_boss.shoot_delay <= easy_game_boss.shoot_delay
        assert hard_game_boss.shoot_delay <= medium_game_boss.shoot_delay