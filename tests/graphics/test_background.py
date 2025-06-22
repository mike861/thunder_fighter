import pytest
import pygame
from unittest.mock import MagicMock, patch
from thunder_fighter.graphics.background import Star, Nebula, Planet, DynamicBackground

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
        assert len(background.nebulae) == 3
        assert len(background.planets) == 2
        
        # Check animation variables
        assert hasattr(background, 'color_phase')
        assert hasattr(background, 'color_speed')
    
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