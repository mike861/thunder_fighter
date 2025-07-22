"""
Ultimate solution for collision test isolation issues.

This implementation provides a complete fix by:
1. Using the ACTUAL import paths from the collision module
2. Properly handling dynamic imports
3. Ensuring complete test isolation
4. Avoiding all forms of state pollution
"""

import sys
import random
from unittest.mock import MagicMock, patch, Mock
import pytest

from thunder_fighter.constants import BULLET_CONFIG


class CollisionTestBase:
    """Base class ensuring complete test isolation."""
    
    def setup_method(self):
        """Set up clean state before each test."""
        # Clear any existing patches to prevent state pollution
        patch.stopall()
        
    def teardown_method(self):
        """Clean up state after each test."""
        # Ensure all patches are cleared
        patch.stopall()
    
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


class TestBulletEnemyCollisionsFinal(CollisionTestBase):
    """Final implementation of bullet-enemy collision tests."""
    
    def test_bullet_hits_enemy_no_item(self, collision_mocks):
        """Test bullet hitting enemy without generating item."""
        # Import the actual function
        from thunder_fighter.systems.collision import check_bullet_enemy_collisions
        
        # Use a single patch context for all related patches
        with patch('pygame.sprite.groupcollide') as mock_groupcollide:
            # Patch the dynamic imports at their actual usage locations
            with patch('thunder_fighter.graphics.effects.explosion.Explosion') as mock_explosion:
                with patch('thunder_fighter.entities.items.items.create_random_item') as mock_create_item:
                    
                    # Configure the collision result
                    mock_groupcollide.return_value = {
                        collision_mocks['enemy']: [collision_mocks['bullet']]
                    }
                    
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


class TestItemPlayerCollisionsFinal(CollisionTestBase):
    """Final implementation of item-player collision tests."""
    
    def test_player_collects_health_item(self, collision_mocks):
        """Test player collecting a health item."""
        # Import the function
        from thunder_fighter.systems.collision import check_items_player_collisions
        
        # Create a health item mock
        health_item = MagicMock()
        health_item.type = "health"
        health_item.rect = MagicMock()
        
        # Patch spritecollide to return the health item
        with patch('pygame.sprite.spritecollide', return_value=[health_item]):
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
        
        # Patch spritecollide to return empty list
        with patch('pygame.sprite.spritecollide', return_value=[]):
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


class TestEnemyPlayerCollisionsFinal(CollisionTestBase):
    """Final implementation of enemy-player collision tests."""
    
    def test_enemy_hits_player(self, collision_mocks):
        """Test enemy colliding with player."""
        # Import the function
        from thunder_fighter.systems.collision import check_enemy_player_collisions
        
        # Patch both spritecollide and the dynamic Explosion import
        with patch('pygame.sprite.spritecollide') as mock_spritecollide:
            with patch('thunder_fighter.graphics.effects.explosion.Explosion') as mock_explosion:
                # Configure spritecollide to return the enemy
                mock_spritecollide.return_value = [collision_mocks['enemy']]
                
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
        
        # Patch spritecollide to return empty list
        with patch('pygame.sprite.spritecollide', return_value=[]):
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


class TestBulletBossCollisionsFinal(CollisionTestBase):
    """Final implementation of bullet-boss collision tests."""
    
    def test_bullet_hits_boss_not_defeated(self, collision_mocks):
        """Test bullet hitting boss without defeating it."""
        # Import the function
        from thunder_fighter.systems.collision import check_bullet_boss_collisions
        
        # Need to patch the exact pygame function and collide_mask
        import pygame
        with patch('pygame.sprite.spritecollide') as mock_spritecollide:
            with patch('pygame.sprite.collide_mask') as mock_collide_mask:
                # Configure the collision
                mock_spritecollide.return_value = [collision_mocks['bullet']]
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