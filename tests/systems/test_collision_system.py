"""Tests for the CollisionSystem.

Tests the unified collision detection and resolution system.
Merged with comprehensive test cases from legacy utils/collisions.py tests.
"""

import sys
import random
from unittest.mock import MagicMock, patch, Mock
import pytest

from thunder_fighter.constants import BULLET_CONFIG
from thunder_fighter.systems.collision import CollisionSystem


class CollisionTestBase:
    """Base class ensuring complete test isolation."""
    
    def setup_method(self):
        """Set up clean state before each test."""
        # Clear any existing patches to prevent state pollution
        patch.stopall()
        
        # ✅ CRITICAL: Reset global collision system singleton to prevent state pollution
        import thunder_fighter.systems.collision as collision_module
        collision_module._global_collision_system = None
        
        # ✅ CRITICAL: Initialize pygame to ensure clean state
        import pygame
        if not pygame.get_init():
            pygame.init()
        
    def teardown_method(self):
        """Clean up state after each test."""
        # Ensure all patches are cleared
        patch.stopall()
        
        # ✅ Clean up global collision system state
        import thunder_fighter.systems.collision as collision_module
        collision_module._global_collision_system = None
    
    @pytest.fixture(autouse=True)
    def complete_isolation(self):
        """Ensure complete test isolation before and after each test."""
        # Clear any existing patches
        patch.stopall()
        
        yield
        
        # Clean up after test
        patch.stopall()


@pytest.fixture
def collision_mocks():
    """Create all necessary mocks for collision tests."""
    mocks = {
        'enemy': MagicMock(),
        'bullet': MagicMock(),
        'boss': MagicMock(),
        'player': MagicMock(),
        'enemies_group': MagicMock(),
        'bullets_group': MagicMock(),
        'all_sprites': MagicMock(),
        'items_group': MagicMock(),
        'score': MagicMock(),
        'ui_manager': MagicMock(),
        'sound_manager': MagicMock(),
    }
    
    # Configure enemy
    mocks['enemy'].rect = MagicMock()
    mocks['enemy'].rect.center = (50, 50)
    mocks['enemy'].level = 1
    mocks['enemy'].alive.return_value = True
    
    # Configure bullet
    mocks['bullet'].rect = MagicMock()
    mocks['bullet'].rect.center = (55, 55)
    
    # Configure boss
    mocks['boss'].rect = MagicMock()
    mocks['boss'].rect.center = (200, 100)
    mocks['boss'].health = 100
    mocks['boss'].damage.return_value = False
    
    # Configure player
    mocks['player'].rect = MagicMock()
    mocks['player'].health = 100
    mocks['player'].heal = MagicMock()
    mocks['player'].increase_bullet_speed = MagicMock()
    mocks['player'].take_damage = MagicMock(return_value=False)
    
    # Configure score
    mocks['score'].value = 0
    mocks['score'].update = MagicMock()
    
    # Configure UI manager
    mocks['ui_manager'].show_item_collected = MagicMock()
    
    # Configure sound manager
    mocks['sound_manager'].play_sound = MagicMock()
    
    # Configure sprite groups
    mocks['all_sprites'].add = MagicMock()
    
    return mocks


class TestCollisionSystem:
    """Test the CollisionSystem class interface."""

    @pytest.fixture
    def collision_system(self):
        """Create a CollisionSystem for testing."""
        return CollisionSystem()

    def test_system_initialization(self, collision_system):
        """Test that the collision system initializes correctly."""
        assert collision_system is not None
        assert hasattr(collision_system, "collision_handlers")
        assert len(collision_system.collision_handlers) > 0

    def test_collision_handlers_setup(self, collision_system):
        """Test that collision handlers are properly set up."""
        expected_handlers = [
            "missile_enemy",
            "bullet_enemy",
            "bullet_boss",
            "enemy_player",
            "boss_bullet_player",
            "enemy_bullet_player",
            "items_player",
        ]

        for handler_name in expected_handlers:
            assert handler_name in collision_system.collision_handlers
            assert callable(collision_system.collision_handlers[handler_name])

    def test_collision_detection_interface(self, collision_system):
        """Test that collision detection methods exist."""
        assert hasattr(collision_system, "check_missile_enemy_collisions")
        assert hasattr(collision_system, "check_bullet_enemy_collisions")
        assert hasattr(collision_system, "check_bullet_boss_collisions")
        assert hasattr(collision_system, "check_enemy_player_collisions")
        assert hasattr(collision_system, "check_boss_bullet_player_collisions")
        assert hasattr(collision_system, "check_items_player_collisions")

    def test_process_all_collisions_interface(self, collision_system):
        """Test that the check_all_collisions method exists."""
        assert hasattr(collision_system, "check_all_collisions")
        assert callable(collision_system.check_all_collisions)


class TestBulletEnemyCollisions(CollisionTestBase):
    """Test bullet-enemy collision detection and resolution."""
    
    def test_bullet_hits_enemy_no_item(self, collision_mocks):
        """Test bullet hitting enemy without generating item."""
        # Import the actual function
        from thunder_fighter.systems.collision import check_bullet_enemy_collisions
        
        # ✅ CRITICAL: Use both module-level and function-level patching for complete isolation
        with patch('thunder_fighter.systems.collision.pygame.sprite.groupcollide') as mock_groupcollide:
            with patch('pygame.sprite.groupcollide', mock_groupcollide):
                with patch('thunder_fighter.graphics.effects.explosion.Explosion') as mock_explosion:
                    with patch('thunder_fighter.entities.items.items.create_random_item') as mock_create_item:
                        
                        # ✅ Configure collision result as real dict with mock objects as keys/values
                        collision_result = {
                            collision_mocks['enemy']: [collision_mocks['bullet']]
                        }
                        mock_groupcollide.return_value = collision_result
                        
                        # Execute the function
                        result = check_bullet_enemy_collisions(
                            collision_mocks['enemies_group'],
                            collision_mocks['bullets_group'],
                            collision_mocks['all_sprites'],
                            collision_mocks['score'],
                            0,  # last_score_checkpoint
                            200,  # score_threshold
                            collision_mocks['items_group'],
                            collision_mocks['player']
                        )
                        
                        # Verify results
                        assert result["enemy_hit"] is True
                        assert result["enemy_count"] == 1
                        assert result["generated_item"] is False
                        
                        # Verify function calls
                        collision_mocks['score'].update.assert_called_once_with(
                            10 + collision_mocks['enemy'].level * 2
                        )
                        mock_create_item.assert_not_called()


class TestItemPlayerCollisions(CollisionTestBase):
    """Test item-player collision detection and resolution."""
    
    def test_player_collects_health_item(self, collision_mocks):
        """Test player collecting a health item."""
        # Import the function
        from thunder_fighter.systems.collision import check_items_player_collisions
        
        # Create a health item mock
        health_item = MagicMock()
        health_item.type = "health"
        health_item.rect = MagicMock()
        
        # ✅ CRITICAL: Use both module-level and function-level patching for complete isolation
        with patch('thunder_fighter.systems.collision.pygame.sprite.spritecollide', return_value=[health_item]) as mock_spritecollide:
            with patch('pygame.sprite.spritecollide', mock_spritecollide):
                # Execute the function
                check_items_player_collisions(
                    collision_mocks['items_group'],
                    collision_mocks['player'],
                    collision_mocks['ui_manager'],
                    collision_mocks['sound_manager']
                )
                
                # Verify the expected behaviors
                collision_mocks['player'].heal.assert_called_once()
                collision_mocks['ui_manager'].show_item_collected.assert_called_with("health")
                collision_mocks['sound_manager'].play_sound.assert_called_with("item_pickup")
    
    def test_player_collects_no_items(self, collision_mocks):
        """Test player not collecting any items."""
        # Import the function
        from thunder_fighter.systems.collision import check_items_player_collisions
        
        # ✅ CRITICAL: Use both module-level and function-level patching for complete isolation
        with patch('thunder_fighter.systems.collision.pygame.sprite.spritecollide', return_value=[]) as mock_spritecollide:
            with patch('pygame.sprite.spritecollide', mock_spritecollide):
                # Execute the function
                check_items_player_collisions(
                    collision_mocks['items_group'],
                    collision_mocks['player'],
                    collision_mocks['ui_manager'],
                    collision_mocks['sound_manager']
                )
                
                # Verify nothing was called
                collision_mocks['player'].heal.assert_not_called()
                collision_mocks['ui_manager'].show_item_collected.assert_not_called()
                collision_mocks['sound_manager'].play_sound.assert_not_called()


class TestEnemyPlayerCollisions(CollisionTestBase):
    """Test enemy-player collision detection and resolution."""
    
    def test_enemy_hits_player(self, collision_mocks):
        """Test enemy colliding with player."""
        # Import the function
        from thunder_fighter.systems.collision import check_enemy_player_collisions
        
        # ✅ CRITICAL: Use both module-level and function-level patching for complete isolation
        with patch('thunder_fighter.systems.collision.pygame.sprite.spritecollide', return_value=[collision_mocks['enemy']]) as mock_spritecollide:
            with patch('pygame.sprite.spritecollide', mock_spritecollide):
                with patch('thunder_fighter.graphics.effects.explosion.Explosion') as mock_explosion:
                    # Execute the function
                    result = check_enemy_player_collisions(
                        collision_mocks['player'],
                        collision_mocks['enemies_group'],
                        collision_mocks['all_sprites']
                    )
                    
                    # Verify collision was detected
                    assert result["was_hit"] is True
                    assert result["game_over"] is False
                    assert result["damage"] == 15 + collision_mocks['enemy'].level * 1
                    
                    # Verify health was reduced
                    expected_health = 100 - (15 + collision_mocks['enemy'].level * 1)
                    assert collision_mocks['player'].health == expected_health
                    
                    # Verify explosion was created
                    mock_explosion.assert_called_once_with(collision_mocks['enemy'].rect.center)
    
    def test_no_enemy_player_collision(self, collision_mocks):
        """Test no collision between enemy and player."""
        # Import the function
        from thunder_fighter.systems.collision import check_enemy_player_collisions
        
        # ✅ CRITICAL: Use both module-level and function-level patching for complete isolation
        with patch('thunder_fighter.systems.collision.pygame.sprite.spritecollide', return_value=[]) as mock_spritecollide:
            with patch('pygame.sprite.spritecollide', mock_spritecollide):
                # Execute the function
                result = check_enemy_player_collisions(
                    collision_mocks['player'],
                    collision_mocks['enemies_group'],
                    collision_mocks['all_sprites']
                )
                
                # Verify no collision detected
                assert result["was_hit"] is False
                assert result["game_over"] is False
                assert result["damage"] == 0
                
                # Verify health unchanged
                assert collision_mocks['player'].health == 100


class TestBulletBossCollisions(CollisionTestBase):
    """Test bullet-boss collision detection and resolution."""
    
    def test_bullet_hits_boss_not_defeated(self, collision_mocks):
        """Test bullet hitting boss without defeating it."""
        # Import the function
        from thunder_fighter.systems.collision import check_bullet_boss_collisions
        
        # ✅ CRITICAL: Use both module-level and function-level patching for complete isolation
        with patch('thunder_fighter.systems.collision.pygame.sprite.spritecollide', return_value=[collision_mocks['bullet']]) as mock_spritecollide:
            with patch('pygame.sprite.spritecollide', mock_spritecollide):
                with patch('thunder_fighter.systems.collision.pygame.sprite.collide_mask') as mock_collide_mask:
                    with patch('pygame.sprite.collide_mask', mock_collide_mask):
                        # Configure the collision
                        collision_mocks['boss'].damage.return_value = False
                        
                        # Execute the function
                        result = check_bullet_boss_collisions(
                            collision_mocks['boss'],
                            collision_mocks['bullets_group'],
                            collision_mocks['all_sprites']
                        )
                        
                        # Verify results
                        assert result["boss_hit"] is True
                        assert result["boss_defeated"] is False
                        assert result["damage"] == int(BULLET_CONFIG["DAMAGE_TO_BOSS"])
                        
                        # Verify damage was called
                        collision_mocks['boss'].damage.assert_called_once_with(
                            int(BULLET_CONFIG["DAMAGE_TO_BOSS"])
                        )
                        
                        # Verify spritecollide was called with correct parameters
                        mock_spritecollide.assert_called_once_with(
                            collision_mocks['boss'],
                            collision_mocks['bullets_group'],
                            True,
                            mock_collide_mask
                        )
    
    def test_no_boss_collision(self, collision_mocks):
        """Test when boss is None."""
        # Import the function
        from thunder_fighter.systems.collision import check_bullet_boss_collisions
        
        # Execute with None boss
        result = check_bullet_boss_collisions(
            None,
            collision_mocks['bullets_group'],
            collision_mocks['all_sprites']
        )
        
        # Verify default results
        assert result["boss_hit"] is False
        assert result["boss_defeated"] is False
        assert result["damage"] == 0