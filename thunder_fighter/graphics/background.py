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

class SpaceStorm:
    """Space storm effect for higher difficulty levels"""
    def __init__(self):
        self.particles = []
        self.spawn_timer = 0
        self.intensity = 1.0
        self.alpha = 255  # Add alpha support for smooth transitions
        
        # Create initial particles
        for _ in range(20):
            self.particles.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'speed': random.uniform(3, 6),
                'size': random.randint(1, 3),
                'alpha': random.randint(100, 200),
                'angle': random.uniform(0, math.pi * 2)
            })
    
    def update(self):
        """Update storm particles"""
        # Update existing particles
        for particle in self.particles:
            particle['y'] += particle['speed'] * self.intensity
            particle['x'] += math.sin(particle['angle']) * 2
            particle['angle'] += 0.1
            
            # Respawn if off screen
            if particle['y'] > HEIGHT + 10:
                particle['y'] = random.randint(-50, -10)
                particle['x'] = random.randint(0, WIDTH)
    
    def draw(self, screen):
        """Draw storm particles with alpha support"""
        if self.alpha <= 0:
            return
            
        for particle in self.particles:
            # Apply global alpha to particle alpha
            particle_alpha = int((particle['alpha'] / 255.0) * (self.alpha / 255.0) * 255)
            color = (200, 100, 100, particle_alpha)
            
            # Create particle surface
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, (particle['size'], particle['size']), particle['size'])
            
            # Draw with blend mode
            screen.blit(particle_surface, (int(particle['x']), int(particle['y'])), special_flags=pygame.BLEND_ADD)

class AsteroidField:
    """Asteroid field effect for asteroid belt level"""
    def __init__(self):
        self.asteroids = []
        self.alpha = 255  # Add alpha support for smooth transitions
        
        # Create asteroids
        for _ in range(8):
            self.asteroids.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(-HEIGHT, HEIGHT),
                'speed': random.uniform(0.5, 2),
                'rotation': 0,
                'rotation_speed': random.uniform(-0.02, 0.02),
                'size': random.randint(20, 50),
                'shape': self._generate_asteroid_shape()
            })
    
    def _generate_asteroid_shape(self):
        """Generate random asteroid shape"""
        points = []
        num_points = random.randint(6, 10)
        for i in range(num_points):
            angle = (math.pi * 2 * i) / num_points
            radius = random.uniform(0.8, 1.2)
            points.append((math.cos(angle) * radius, math.sin(angle) * radius))
        return points
    
    def update(self):
        """Update asteroids"""
        for asteroid in self.asteroids:
            asteroid['y'] += asteroid['speed']
            asteroid['rotation'] += asteroid['rotation_speed']
            
            if asteroid['y'] > HEIGHT + 100:
                asteroid['y'] = random.randint(-200, -50)
                asteroid['x'] = random.randint(0, WIDTH)
    
    def draw(self, screen):
        """Draw asteroids with alpha support"""
        if self.alpha <= 0:
            return
            
        for asteroid in self.asteroids:
            # Create asteroid surface
            size = asteroid['size']
            asteroid_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            
            # Draw asteroid shape
            points = []
            for px, py in asteroid['shape']:
                # Apply rotation
                cos_r = math.cos(asteroid['rotation'])
                sin_r = math.sin(asteroid['rotation'])
                rx = px * cos_r - py * sin_r
                ry = px * sin_r + py * cos_r
                
                # Scale and center
                points.append((size + rx * size * 0.8, size + ry * size * 0.8))
            
            # Apply alpha to colors
            alpha_factor = self.alpha / 255.0
            main_color = (int(60 * alpha_factor), int(40 * alpha_factor), int(30 * alpha_factor), self.alpha)
            border_color = (int(40 * alpha_factor), int(25 * alpha_factor), int(20 * alpha_factor), self.alpha)
            
            # Draw with alpha
            pygame.draw.polygon(asteroid_surface, main_color[:3], points)
            pygame.draw.polygon(asteroid_surface, border_color[:3], points, 2)
            
            # Apply overall alpha to surface
            asteroid_surface.set_alpha(self.alpha)
            
            # Blit to screen
            screen.blit(asteroid_surface, (int(asteroid['x'] - size), int(asteroid['y'] - size)))

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
    """Dynamic scrolling background system with level-based themes"""
    def __init__(self):
        # Create multiple star layers for parallax effect
        self.stars_layer1 = [Star(layer=1) for _ in range(30)]  # Far stars
        self.stars_layer2 = [Star(layer=2) for _ in range(20)]  # Medium stars
        self.stars_layer3 = [Star(layer=3) for _ in range(15)]  # Near stars
        
        # Create nebula clouds
        self.nebulae = [Nebula() for _ in range(3)]
        
        # Create planets
        self.planets = [Planet() for _ in range(2)]
        
        # Create special effects (initially inactive)
        self.space_storm = None
        self.asteroid_field = None
        
        # Current level and transition state
        self.current_level = 1
        self.target_level = 1
        self.transition_progress = 0.0
        self.transitioning = False
        
        # Double buffering for smooth transitions
        self.current_background_buffer = None
        self.target_background_buffer = None
        self.buffer_needs_update = True
        
        # Target level effects (for smooth transitions)
        self.target_nebulae = []
        self.target_planets = []
        self.target_space_storm = None
        self.target_asteroid_field = None
        
        # Level themes with progressive difficulty colors
        self.level_themes = {
            1: {  # Level 1 - Deep Space (Blue/Black)
                'primary_colors': [(5, 5, 20), (10, 5, 30), (5, 10, 25)],
                'nebula_colors': [(20, 50, 80), (50, 20, 80)],
                'star_brightness': 1.0,
                'nebula_count': 2,
                'planet_count': 1,
                'special_effect': None,
                'description': 'Deep Space'
            },
            2: {  # Level 2 - Nebula Field (Purple/Blue)
                'primary_colors': [(15, 5, 30), (25, 10, 40), (20, 5, 35)],
                'nebula_colors': [(80, 20, 100), (60, 40, 120)],
                'star_brightness': 0.9,
                'nebula_count': 4,
                'planet_count': 2,
                'special_effect': None,
                'description': 'Nebula Field'
            },
            3: {  # Level 3 - Asteroid Belt (Brown/Orange)
                'primary_colors': [(30, 15, 10), (40, 20, 15), (35, 18, 12)],
                'nebula_colors': [(120, 60, 30), (100, 50, 20)],
                'star_brightness': 0.8,
                'nebula_count': 3,
                'planet_count': 3,
                'special_effect': 'asteroid_field',
                'description': 'Asteroid Belt'
            },
            4: {  # Level 4 - Red Zone (Red/Orange)
                'primary_colors': [(40, 10, 10), (50, 15, 15), (45, 12, 12)],
                'nebula_colors': [(150, 30, 30), (120, 40, 20)],
                'star_brightness': 0.7,
                'nebula_count': 5,
                'planet_count': 2,
                'special_effect': 'space_storm',
                'description': 'Red Zone'
            },
            5: {  # Level 5 - Final Battle (Dark Red/Black)
                'primary_colors': [(30, 5, 5), (40, 10, 10), (35, 8, 8)],
                'nebula_colors': [(100, 20, 20), (80, 10, 10)],
                'star_brightness': 0.6,
                'nebula_count': 6,
                'planet_count': 1,
                'special_effect': 'space_storm',
                'description': 'Final Battle'
            }
        }
        
        # Animation variables
        self.color_phase = 0
        self.color_speed = 0.01
        
        # Transition effect variables
        self.transition_duration = 3.0  # Increased duration for smoother transition
        self.transition_start_time = 0
        
        # Initialize buffers (will be created when screen size is known)
        self._screen_size = None
        
        # Initialize with level 1 theme
        self._apply_level_theme(1)
    
    def set_level(self, level: int):
        """Start transition to a new level theme"""
        if level != self.current_level and level in self.level_themes:
            self.target_level = level
            self.transitioning = True
            self.transition_start_time = pygame.time.get_ticks() / 1000.0
            self.transition_progress = 0.0
            
            # Prepare target level elements for smooth transition
            self._prepare_target_level_elements(level)
            self.buffer_needs_update = True
    
    def _initialize_buffers(self, screen_size):
        """Initialize or recreate background buffers"""
        if self._screen_size != screen_size:
            self._screen_size = screen_size
            self.current_background_buffer = pygame.Surface(screen_size, pygame.SRCALPHA)
            self.target_background_buffer = pygame.Surface(screen_size, pygame.SRCALPHA)
            self.buffer_needs_update = True
    
    def _prepare_target_level_elements(self, level: int):
        """Prepare target level elements for smooth transition"""
        theme = self.level_themes.get(level, self.level_themes[1])
        
        # Prepare target nebulae
        self.target_nebulae = []
        target_nebula_count = theme['nebula_count']
        for _ in range(target_nebula_count):
            nebula = Nebula()
            nebula.color = random.choice(theme['nebula_colors'])
            self.target_nebulae.append(nebula)
        
        # Prepare target planets
        self.target_planets = []
        target_planet_count = theme['planet_count']
        for _ in range(target_planet_count):
            self.target_planets.append(Planet())
        
        # Prepare target special effects
        special_effect = theme.get('special_effect')
        self.target_space_storm = None
        self.target_asteroid_field = None
        
        if special_effect == 'space_storm':
            self.target_space_storm = SpaceStorm()
            if level >= 5:
                self.target_space_storm.intensity = 1.5
        elif special_effect == 'asteroid_field':
            self.target_asteroid_field = AsteroidField()
    
    def _smooth_ease_in_out(self, t):
        """Smooth ease-in-out transition curve"""
        # Uses a cubic bezier-like curve for ultra-smooth transition
        return t * t * t * (t * (6.0 * t - 15.0) + 10.0)
    
    def _apply_level_theme(self, level: int):
        """Apply theme settings for a specific level"""
        theme = self.level_themes.get(level, self.level_themes[1])
        
        # Adjust nebula count
        current_nebula_count = len(self.nebulae)
        target_nebula_count = theme['nebula_count']
        
        if current_nebula_count < target_nebula_count:
            for _ in range(target_nebula_count - current_nebula_count):
                self.nebulae.append(Nebula())
        elif current_nebula_count > target_nebula_count:
            self.nebulae = self.nebulae[:target_nebula_count]
        
        # Update nebula colors
        for nebula in self.nebulae:
            nebula.color = random.choice(theme['nebula_colors'])
        
        # Adjust planet count
        current_planet_count = len(self.planets)
        target_planet_count = theme['planet_count']
        
        if current_planet_count < target_planet_count:
            for _ in range(target_planet_count - current_planet_count):
                self.planets.append(Planet())
        elif current_planet_count > target_planet_count:
            self.planets = self.planets[:target_planet_count]
        
        # Handle special effects
        special_effect = theme.get('special_effect')
        
        # Clear existing effects
        self.space_storm = None
        self.asteroid_field = None
        
        # Create new effect if needed
        if special_effect == 'space_storm':
            self.space_storm = SpaceStorm()
            if level >= 5:
                self.space_storm.intensity = 1.5  # More intense for final level
        elif special_effect == 'asteroid_field':
            self.asteroid_field = AsteroidField()
    
    def update(self):
        """Update all background elements"""
        # Handle level transition
        if self.transitioning:
            current_time = pygame.time.get_ticks() / 1000.0
            elapsed = current_time - self.transition_start_time
            self.transition_progress = min(1.0, elapsed / self.transition_duration)
            
            # Use smooth easing
            smooth_progress = self._smooth_ease_in_out(self.transition_progress)
            
            if self.transition_progress >= 1.0:
                self.transitioning = False
                self.current_level = self.target_level
                self._apply_level_theme(self.current_level)
                self.buffer_needs_update = True
        
        # Update all star layers
        for star in self.stars_layer1:
            star.update()
        for star in self.stars_layer2:
            star.update()
        for star in self.stars_layer3:
            star.update()
        
        # Update current level elements
        for nebula in self.nebulae:
            nebula.update()
        for planet in self.planets:
            planet.update()
        if self.space_storm:
            self.space_storm.update()
        if self.asteroid_field:
            self.asteroid_field.update()
        
        # Update target level elements during transition
        if self.transitioning:
            for nebula in self.target_nebulae:
                nebula.update()
            for planet in self.target_planets:
                planet.update()
            if self.target_space_storm:
                self.target_space_storm.update()
            if self.target_asteroid_field:
                self.target_asteroid_field.update()
        
        # Update background color animation
        self.color_phase += self.color_speed
    
    def _render_level_background(self, surface, level, elements=None, special_effects=None, effect_alpha=255):
        """Render background for a specific level to a surface"""
        theme = self.level_themes.get(level, self.level_themes[1])
        
        # Clear surface
        surface.fill((0, 0, 0, 0))
        
        # Draw gradient background
        self._draw_level_gradient(surface, theme)
        
        # Use provided elements or current level elements
        if elements is None:
            nebulae = self.nebulae
            planets = self.planets
            space_storm = self.space_storm
            asteroid_field = self.asteroid_field
        else:
            nebulae = elements.get('nebulae', [])
            planets = elements.get('planets', [])
            space_storm = special_effects.get('space_storm') if special_effects else None
            asteroid_field = special_effects.get('asteroid_field') if special_effects else None
        
        # Draw nebulae
        for nebula in nebulae:
            nebula.draw(surface)
        
        # Draw planets
        for planet in planets:
            planet.draw(surface)
        
        # Draw special effects (before stars) with alpha support
        if asteroid_field:
            # Store original alpha
            original_alpha = getattr(asteroid_field, 'alpha', 255)
            asteroid_field.alpha = effect_alpha
            asteroid_field.draw(surface)
            # Restore original alpha
            asteroid_field.alpha = original_alpha
        
        # Draw stars with level-appropriate brightness
        brightness_factor = theme['star_brightness']
        
        for star in self.stars_layer1:
            original_brightness = star.brightness
            star.brightness = int(star.brightness * brightness_factor)
            star.draw(surface)
            star.brightness = original_brightness
            
        for star in self.stars_layer2:
            original_brightness = star.brightness
            star.brightness = int(star.brightness * brightness_factor)
            star.draw(surface)
            star.brightness = original_brightness
            
        for star in self.stars_layer3:
            original_brightness = star.brightness
            star.brightness = int(star.brightness * brightness_factor)
            star.draw(surface)
            star.brightness = original_brightness
        
        # Draw space storm on top with alpha support
        if space_storm:
            # Store original alpha
            original_alpha = getattr(space_storm, 'alpha', 255)
            space_storm.alpha = effect_alpha
            space_storm.draw(surface)
            # Restore original alpha
            space_storm.alpha = original_alpha
    
    def _draw_level_gradient(self, surface, theme):
        """Draw gradient background for a specific theme"""
        # Calculate current background colors
        phase = (math.sin(self.color_phase) + 1) * 0.5  # Normalize to 0-1
        
        # Get base colors
        colors = theme['primary_colors']
        color1 = colors[0]
        color2 = colors[1]
        
        # Interpolate between the two colors for animation
        current_color = self._interpolate_color(color1, color2, phase)
        
        # Fill background
        surface.fill(current_color)
        
        # Add vertical gradient effect with level-appropriate intensity
        level_num = list(self.level_themes.keys())[list(self.level_themes.values()).index(theme)]
        gradient_intensity = 20 if level_num <= 2 else 30
        
        height = surface.get_height()
        for y in range(0, height, 4):
            gradient_factor = y / height
            
            # Create darker gradient for higher levels
            if level_num >= 4:
                gradient_factor = gradient_factor * gradient_factor  # Quadratic darkening
            
            gradient_color = tuple(
                min(255, int(current_color[i] + gradient_factor * gradient_intensity)) 
                for i in range(3)
            )
            pygame.draw.line(surface, gradient_color, (0, y), (surface.get_width(), y), 4)
    
    def _interpolate_color(self, color1, color2, progress):
        """Interpolate between two colors"""
        return tuple(
            int(color1[i] + (color2[i] - color1[i]) * progress)
            for i in range(3)
        )
    
    def draw(self, screen):
        """Draw background using double buffering for smooth transitions"""
        # Initialize buffers if needed
        self._initialize_buffers(screen.get_size())
        
        if self.transitioning:
            # Double buffered smooth transition
            self._draw_smooth_transition(screen)
        else:
            # Single buffer normal rendering
            self._render_level_background(
                screen, 
                self.current_level,
                elements={
                    'nebulae': self.nebulae,
                    'planets': self.planets
                },
                special_effects={
                    'space_storm': self.space_storm,
                    'asteroid_field': self.asteroid_field
                }
            )
        
        # Draw level indicator overlay (always on top)
        self._draw_level_indicator(screen)
    
    def _draw_smooth_transition(self, screen):
        """Draw smooth transition between levels using double buffering"""
        smooth_progress = self._smooth_ease_in_out(self.transition_progress)
        
        # Calculate alpha values for smooth effect transitions
        current_effect_alpha = int(255 * (1.0 - smooth_progress))
        target_effect_alpha = int(255 * smooth_progress)
        
        # Render current level to buffer
        self._render_level_background(
            self.current_background_buffer,
            self.current_level,
            elements={
                'nebulae': self.nebulae,
                'planets': self.planets
            },
            special_effects={
                'space_storm': self.space_storm,
                'asteroid_field': self.asteroid_field
            },
            effect_alpha=current_effect_alpha
        )
        
        # Render target level to buffer
        self._render_level_background(
            self.target_background_buffer,
            self.target_level,
            elements={
                'nebulae': self.target_nebulae,
                'planets': self.target_planets
            },
            special_effects={
                'space_storm': self.target_space_storm,
                'asteroid_field': self.target_asteroid_field
            },
            effect_alpha=target_effect_alpha
        )
        
        # Draw current level background
        screen.blit(self.current_background_buffer, (0, 0))
        
        # Overlay target level background with alpha blending
        target_alpha = int(255 * smooth_progress)
        self.target_background_buffer.set_alpha(target_alpha)
        screen.blit(self.target_background_buffer, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
        
        # Restore target buffer alpha
        self.target_background_buffer.set_alpha(255)
    
    def _draw_level_indicator(self, screen):
        """Draw level transition indicator with improved effects"""
        if self.transitioning:
            # Smooth fade in/out calculation
            fade_factor = 1.0 - abs(self.transition_progress - 0.5) * 2
            fade_factor = max(0.0, fade_factor)
            
            # Subtle overlay instead of harsh black
            overlay_alpha = int(64 * fade_factor)  # Much more subtle
            if overlay_alpha > 0:
                overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
                overlay.fill((0, 0, 20, overlay_alpha))  # Dark blue tint
                screen.blit(overlay, (0, 0))
            
            # Level text with smooth animation
            target_theme = self.level_themes.get(self.target_level, self.level_themes[1])
            
            # Text fade effect
            text_alpha = int(255 * fade_factor)
            if text_alpha > 0:
                # Main level text
                font = pygame.font.Font(None, 72)
                text = font.render(f"Level {self.target_level}", True, WHITE)
                text.set_alpha(text_alpha)
                
                # Description text
                desc_font = pygame.font.Font(None, 48)
                desc_text = desc_font.render(target_theme['description'], True, WHITE)
                desc_text.set_alpha(text_alpha)
                
                # Center positioning
                screen_center = (screen.get_width() // 2, screen.get_height() // 2)
                text_rect = text.get_rect(center=(screen_center[0], screen_center[1] - 50))
                desc_rect = desc_text.get_rect(center=(screen_center[0], screen_center[1] + 20))
                
                # Add subtle glow effect
                if text_alpha > 128:
                    glow_alpha = text_alpha // 3
                    glow_text = font.render(f"Level {self.target_level}", True, (100, 150, 255))
                    glow_text.set_alpha(glow_alpha)
                    
                    # Draw glow slightly offset
                    for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
                        glow_rect = text_rect.copy()
                        glow_rect.x += dx
                        glow_rect.y += dy
                        screen.blit(glow_text, glow_rect)
                
                # Draw main text
                screen.blit(text, text_rect)
                screen.blit(desc_text, desc_rect) 