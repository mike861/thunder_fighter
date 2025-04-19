import pygame
import random
import math
from thunder_fighter.constants import WIDTH, HEIGHT
<<<<<<< HEAD
from thunder_fighter.graphics.renderers import create_health_item, create_bullet_speed_item, create_bullet_path_item
=======
from thunder_fighter.graphics.renderers import create_health_item, create_bullet_speed_item, create_bullet_path_item, create_player_speed_item
>>>>>>> origin/init
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

<<<<<<< HEAD
=======
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

>>>>>>> origin/init
def create_random_item(game_time, all_sprites, items_group):
    """Creates a random item based on game time and adds it to groups."""
    # Probabilities based on game time (adjust as needed)
    time_factor = min(1.0, game_time / 10.0) # Max probability reached after 10 mins
    
<<<<<<< HEAD
    prob_health = 0.4 + 0.1 * time_factor
    prob_speed = 0.3 + 0.1 * time_factor
    prob_path = 0.3 + 0.1 * time_factor
    
    # Normalize probabilities
    total_prob = prob_health + prob_speed + prob_path
    prob_health /= total_prob
    prob_speed /= total_prob
    # prob_path = 1.0 - prob_health - prob_speed # Ensure sum is 1
=======
    # Add probability for the new player speed item
    prob_health = 0.35 + 0.1 * time_factor
    prob_bullet_speed = 0.25 + 0.1 * time_factor
    prob_bullet_path = 0.20 + 0.1 * time_factor
    prob_player_speed = 0.20 + 0.05 * time_factor # New item probability
    
    # Normalize probabilities
    total_prob = prob_health + prob_bullet_speed + prob_bullet_path + prob_player_speed
    prob_health /= total_prob
    prob_bullet_speed /= total_prob
    prob_bullet_path /= total_prob
    prob_player_speed /= total_prob # Normalize new probability
>>>>>>> origin/init

    rand_val = random.random()
    x = random.randrange(50, WIDTH - 50)
    y = random.randrange(-100, -50)
    item_type = "unknown"
    item = None

    if rand_val < prob_health:
        item_type = 'health'
        item = HealthItem()
<<<<<<< HEAD
    elif rand_val < prob_health + prob_speed:
        item_type = 'bullet_speed'
        # Assign a speed increase value (can be randomized or fixed)
        speed_increase = 1 + random.randint(0, 1) # Increase speed by 1 or 2
        item = BulletSpeedItem()
    else:
        item_type = 'bullet_path'
        item = BulletPathItem()
=======
    elif rand_val < prob_health + prob_bullet_speed:
        item_type = 'bullet_speed'
        item = BulletSpeedItem()
    elif rand_val < prob_health + prob_bullet_speed + prob_bullet_path:
        item_type = 'bullet_path'
        item = BulletPathItem()
    else: # The remaining probability is for player_speed
        item_type = 'player_speed'
        item = PlayerSpeedItem()
>>>>>>> origin/init
        
    if item:
        all_sprites.add(item)
        items_group.add(item)
<<<<<<< HEAD
        # Log item creation (changed from print)
        logger.info(f"Created random item: Type='{item_type}', Pos=({x}, {y})")
=======
        logger.info(f"Created random item: Type='{item_type}', Pos=({item.rect.centerx}, {item.rect.centery})")
>>>>>>> origin/init
    else:
        logger.warning("Failed to create random item.")
    
    return item 