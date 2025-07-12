"""
Flash Effects System

Handles flash effects for entities including damage flash, power-up flash, etc.
"""

import pygame

from thunder_fighter.constants import WHITE


class FlashEffect:
    """Flash effect that modifies entity's color directly"""
    def __init__(self, entity, color=WHITE, duration=200, flash_speed=50):
        self.entity = entity  # The sprite to flash
        self.color = color
        self.duration = duration
        self.creation_time = pygame.time.get_ticks()
        self.flash_speed = flash_speed  # Flash frequency in milliseconds
        self.last_flash = self.creation_time
        self.is_flashing = True
        self.active = True

        # Store original image to restore later
        if hasattr(entity, 'image'):
            self.original_image = entity.image.copy()
        else:
            self.original_image = None

    def update(self):
        """Update flash effect on the entity"""
        if not self.active or not self.entity.alive():
            self.stop()
            return False

        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.creation_time

        # Check if effect should end
        if elapsed > self.duration:
            self.stop()
            return False

        # Toggle flash
        if current_time - self.last_flash > self.flash_speed:
            self.is_flashing = not self.is_flashing
            self.last_flash = current_time

            if self.is_flashing and self.original_image:
                # Apply color overlay
                flash_image = self.original_image.copy()
                flash_image.fill(self.color, special_flags=pygame.BLEND_ADD)
                self.entity.image = flash_image
            elif self.original_image:
                # Restore original
                self.entity.image = self.original_image.copy()

        return True

    def stop(self):
        """Stop the flash effect and restore original image"""
        self.active = False
        if self.original_image and hasattr(self.entity, 'image'):
            self.entity.image = self.original_image.copy()


class FlashEffectManager:
    """Manages flash effects for entities"""
    def __init__(self):
        self.effects = []

    def add_flash(self, entity, color=WHITE, duration=200):
        """Add a flash effect to an entity"""
        # Remove any existing flash effect for this entity
        self.effects = [e for e in self.effects if e.entity != entity]

        # Create new flash effect
        effect = FlashEffect(entity, color, duration)
        self.effects.append(effect)

    def update(self):
        """Update all flash effects"""
        # Update effects and remove inactive ones
        self.effects = [effect for effect in self.effects if effect.update()]

    def clear(self):
        """Clear all flash effects"""
        for effect in self.effects:
            effect.stop()
        self.effects.clear()


# Global flash effect manager
flash_manager = FlashEffectManager()


def create_flash_effect(entity, color=WHITE, duration=200):
    """Create a flash effect on an entity"""
    flash_manager.add_flash(entity, color, duration)
