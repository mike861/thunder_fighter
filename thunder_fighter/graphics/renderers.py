import pygame
import os
from thunder_fighter.constants import *

def load_image(name, colorkey=None):
    """Load an image and return its surface using resource manager"""
    from thunder_fighter.utils.resource_manager import get_resource_manager
    
    resource_manager = get_resource_manager()
    
    try:
        # Use resource manager to load image with caching
        image = resource_manager.load_image(name, colorkey=colorkey, alpha=False)
        return image
    except Exception as e:
        print(f'Cannot load image: {name} - {e}')
        # Create fallback placeholder
        placeholder = pygame.Surface((32, 32))
        placeholder.fill((255, 0, 255))  # Magenta placeholder
        return placeholder

def create_player_surface():
    """Create player aircraft surface with modern fighter jet design"""
    # Keep improved size: 60x50
    surface = pygame.Surface((60, 50))
    surface.set_colorkey((0, 0, 0))  # Set black as transparent
    
    # Color scheme for player fighter jet
    main_color = (120, 170, 255)     # Light blue main body
    secondary_color = (80, 130, 220)  # Darker blue for details
    accent_color = (200, 220, 255)    # Light blue accents
    engine_color = (255, 120, 100)    # Orange-red engines
    
    # Draw main fuselage (sleeker fighter design)
    fuselage_points = [(30, 5), (25, 15), (27, 38), (33, 38), (35, 15)]
    pygame.draw.polygon(surface, main_color, fuselage_points)
    
    # Draw nose cone (pointed for speed)
    nose_points = [(30, 5), (27, 12), (33, 12)]
    pygame.draw.polygon(surface, accent_color, nose_points)
    
    # Draw swept wings (modern fighter style)
    left_wing = [(8, 28), (27, 22), (27, 32), (12, 38)]
    right_wing = [(52, 28), (33, 22), (33, 32), (48, 38)]
    pygame.draw.polygon(surface, secondary_color, left_wing)
    pygame.draw.polygon(surface, secondary_color, right_wing)
    
    # Draw wing tips with accent color
    pygame.draw.polygon(surface, accent_color, [(8, 28), (12, 30), (15, 35), (12, 38)])
    pygame.draw.polygon(surface, accent_color, [(52, 28), (48, 30), (45, 35), (48, 38)])
    
    # Draw rear stabilizers (tail fins)
    left_stabilizer = [(24, 38), (20, 48), (27, 42)]
    right_stabilizer = [(36, 38), (40, 48), (33, 42)]
    pygame.draw.polygon(surface, main_color, left_stabilizer)
    pygame.draw.polygon(surface, main_color, right_stabilizer)
    
    # Draw cockpit canopy (more realistic)
    pygame.draw.ellipse(surface, (60, 100, 150), (26, 14, 8, 12))  # Dark canopy
    pygame.draw.ellipse(surface, (150, 180, 220), (27, 15, 6, 8))   # Reflection
    pygame.draw.ellipse(surface, (200, 220, 255), (28, 16, 4, 4))   # Highlight
    
    # Draw twin engines with glow
    pygame.draw.circle(surface, engine_color, (24, 42), 3)  # Left engine
    pygame.draw.circle(surface, engine_color, (36, 42), 3)  # Right engine
    # Engine afterburner glow
    pygame.draw.circle(surface, (255, 200, 150), (24, 42), 2)
    pygame.draw.circle(surface, (255, 200, 150), (36, 42), 2)
    pygame.draw.circle(surface, (255, 255, 200), (24, 42), 1)
    pygame.draw.circle(surface, (255, 255, 200), (36, 42), 1)
    
    # Add air intakes
    pygame.draw.ellipse(surface, secondary_color, (22, 25, 4, 6))
    pygame.draw.ellipse(surface, secondary_color, (34, 25, 4, 6))
    
    # Add weapon hardpoints (small details)
    pygame.draw.circle(surface, accent_color, (15, 32), 1)
    pygame.draw.circle(surface, accent_color, (45, 32), 1)
    
    # Strong outline for visibility
    # Black shadow outline
    pygame.draw.lines(surface, (0, 0, 0), True, fuselage_points, 3)
    pygame.draw.lines(surface, (0, 0, 0), True, left_wing, 2)
    pygame.draw.lines(surface, (0, 0, 0), True, right_wing, 2)
    
    # White highlight outline
    pygame.draw.lines(surface, (255, 255, 255), True, fuselage_points, 1)
    pygame.draw.lines(surface, (255, 255, 255), True, left_wing, 1)
    pygame.draw.lines(surface, (255, 255, 255), True, right_wing, 1)
    
    # Add detail lines for realism
    pygame.draw.line(surface, (255, 255, 255), (30, 5), (30, 15), 1)    # Nose stripe
    pygame.draw.line(surface, accent_color, (27, 22), (33, 22), 1)       # Wing root
    pygame.draw.line(surface, accent_color, (24, 38), (36, 38), 1)       # Rear line
    
    return surface

def create_enemy_surface(level=0):
    """Create enemy aircraft surface with fighter jet appearance based on level"""
    # Keep the improved size: 40x50
    surface = pygame.Surface((40, 50))
    surface.set_colorkey((0, 0, 0))  # Set black as transparent
    
    # Choose color scheme based on level
    if level < 3:
        # Low level enemies: red/dark red
        main_color = (220, 50, 50)  # Brighter red
        secondary_color = (150, 30, 30)  # Dark red
        accent_color = (255, 100, 100)  # Light red
        glow_color = None
    elif level < 6:
        # Medium level enemies: orange/yellow
        main_color = (255, 140, 0)  # Orange
        secondary_color = (200, 80, 0)  # Dark orange
        accent_color = (255, 200, 0)  # Yellow
        glow_color = (255, 200, 0, 100)  # Glow effect
    elif level < 9:
        # High level enemies: blue/cyan
        main_color = (30, 144, 255)  # Dodge blue
        secondary_color = (20, 80, 180)  # Dark blue
        accent_color = (100, 200, 255)  # Light blue
        glow_color = (0, 191, 255, 120)  # Sky blue glow
    else:
        # Super high level enemies: purple/magenta
        main_color = (160, 50, 200)  # Purple
        secondary_color = (100, 20, 130)  # Dark purple
        accent_color = (220, 100, 255)  # Light purple
        glow_color = (186, 85, 211, 150)  # Purple glow
    
    # Draw main fuselage (fighter jet body)
    fuselage_points = [(20, 5), (16, 15), (18, 35), (22, 35), (24, 15)]
    pygame.draw.polygon(surface, main_color, fuselage_points)
    
    # Draw nose cone
    nose_points = [(20, 5), (18, 12), (22, 12)]
    pygame.draw.polygon(surface, accent_color, nose_points)
    
    # Draw main wings (delta wing design)
    left_wing = [(5, 25), (18, 20), (18, 30), (8, 35)]
    right_wing = [(35, 25), (22, 20), (22, 30), (32, 35)]
    pygame.draw.polygon(surface, secondary_color, left_wing)
    pygame.draw.polygon(surface, secondary_color, right_wing)
    
    # Draw rear stabilizers
    left_stabilizer = [(15, 35), (12, 45), (18, 40)]
    right_stabilizer = [(25, 35), (28, 45), (22, 40)]
    pygame.draw.polygon(surface, main_color, left_stabilizer)
    pygame.draw.polygon(surface, main_color, right_stabilizer)
    
    # Draw cockpit canopy
    pygame.draw.ellipse(surface, (80, 80, 120), (17, 12, 6, 8))  # Dark blue canopy
    pygame.draw.ellipse(surface, (120, 120, 160), (18, 13, 4, 6))  # Lighter reflection
    
    # Draw engines/exhausts
    pygame.draw.circle(surface, (200, 100, 100), (15, 42), 3)  # Left engine
    pygame.draw.circle(surface, (200, 100, 100), (25, 42), 3)  # Right engine
    pygame.draw.circle(surface, (255, 150, 150), (15, 42), 1)  # Engine glow
    pygame.draw.circle(surface, (255, 150, 150), (25, 42), 1)  # Engine glow
    
    # Add glow effect for high level enemies (simplified to avoid black shadows)
    if level >= 4 and glow_color:
        # Instead of complex glow, add simple bright outline effect
        glow_rgb = glow_color[:3]  # Extract RGB without alpha
        
        # Draw multiple colored outlines for glow effect
        pygame.draw.lines(surface, glow_rgb, True, fuselage_points, 1)
        pygame.draw.lines(surface, glow_rgb, True, left_wing, 1)
        pygame.draw.lines(surface, glow_rgb, True, right_wing, 1)
        
        # Add bright spots at key points for energy effect
        pygame.draw.circle(surface, glow_rgb, (20, 8), 2, 1)   # Nose glow
        pygame.draw.circle(surface, glow_rgb, (15, 42), 4, 1)  # Left engine glow
        pygame.draw.circle(surface, glow_rgb, (25, 42), 4, 1)  # Right engine glow
    
    # Add level-specific details
    if level >= 5:
        # Weapon hardpoints
        pygame.draw.circle(surface, accent_color, (10, 28), 2)
        pygame.draw.circle(surface, accent_color, (30, 28), 2)
    
    if level >= 7:
        # Extra armor plating
        pygame.draw.rect(surface, secondary_color, (17, 8, 6, 4))
        # Sensor array
        pygame.draw.circle(surface, accent_color, (20, 10), 1)
    
    if level >= 9:
        # Advanced features - energy weapons
        pygame.draw.line(surface, (255, 255, 100), (20, 5), (20, 12), 2)
        # Thruster enhancement
        pygame.draw.circle(surface, (255, 255, 0), (15, 42), 4)
        pygame.draw.circle(surface, (255, 255, 0), (25, 42), 4)
    
    # Strong outline for visibility against background
    # Black outline first (shadow effect)
    pygame.draw.lines(surface, (0, 0, 0), True, fuselage_points, 2)
    pygame.draw.lines(surface, (0, 0, 0), True, left_wing, 2)
    pygame.draw.lines(surface, (0, 0, 0), True, right_wing, 2)
    
    # White highlight outline
    pygame.draw.lines(surface, (255, 255, 255), True, fuselage_points, 1)
    pygame.draw.lines(surface, (255, 255, 255), True, left_wing, 1)
    pygame.draw.lines(surface, (255, 255, 255), True, right_wing, 1)
    
    # Add level indicator (small dots at bottom)
    for i in range(min(3, (level + 2) // 3)):
        dot_x = 16 + i * 4
        pygame.draw.circle(surface, (255, 255, 255), (dot_x, 47), 1)
        pygame.draw.circle(surface, accent_color, (dot_x, 47), 1)
    
    return surface

def create_boss_surface(level=1):
    """Create BOSS aircraft surface with different appearance based on level"""
    # Create a surface with size 100x80
    surface = pygame.Surface((100, 80), pygame.SRCALPHA)
    
    # Choose color based on level
    if level == 1:
        # 1st Boss: purple series
        main_color = PURPLE
        secondary_color = MAGENTA
        detail_color = RED
        engine_color = ORANGE
        cockpit_color = CYAN
    elif level == 2:
        # 2nd Boss: blue series
        main_color = BLUE
        secondary_color = DARK_BLUE
        detail_color = CYAN
        engine_color = LIGHT_BLUE
        cockpit_color = WHITE
    else:
        # 3rd Boss: red series
        main_color = RED
        secondary_color = DARK_RED
        detail_color = ORANGE
        engine_color = YELLOW
        cockpit_color = LIGHT_BLUE
    
    # Draw BOSS aircraft body
    points = [(50, 10), (10, 50), (90, 50)]
    pygame.draw.polygon(surface, main_color, points)
    
    # Draw BOSS aircraft bottom
    pygame.draw.rect(surface, secondary_color, (20, 50, 60, 30))
    
    # Draw multiple wings
    pygame.draw.polygon(surface, detail_color, [(0, 40), (20, 35), (10, 55)])
    pygame.draw.polygon(surface, detail_color, [(100, 40), (80, 35), (90, 55)])
    pygame.draw.polygon(surface, engine_color, [(10, 60), (25, 50), (30, 70)])
    pygame.draw.polygon(surface, engine_color, [(90, 60), (75, 50), (70, 70)])
    
    # Draw multiple engines
    pygame.draw.rect(surface, engine_color, (30, 75, 10, 5))
    pygame.draw.rect(surface, engine_color, (60, 75, 10, 5))
    pygame.draw.rect(surface, YELLOW, (45, 70, 10, 10))
    
    # Draw main cockpit
    pygame.draw.ellipse(surface, cockpit_color, (40, 20, 20, 20))
    pygame.draw.ellipse(surface, WHITE, (45, 25, 10, 10))
    
    # Add decoration details
    pygame.draw.circle(surface, YELLOW, (50, 50), 8)
    pygame.draw.circle(surface, WHITE, (50, 50), 3)
    
    # Add level-specific features
    if level >= 2:
        # 2nd level and above Bosses have extra cannons
        pygame.draw.rect(surface, detail_color, (15, 45, 5, 10))
        pygame.draw.rect(surface, detail_color, (80, 45, 5, 10))
        
    if level >= 3:
        # 3rd Boss has extra armor and energy core
        pygame.draw.rect(surface, secondary_color, (35, 30, 30, 5))
        pygame.draw.circle(surface, YELLOW, (50, 50), 12)
        pygame.draw.circle(surface, WHITE, (50, 50), 6)
        
        # Simplify glow effect to avoid transparency mixing issues
        # Draw circle directly on the current surface
        for radius in range(25, 15, -2):
            # Use decreasing alpha values to create gradient glow effect
            alpha = max(10, 70 - (25 - radius) * 5)
            glow_color = (255, 255, 0, alpha)
            # Create a separate surface for glow effect
            glow_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, glow_color, (radius, radius), radius)
            # Draw glow effect on main surface, position centered
            surface.blit(glow_surf, (50 - radius, 50 - radius))
    
    # Add edge lines
    pygame.draw.lines(surface, DARK_BLUE, True, points, 2)
    pygame.draw.rect(surface, DARK_BLUE, (20, 50, 60, 30), 2)
    
    # Level indicator
    for i in range(level):
        pygame.draw.circle(surface, WHITE, (85 - i*7, 65), 3)
    
    return surface

def create_bullet():
    """Create bullet surface"""
    # Create a surface with size 5x15
    bullet_surface = pygame.Surface((5, 15), pygame.SRCALPHA)
    
    # Draw bullet
    pygame.draw.rect(bullet_surface, YELLOW, (0, 0, 5, 10))
    pygame.draw.rect(bullet_surface, ORANGE, (0, 10, 5, 5))
    
    # Add glow effect
    pygame.draw.line(bullet_surface, WHITE, (2, 0), (2, 7), 1)
    
    return bullet_surface

def create_boss_bullet():
    """Create BOSS bullet surface"""
    # Create a surface with size 10x20
    bullet_surface = pygame.Surface((10, 20), pygame.SRCALPHA)
    
    # Draw BOSS bullet
    pygame.draw.rect(bullet_surface, MAGENTA, (0, 0, 10, 15))
    pygame.draw.rect(bullet_surface, PURPLE, (0, 15, 10, 5))
    
    # Add glow effect
    pygame.draw.line(bullet_surface, WHITE, (5, 0), (5, 10), 2)
    
    return bullet_surface

def create_health_item():
    """Create health item surface"""
    # Create a surface with size 30x30
    item_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
    
    # Draw circular background
    pygame.draw.circle(item_surface, PINK, (15, 15), 15)
    
    # Draw cross
    pygame.draw.rect(item_surface, RED, (5, 12, 20, 6))
    pygame.draw.rect(item_surface, RED, (12, 5, 6, 20))
    
    # Add white edge
    pygame.draw.circle(item_surface, WHITE, (15, 15), 15, 2)
    
    return item_surface

def create_bullet_speed_item():
    """Create bullet speed boost item surface"""
    # Create a surface with size 30x30
    item_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
    
    # Draw circular background
    pygame.draw.circle(item_surface, LIGHT_BLUE, (15, 15), 15)
    
    # Draw internal pattern - lightning shape
    lightning_points = [
        (10, 5), (20, 5), (15, 12), 
        (20, 12), (10, 25), (15, 18), 
        (10, 18)
    ]
    pygame.draw.polygon(item_surface, YELLOW, lightning_points)
    
    # Add glow effect
    glow_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(glow_surface, (0, 191, 255, 70), (20, 20), 18)
    item_surface.blit(glow_surface, (-5, -5), special_flags=pygame.BLEND_ALPHA_SDL2)
    
    # Add white edge
    pygame.draw.circle(item_surface, WHITE, (15, 15), 15, 2)
    
    return item_surface

def create_bullet_path_item():
    """Create bullet path boost item surface"""
    # Create a surface with size 30x30
    item_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
    
    # Draw circular background
    pygame.draw.circle(item_surface, GREEN, (15, 15), 15)
    
    # Draw internal pattern - multiple path patterns
    # Center point
    pygame.draw.circle(item_surface, WHITE, (15, 20), 3)
    
    # Path lines
    pygame.draw.line(item_surface, WHITE, (15, 20), (15, 5), 2)
    pygame.draw.line(item_surface, WHITE, (15, 20), (8, 5), 2)
    pygame.draw.line(item_surface, WHITE, (15, 20), (22, 5), 2)
    
    # Path end points
    pygame.draw.circle(item_surface, YELLOW, (15, 5), 2)
    pygame.draw.circle(item_surface, YELLOW, (8, 5), 2)
    pygame.draw.circle(item_surface, YELLOW, (22, 5), 2)
    
    # Add glow effect
    glow_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(glow_surface, (100, 255, 100, 70), (20, 20), 18)
    item_surface.blit(glow_surface, (-5, -5), special_flags=pygame.BLEND_ALPHA_SDL2)
    
    # Add white edge
    pygame.draw.circle(item_surface, WHITE, (15, 15), 15, 2)
    
    return item_surface

def create_player_speed_item():
    """Create player speed boost item surface"""
    item_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
    
    # Draw circular background (green series)
    pygame.draw.circle(item_surface, (0, 200, 0), (15, 15), 15)
    
    # Draw internal pattern - upward arrow
    arrow_points = [
        (15, 5),  # Arrow top
        (22, 15), # Right shoulder
        (18, 15), # Right neck
        (18, 25), # Right bottom
        (12, 25), # Left bottom
        (12, 15), # Left neck
        (8, 15)   # Left shoulder
    ]
    pygame.draw.polygon(item_surface, WHITE, arrow_points)
    
    # Add glow effect
    glow_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(glow_surface, (100, 255, 100, 70), (20, 20), 18)
    item_surface.blit(glow_surface, (-5, -5), special_flags=pygame.BLEND_ALPHA_SDL2)
    
    # Add white edge
    pygame.draw.circle(item_surface, WHITE, (15, 15), 15, 2)
    
    return item_surface

def create_wingman():
    """Create wingman surface"""
    wingman_surface = pygame.Surface((20, 25), pygame.SRCALPHA)
    
    # Body
    pygame.draw.polygon(wingman_surface, (0, 180, 255), [(10, 0), (0, 25), (20, 25)])
    # Details
    pygame.draw.polygon(wingman_surface, (200, 200, 200), [(10, 5), (5, 20), (15, 20)])
    
    return wingman_surface

def create_tracking_missile():
    """Creates the surface for a tracking missile."""
    missile_surface = pygame.Surface((6, 12), pygame.SRCALPHA)
    pygame.draw.rect(missile_surface, ORANGE, (0, 0, 6, 9))
    pygame.draw.polygon(missile_surface, RED, [(0, 9), (6, 9), (3, 12)])
    pygame.draw.line(missile_surface, YELLOW, (3, 0), (3, 7), 1)
    return missile_surface

def create_wingman_item():
    """Creates the surface for a wingman power-up item."""
    item_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
    
    # Background
    pygame.draw.circle(item_surface, (255, 255, 255), (15, 15), 15)
    pygame.draw.circle(item_surface, (0, 180, 255), (15, 15), 15, 2)

    # Draw wingman icon
    wingman_icon = create_wingman()
    wingman_icon = pygame.transform.scale(wingman_icon, (18, 22))
    
    rect = wingman_icon.get_rect(center=(15, 15))
    item_surface.blit(wingman_icon, rect)
    
    return item_surface

def draw_health_bar(surface, x, y, width, height, health, max_health, border_color=WHITE):
    """Draw health bar"""
    # Health bar background
    pygame.draw.rect(surface, DARK_GRAY, (x, y, width, height))
    
    # Calculate current health bar width based on health
    health_width = int(health / max_health * width)
    
    # Change health bar color based on health
    if health > max_health * 0.6:
        color = GREEN
    elif health > max_health * 0.3:
        color = YELLOW
    else:
        color = RED
        
    # Draw health bar
    pygame.draw.rect(surface, color, (x, y, health_width, height))
    
    # Draw health bar border
    pygame.draw.rect(surface, border_color, (x, y, width, height), 1)

def draw_text(surface, text, size, x, y, color=WHITE, font_name='arial'):
    """Draw text on surface using resource manager"""
    from thunder_fighter.utils.resource_manager import get_resource_manager
    
    resource_manager = get_resource_manager()
    
    try:
        # Use resource manager to load font with caching
        font = resource_manager.load_font(font_name, size, system_font=True)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        surface.blit(text_surface, text_rect)
    except Exception as e:
        print(f"Error rendering text: {e}")
        # Fallback to default font
        try:
            font = resource_manager.load_font(None, size, system_font=True)
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect()
            text_rect.midtop = (x, y)
            surface.blit(text_surface, text_rect)
        except Exception as fallback_error:
            print(f"Fallback font also failed: {fallback_error}")

# Function aliases for backward compatibility
create_player_ship = create_player_surface
create_enemy_ship = create_enemy_surface  
create_boss_ship = create_boss_surface