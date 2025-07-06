import pytest
import pygame
from unittest.mock import MagicMock, patch
from thunder_fighter.graphics.background import Star, Nebula, Planet, DynamicBackground, SpaceStorm, AsteroidField

class TestStar:
    """Test Star class"""
    
    def test_star_initialization(self):
        """Test star initialization with different layers"""
        star1 = Star(layer=1)
        star2 = Star(layer=2)
        star3 = Star(layer=3)
        
        # Check layer-specific properties
        assert star1.layer == 1
        assert star2.layer == 2
        assert star3.layer == 3
        
        # Layer 3 should be fastest
        assert star3.speed > star2.speed > star1.speed
        
        # Check brightness ranges are correct for each layer
        assert 80 <= star1.brightness <= 150
        assert 120 <= star2.brightness <= 200
        assert 150 <= star3.brightness <= 255
    
    def test_star_update(self):
        """Test star position update"""
        star = Star(layer=1)
        initial_y = star.y
        
        star.update()
        
        # Star should move down
        assert star.y > initial_y
    
    def test_star_reset_position(self):
        """Test star position reset when off screen"""
        star = Star(layer=1)
        star.y = 700  # Move off screen
        
        star.update()
        
        # Star should reset to top
        assert star.y < 0

class TestNebula:
    """Test Nebula class"""
    
    def test_nebula_initialization(self):
        """Test nebula initialization"""
        nebula = Nebula()
        
        assert hasattr(nebula, 'x')
        assert hasattr(nebula, 'y')
        assert hasattr(nebula, 'speed')
        assert hasattr(nebula, 'size')
        assert hasattr(nebula, 'color')
        assert hasattr(nebula, 'alpha')
    
    def test_nebula_update(self):
        """Test nebula position update"""
        nebula = Nebula()
        initial_y = nebula.y
        
        nebula.update()
        
        # Nebula should move down
        assert nebula.y >= initial_y

class TestPlanet:
    """Test Planet class"""
    
    def test_planet_initialization(self):
        """Test planet initialization"""
        planet = Planet()
        
        assert hasattr(planet, 'x')
        assert hasattr(planet, 'y')
        assert hasattr(planet, 'speed')
        assert hasattr(planet, 'size')
        assert hasattr(planet, 'color')
        assert hasattr(planet, 'has_rings')
    
    def test_planet_update(self):
        """Test planet position update"""
        planet = Planet()
        initial_y = planet.y
        
        planet.update()
        
        # Planet should move down
        assert planet.y >= initial_y

class TestDynamicBackground:
    """Test DynamicBackground class"""
    
    def test_background_initialization(self):
        """Test dynamic background initialization"""
        background = DynamicBackground()
        
        # Check that all components are created
        assert len(background.stars_layer1) == 30
        assert len(background.stars_layer2) == 20
        assert len(background.stars_layer3) == 15
        # After initialization, level 1 theme is applied, which has 2 nebulae
        assert len(background.nebulae) == 2
        # Level 1 theme has 1 planet
        assert len(background.planets) == 1
        
        # Check animation variables
        assert hasattr(background, 'color_phase')
        assert hasattr(background, 'color_speed')
        
        # Check level-related attributes
        assert background.current_level == 1
        assert background.target_level == 1
        assert not background.transitioning
    
    def test_background_update(self):
        """Test background update method"""
        background = DynamicBackground()
        initial_phase = background.color_phase
        
        background.update()
        
        # Color phase should change
        assert background.color_phase != initial_phase
    
    def test_background_draw(self):
        """Test background drawing"""
        # Initialize pygame for testing
        pygame.init()
        
        # Create a real surface for testing
        test_screen = pygame.Surface((480, 600))
        
        background = DynamicBackground()
        
        # Should not raise any exceptions
        try:
            background.draw(test_screen)
        except Exception as e:
            pytest.fail(f"Background draw raised exception: {e}")
        
        # Test passed if no exception was raised
        assert True
    
    def test_level_transition(self):
        """Test level transition functionality"""
        background = DynamicBackground()
        
        # Initially at level 1
        assert background.current_level == 1
        assert not background.transitioning
        
        # Trigger level change
        background.set_level(3)
        
        # Should be transitioning to level 3
        assert background.transitioning
        assert background.target_level == 3
        assert background.current_level == 1  # Still at old level during transition
        
        # Complete the transition by manually setting the flag
        background.transitioning = False
        background.current_level = background.target_level
        background._apply_level_theme(background.current_level)
        
        assert not background.transitioning
        assert background.current_level == 3
        assert background.asteroid_field is not None
    
    def test_special_effects_creation(self):
        """Test special effects are created for appropriate levels"""
        background = DynamicBackground()
        
        # Level 1 should have no special effects
        background.set_level(1)
        background.transitioning = False
        background.current_level = 1
        background._apply_level_theme(1)
        assert background.space_storm is None
        assert background.asteroid_field is None
        
        # Level 3 should have asteroid field
        background.set_level(3)
        background.transitioning = False
        background.current_level = 3
        background._apply_level_theme(3)
        assert background.asteroid_field is not None
        assert background.space_storm is None
        
        # Level 4 should have space storm
        background.set_level(4)
        background.transitioning = False
        background.current_level = 4
        background._apply_level_theme(4)
        assert background.space_storm is not None
        assert background.asteroid_field is None

class TestSpaceStorm:
    """Test SpaceStorm class"""
    
    def test_space_storm_initialization(self):
        """Test space storm initialization"""
        storm = SpaceStorm()
        
        assert hasattr(storm, 'particles')
        assert hasattr(storm, 'intensity')
        assert len(storm.particles) == 20
        assert storm.intensity == 1.0
    
    def test_space_storm_update(self):
        """Test space storm particle update"""
        storm = SpaceStorm()
        initial_positions = [(p['x'], p['y']) for p in storm.particles]
        
        storm.update()
        
        # At least some particles should have moved
        current_positions = [(p['x'], p['y']) for p in storm.particles]
        assert initial_positions != current_positions

class TestAsteroidField:
    """Test AsteroidField class"""
    
    def test_asteroid_field_initialization(self):
        """Test asteroid field initialization"""
        field = AsteroidField()
        
        assert hasattr(field, 'asteroids')
        assert len(field.asteroids) == 8
        
        # Check each asteroid has required properties
        for asteroid in field.asteroids:
            assert 'x' in asteroid
            assert 'y' in asteroid
            assert 'speed' in asteroid
            assert 'rotation' in asteroid
            assert 'size' in asteroid
            assert 'shape' in asteroid
    
    def test_asteroid_field_update(self):
        """Test asteroid field update"""
        field = AsteroidField()
        initial_rotations = [a['rotation'] for a in field.asteroids]
        
        field.update()
        
        # Rotations should have changed
        current_rotations = [a['rotation'] for a in field.asteroids]
        assert initial_rotations != current_rotations 