"""
UI Manager Module

This module provides the main UI Manager for the Thunder Fighter game.
The UI system uses a modular component-based architecture following the single responsibility principle.

Components include:
- HealthBarComponent: Draws health bars
- NotificationManager: Manages game notifications
- GameInfoDisplay: Shows score, level, and time
- PlayerStatsDisplay: Displays player statistics
- BossStatusDisplay: Shows boss health and status
- ScreenOverlayManager: Manages special screens (pause, victory, game over)
- DevInfoDisplay: Developer debug information
"""

# Import and re-export the refactored UIManager
from thunder_fighter.graphics.ui_manager_refactored import UIManager

# For backwards compatibility, also re-export the original PlayerUIManager name
PlayerUIManager = UIManager

__all__ = ['UIManager', 'PlayerUIManager'] 