import pygame
import random
import math
from thunder_fighter.constants import WIDTH, HEIGHT, WHITE, BLUE, DARK_BLUE, LIGHT_BLUE, CYAN, PURPLE

class Star:
    """Enhanced background star class with multiple layers and effects"""
    def __init__(self, layer=1):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, 0)  # Start above screen
        self.layer = layer
        
        # Different speeds for parallax effect
        if layer == 1:  # Far stars
            self.speed = random.uniform(0.5, 1.0)
            self.size = random.randint(1, 2)
            self.brightness = random.randint(80, 150)
        elif layer == 2:  # Medium stars
            self.speed = random.uniform(1.0, 2.0)
            self.size = random.randint(1, 3)
            self.brightness = random.randint(120, 200)
        else:  # Near stars (layer 3)
            self.speed = random.uniform(2.0, 3.5)
            self.size = random.randint(2, 4)
            self.brightness = random.randint(150, 255)
        
        # Twinkling effect
        self.twinkle_phase = random.uniform(0, math.pi * 2)
        self.twinkle_speed = random.uniform(0.02, 0.05)
        
        # Color variation
        self.color_type = random.choice(['white', 'blue', 'cyan'])
    
    def update(self):
        """Update star position and effects"""
        self.y += self.speed
        if self.y > HEIGHT + 10:
            self.y = random.randint(-50, -10)
            self.x = random.randint(0, WIDTH)
        
        # Update twinkling
        self.twinkle_phase += self.twinkle_speed
    
    def draw(self, screen):
        """Draw star with twinkling effect"""
        # Calculate twinkling brightness
        twinkle_factor = (math.sin(self.twinkle_phase) + 1) * 0.3 + 0.4  # Range 0.4-1.0
        brightness = int(self.brightness * twinkle_factor)
        
        # Choose color based on type
        if self.color_type == 'white':
            color = (brightness, brightness, brightness)
        elif self.color_type == 'blue':
            color = (brightness // 3, brightness // 2, brightness)
        else:  # cyan
            color = (brightness // 4, brightness, brightness)
        
        # Draw star with size variation for twinkling
        size = self.size if twinkle_factor > 0.7 else max(1, self.size - 1)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), size)

class Nebula:
    """Background nebula cloud effect"""
    def __init__(self):
        self.x = random.randint(-100, WIDTH + 100)
        self.y = random.randint(-200, HEIGHT + 200)
        self.speed = random.uniform(0.1, 0.3)
        self.size = random.randint(80, 200)
        self.color = random.choice([
            (50, 20, 80),   # Purple
            (20, 50, 80),   # Blue
            (80, 20, 50),   # Red
            (20, 80, 50),   # Green
        ])
        self.alpha = random.randint(10, 30)
        self.rotation = 0
        self.rotation_speed = random.uniform(-0.01, 0.01)
    
    def update(self):
        """Update nebula position and rotation"""
        self.y += self.speed
        self.rotation += self.rotation_speed
        
        if self.y > HEIGHT + 200:
            self.y = random.randint(-400, -200)
            self.x = random.randint(-100, WIDTH + 100)
    
    def draw(self, screen):
        """Draw nebula with transparency"""
        # Create a surface for the nebula
        nebula_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Draw multiple circles for cloud effect
        for i in range(3):
            radius = self.size // (2 + i)
            alpha = self.alpha // (1 + i)
            color = (*self.color, alpha)
            center = (self.size // 2, self.size // 2)
            
            # Create individual circle surface
            circle_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(circle_surface, color, (radius, radius), radius)
            
            # Blit to nebula surface
            nebula_surface.blit(circle_surface, (center[0] - radius, center[1] - radius), 
                              special_flags=pygame.BLEND_ALPHA_SDL2)
        
        # Rotate if needed
        if self.rotation != 0:
            nebula_surface = pygame.transform.rotate(nebula_surface, math.degrees(self.rotation))
        
        # Blit to screen
        rect = nebula_surface.get_rect(center=(self.x, self.y))
        screen.blit(nebula_surface, rect, special_flags=pygame.BLEND_ADD)

class Planet:
    """Background planet object"""
    def __init__(self):
        self.x = random.randint(-50, WIDTH + 50)
        self.y = random.randint(-300, -100)
        self.speed = random.uniform(0.2, 0.5)
        self.size = random.randint(30, 80)
        self.color = random.choice([
            (100, 150, 200),  # Blue planet
            (200, 150, 100),  # Brown planet
            (150, 200, 100),  # Green planet
            (200, 100, 150),  # Pink planet
        ])
        self.has_rings = random.choice([True, False])
        self.ring_color = (150, 150, 150)
    
    def update(self):
        """Update planet position"""
        self.y += self.speed
        
        if self.y > HEIGHT + 100:
            self.y = random.randint(-400, -100)
            self.x = random.randint(-50, WIDTH + 50)
    
    def draw(self, screen):
        """Draw planet with optional rings"""
        # Draw planet body
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        
        # Add shading for 3D effect
        shadow_color = tuple(c // 2 for c in self.color)
        pygame.draw.circle(screen, shadow_color, 
                         (int(self.x + self.size // 3), int(self.y + self.size // 3)), 
                         self.size // 3)
        
        # Add highlight
        highlight_color = tuple(min(255, c + 50) for c in self.color)
        pygame.draw.circle(screen, highlight_color, 
                         (int(self.x - self.size // 4), int(self.y - self.size // 4)), 
                         self.size // 6)
        
        # Draw rings if planet has them
        if self.has_rings:
            ring_width = self.size + 20
            ring_height = self.size // 3
            ring_rect = pygame.Rect(self.x - ring_width // 2, self.y - ring_height // 2, 
                                  ring_width, ring_height)
            pygame.draw.ellipse(screen, self.ring_color, ring_rect, 2)

class DynamicBackground:
    """Dynamic scrolling background system"""
    def __init__(self):
        # Create multiple star layers for parallax effect
        self.stars_layer1 = [Star(layer=1) for _ in range(30)]  # Far stars
        self.stars_layer2 = [Star(layer=2) for _ in range(20)]  # Medium stars
        self.stars_layer3 = [Star(layer=3) for _ in range(15)]  # Near stars
        
        # Create nebula clouds
        self.nebulae = [Nebula() for _ in range(3)]
        
        # Create planets
        self.planets = [Planet() for _ in range(2)]
        
        # Background gradient colors
        self.bg_colors = [
            (5, 5, 20),     # Deep space
            (10, 5, 30),    # Dark blue
            (5, 10, 25),    # Blue-purple
        ]
        
        # Animation variables
        self.color_phase = 0
        self.color_speed = 0.01
    
    def update(self):
        """Update all background elements"""
        # Update all star layers
        for star in self.stars_layer1:
            star.update()
        for star in self.stars_layer2:
            star.update()
        for star in self.stars_layer3:
            star.update()
        
        # Update nebulae
        for nebula in self.nebulae:
            nebula.update()
        
        # Update planets
        for planet in self.planets:
            planet.update()
        
        # Update background color animation
        self.color_phase += self.color_speed
    
    def draw_gradient_background(self, screen):
        """Draw animated gradient background"""
        # Calculate current background color
        phase = (math.sin(self.color_phase) + 1) * 0.5  # Normalize to 0-1
        
        # Interpolate between colors
        color1 = self.bg_colors[0]
        color2 = self.bg_colors[1]
        current_color = tuple(
            int(color1[i] + (color2[i] - color1[i]) * phase) 
            for i in range(3)
        )
        
        # Fill background with gradient effect
        screen.fill(current_color)
        
        # Add subtle vertical gradient
        for y in range(0, HEIGHT, 4):
            gradient_factor = y / HEIGHT
            gradient_color = tuple(
                min(255, int(current_color[i] + gradient_factor * 10)) 
                for i in range(3)
            )
            pygame.draw.line(screen, gradient_color, (0, y), (WIDTH, y), 4)
    
    def draw(self, screen):
        """Draw all background elements in correct order"""
        # 1. Draw gradient background
        self.draw_gradient_background(screen)
        
        # 2. Draw nebulae (furthest back)
        for nebula in self.nebulae:
            nebula.draw(screen)
        
        # 3. Draw planets
        for planet in self.planets:
            planet.draw(screen)
        
        # 4. Draw stars in layers (parallax effect)
        for star in self.stars_layer1:  # Furthest stars
            star.draw(screen)
        for star in self.stars_layer2:  # Medium stars
            star.draw(screen)
        for star in self.stars_layer3:  # Nearest stars
            star.draw(screen) 