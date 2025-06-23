"""
UI Manager Module

This module provides backwards compatibility by re-exporting the refactored UIManager.
The original monolithic UIManager has been replaced with a modular component-based approach.

The original implementation has been preserved in ui_manager_original.py for reference.
"""

# Import and re-export the refactored UIManager
from thunder_fighter.graphics.ui_manager_refactored import UIManager

# For backwards compatibility, also re-export the original PlayerUIManager name
PlayerUIManager = UIManager

__all__ = ['UIManager', 'PlayerUIManager'] 