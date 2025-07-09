import pygame
import random
import math
from thunder_fighter.constants import WIDTH, HEIGHT, PLAYER_MAX_SPEED, BULLET_SPEED_MAX, BULLET_PATHS_MAX
from thunder_fighter.graphics.renderers import create_health_item, create_bullet_speed_item, create_bullet_path_item, create_player_speed_item, create_wingman_item
from thunder_fighter.utils.logger import logger

class HealthItem(pygame.sprite.Sprite):
    """Health item class"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = create_health_item()
        self.rect = self.image.get_rect()
        # Generate at random position at top of screen
        self.rect.x = random.randrange(30, WIDTH - 30)
        self.rect.y = -30
        self.speedy = 2  # Vertical falling speed
        # Add horizontal swinging effect
        self.direction = random.choice([-1, 1])
        self.angle = random.randrange(360)
        self.type = "health"  # Item type identifier
        
    def update(self):
        """Update item position"""
        # Vertical movement
        self.rect.y += self.speedy
        
        # Horizontal swinging
        self.angle = (self.angle + 2) % 360
        self.rect.x += self.direction * math.sin(math.radians(self.angle)) * 0.5
        
        # Ensure item doesn't go off screen edges
        if self.rect.left < 0:
            self.rect.left = 0
            self.direction = 1
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.direction = -1
            
        # Remove item if it goes off bottom of screen
        if self.rect.top > HEIGHT:
            self.kill()

class BulletSpeedItem(pygame.sprite.Sprite):
    """Bullet speed boost item class"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = create_bullet_speed_item()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(30, WIDTH - 30)
        self.rect.y = -30
        self.speedy = 2.5  # Slightly faster than normal items
        self.direction = random.choice([-1, 1])
        self.angle = random.randrange(360)
        self.type = "bullet_speed"  # Item type identifier
        
        # Bullet speed increase amount
        self.speed_increase = random.randint(1, 3)
        
    def update(self):
        """Update item position"""
        self.rect.y += self.speedy
        
        # More pronounced horizontal swinging
        self.angle = (self.angle + 3) % 360
        self.rect.x += self.direction * math.sin(math.radians(self.angle)) * 0.8
        
        # Boundary check
        if self.rect.left < 0:
            self.rect.left = 0
            self.direction = 1
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.direction = -1
            
        # Off-screen check
        if self.rect.top > HEIGHT:
            self.kill()

class BulletPathItem(pygame.sprite.Sprite):
    """Bullet path increase item class"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = create_bullet_path_item()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(30, WIDTH - 30)
        self.rect.y = -30
        self.speedy = 1.5  # Slower falling speed
        self.direction = random.choice([-1, 1])
        self.angle = random.randrange(360)
        self.type = "bullet_path"  # Item type identifier
        
    def update(self):
        """Update item position"""
        self.rect.y += self.speedy
        
        # More complex movement pattern
        self.angle = (self.angle + 2) % 360
        self.rect.x += self.direction * math.sin(math.radians(self.angle * 1.5)) * 1.0
        
        # Boundary check
        if self.rect.left < 0:
            self.rect.left = 0
            self.direction = 1
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.direction = -1
            
        # Off-screen check
        if self.rect.top > HEIGHT:
            self.kill()

class PlayerSpeedItem(pygame.sprite.Sprite):
    """Player speed boost item class"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = create_player_speed_item()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(30, WIDTH - 30)
        self.rect.y = -30
        self.speedy = 2.2 # Slightly different speed
        self.direction = random.choice([-1, 1])
        self.angle = random.randrange(360)
        self.type = "player_speed" # Item type identifier
        
        # Player speed increase amount (can be fixed or random)
        self.speed_increase = 1 

    def update(self):
        """Update item position"""
        self.rect.y += self.speedy
        
        # Slightly different horizontal swinging
        self.angle = (self.angle + 2.5) % 360
        self.rect.x += self.direction * math.sin(math.radians(self.angle)) * 0.6
        
        # Boundary check
        if self.rect.left < 0:
            self.rect.left = 0
            self.direction = 1
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.direction = -1
            
        # Off-screen check
        if self.rect.top > HEIGHT:
            self.kill()

class WingmanItem(pygame.sprite.Sprite):
    """Wingman item class"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = create_wingman_item()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(30, WIDTH - 30)
        self.rect.y = -30
        self.speedy = 2.0
        self.direction = random.choice([-1, 1])
        self.angle = random.randrange(360)
        self.type = "wingman"

    def update(self):
        """Update item position"""
        self.rect.y += self.speedy
        
        self.angle = (self.angle + 1) % 360
        self.rect.x += self.direction * math.sin(math.radians(self.angle)) * 1.2
        
        if self.rect.left < 0:
            self.rect.left = 0
            self.direction = 1
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.direction = -1
            
        if self.rect.top > HEIGHT:
            self.kill()

def create_random_item(game_time, game_level, all_sprites, items_group, player):
    """Create items dynamically based on game time and player status"""

    weights = {
        HealthItem: 15,
        PlayerSpeedItem: 10,
        BulletSpeedItem: 10,
        BulletPathItem: 5,
        WingmanItem: 3,
    }

    # Dynamically adjust weights
    if player.health >= 100:
        weights[HealthItem] = 1  # Greatly reduce health recovery item weight
    if player.speed >= 10:
        weights[PlayerSpeedItem] = 1
    if player.bullet_speed >= 15:
        weights[BulletSpeedItem] = 1
    if player.bullet_paths >= 3:
        weights[BulletPathItem] = 1
    if len(player.wingmen_list) >= 2:
        weights[WingmanItem] = 0

    # Wingman items only appear after level 3
    if game_level < 3:
        weights[WingmanItem] = 0
        
    # Filter out items with zero weight
    available_items = {item: weight for item, weight in weights.items() if weight > 0}
    if not available_items:
        return None

    item_classes = list(available_items.keys())
    item_weights = list(available_items.values())

    # Randomly select an item type based on weights
    chosen_item_class = random.choices(item_classes, weights=item_weights, k=1)[0]
    
    # Create item instance
    item = chosen_item_class()
    all_sprites.add(item)
    items_group.add(item)
    
    logger.info(f"Created item: {item.type} at level {game_level}")
    return item 