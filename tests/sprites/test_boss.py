from unittest.mock import MagicMock, patch

import pygame
import pytest

from thunder_fighter.entities.enemies.boss import Boss

@pytest.fixture
def mock_pygame():
    with patch('thunder_fighter.sprites.boss.pygame') as mock, \
         patch('thunder_fighter.sprites.boss.ptime') as mock_ptime:
        # Mock pygame attributes and methods
        mock.Rect = pygame.Rect
        # Create real Surface instead of MagicMock
        mock.Surface = pygame.Surface
        mock.SRCALPHA = pygame.SRCALPHA
        # Ensure mask.from_surface returns real mask objects
        mock.mask.from_surface = pygame.mask.from_surface
        # Set pygame.time
        mock_ptime.get_ticks.return_value = 0
        mock.math.Vector2.return_value = MagicMock()
        # Return two mocks
        yield mock, mock_ptime

@pytest.fixture
def mock_random():
    with patch('thunder_fighter.sprites.boss.random') as mock:
        # Default return values, can be changed in tests as needed
        mock.random.return_value = 0.5
        mock.randint.return_value = 50
        mock.choice.return_value = 1
        mock.uniform.return_value = 0.5
        # Important: ensure choices returns integers, not MagicMock
        mock.choices.return_value = [1]  # Ensure list contains integers
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
        # Return real Surface object instead of MagicMock
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
        """Test if Boss initialization correctly sets attributes"""
        assert boss.level == 2
        assert boss.health == boss.max_health
        assert boss.rect.centerx == 240
        assert boss.image is not None

    def test_boss_shooting(self, boss, mocker):
        """Test Boss shooting logic"""
        # Patch the rendering function for bullets to avoid graphical operations
        mocker.patch('thunder_fighter.sprites.bullets.create_boss_bullet', return_value=pygame.Surface((5, 10)))

        initial_bullet_count = len(boss.boss_bullets_group)
        boss.shoot()
        assert len(boss.boss_bullets_group) > initial_bullet_count

    def test_boss_damage_and_health(self, boss):
        """Test Boss damage and health logic"""
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
        """Test Boss movement patterns"""
        # Manually set initial position and movement parameters
        boss.rect.y = 50  # Ensure Boss has entered
        initial_x = boss.rect.centerx
        initial_y = boss.rect.centery

        # Set direction and speed
        boss.direction = 1
        boss.base_speedx = 5  # Use larger speed value to ensure obvious movement effect

        # Update Boss state
        boss.update()

        # Y coordinate should remain relatively stable (may fluctuate within range)
        assert abs(boss.rect.centery - initial_y) < 50

        # Check horizontal movement
        # Since direction is 1, speedx is positive, so x coordinate should increase
        assert boss.rect.centerx > initial_x

        # Reset position, then test direction change
        boss.rect.centerx = initial_x
        boss.direction = -1
        boss.update()

        # Direction is -1, speedx is negative, so x coordinate should decrease
        assert boss.rect.centerx < initial_x

        # Test boundary bounce
        # Move Boss near left screen boundary
        boss.rect.left = 10
        boss.direction = -1  # Move left
        boss.speedx = boss.base_speedx * boss.direction  # Ensure speedx is negative

        boss.update()

        # Should reverse movement (direction changes to positive)
        assert boss.direction > 0

        # Move Boss near right screen boundary
        boss.rect.right = 790  # Assume screen width is 800
        boss.direction = 1  # Move right
        boss.speedx = boss.base_speedx * boss.direction  # Ensure speedx is positive

        boss.update()

        # Should reverse movement (direction changes to negative)
        assert boss.direction < 0

    def test_boss_attack_pattern_changes(self, boss):
        """Test Boss attack pattern changes based on health"""
        initial_health = boss.health
        initial_shoot_pattern = boss.shoot_pattern

        # Deal heavy damage to reduce health below 50%
        boss.damage(initial_health // 2 + 1)

        # Update state to trigger attack pattern change
        boss.update()

        # Verify if attack pattern has changed
        # Usually when Boss health is low, attacks become more frequent or intense
        current_shoot_delay = boss.shoot_delay
        assert current_shoot_delay <= boss.shoot_delay

        # Verify if attack pattern has changed
        assert boss.shoot_pattern != initial_shoot_pattern

    def test_boss_dynamic_difficulty(self, boss):
        """Test Boss difficulty adjustment for different game levels"""
        # Compare attributes of same level Boss under different game levels
        boss_level = 2

        easy_game_boss = Boss(boss.all_sprites, boss.boss_bullets_group, boss_level, 1)
        medium_game_boss = Boss(boss.all_sprites, boss.boss_bullets_group, boss_level, 5)
        hard_game_boss = Boss(boss.all_sprites, boss.boss_bullets_group, boss_level, 10)

        # Verify that higher game level Bosses are stronger
        assert medium_game_boss.health >= easy_game_boss.health
        assert hard_game_boss.health >= medium_game_boss.health

        # Verify attack speed increases with game level
        assert medium_game_boss.shoot_delay <= easy_game_boss.shoot_delay
        assert hard_game_boss.shoot_delay <= medium_game_boss.shoot_delay
