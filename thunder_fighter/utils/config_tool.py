#!/usr/bin/env python3
"""
Thunder Fighter Configuration Tool

A command-line utility for managing game configuration settings.
"""

import argparse
import sys
import json
from thunder_fighter.utils.config_manager import config_manager

def show_config():
    """Display current configuration"""
    print("Thunder Fighter Configuration")
    print("=" * 40)
    print(f"Configuration file: {config_manager.config_file}")
    print()
    
    print("Sound Settings:")
    print(f"  Music Volume: {config_manager.sound.music_volume}")
    print(f"  Sound Volume: {config_manager.sound.sound_volume}")
    print(f"  Music Enabled: {config_manager.sound.music_enabled}")
    print(f"  Sound Enabled: {config_manager.sound.sound_enabled}")
    print()
    
    print("Display Settings:")
    print(f"  Fullscreen: {config_manager.display.fullscreen}")
    print(f"  Screen Scaling: {config_manager.display.screen_scaling}")
    print(f"  Width: {config_manager.display.width}")
    print(f"  Height: {config_manager.display.height}")
    print()
    
    print("Gameplay Settings:")
    print(f"  Difficulty: {config_manager.gameplay.difficulty}")
    print(f"  Initial Lives: {config_manager.gameplay.initial_lives}")
    print()
    
    print("Controls:")
    print(f"  Move Left: {config_manager.controls.move_left}")
    print(f"  Move Right: {config_manager.controls.move_right}")
    print(f"  Move Up: {config_manager.controls.move_up}")
    print(f"  Move Down: {config_manager.controls.move_down}")
    print(f"  Shoot: {config_manager.controls.shoot}")
    print(f"  Pause: {config_manager.controls.pause}")
    print()
    
    print("Debug Settings:")
    print(f"  Dev Mode: {config_manager.debug.dev_mode}")
    print(f"  Log Level: {config_manager.debug.log_level}")

def set_config(section, key, value):
    """Set a configuration value"""
    try:
        # Parse the value to appropriate type
        if value.lower() in ('true', 'false'):
            value = value.lower() == 'true'
        elif value.replace('.', '').isdigit():
            value = float(value) if '.' in value else int(value)
        elif value.startswith('[') and value.endswith(']'):
            # Parse list (e.g., "[LEFT, a]")
            value = [item.strip().strip('"\'') for item in value[1:-1].split(',')]
        
        # Set the value
        section_obj = getattr(config_manager, section)
        if hasattr(section_obj, key):
            setattr(section_obj, key, value)
            config_manager.save_configuration()
            print(f"Successfully set {section}.{key} = {value}")
        else:
            print(f"Error: Unknown setting '{key}' in section '{section}'")
            return False
            
    except Exception as e:
        print(f"Error setting configuration: {e}")
        return False
    
    return True

def reset_config():
    """Reset configuration to defaults"""
    try:
        config_manager.reset_to_defaults()
        config_manager.save_configuration()
        print("Configuration reset to defaults successfully.")
    except Exception as e:
        print(f"Error resetting configuration: {e}")

def main():
    """Main entry point for the configuration tool"""
    parser = argparse.ArgumentParser(
        description="Thunder Fighter Configuration Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s show                              # Show current configuration
  %(prog)s set sound music_volume 0.8        # Set music volume to 0.8
  %(prog)s set gameplay difficulty hard      # Set difficulty to hard
  %(prog)s set debug dev_mode true           # Enable developer mode
  %(prog)s reset                             # Reset to defaults
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Show command
    subparsers.add_parser('show', help='Show current configuration')
    
    # Set command
    set_parser = subparsers.add_parser('set', help='Set configuration value')
    set_parser.add_argument('section', choices=['sound', 'display', 'gameplay', 'controls', 'debug'],
                           help='Configuration section')
    set_parser.add_argument('key', help='Configuration key')
    set_parser.add_argument('value', help='Configuration value')
    
    # Reset command
    subparsers.add_parser('reset', help='Reset configuration to defaults')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'show':
        show_config()
    elif args.command == 'set':
        set_config(args.section, args.key, args.value)
    elif args.command == 'reset':
        reset_config()

if __name__ == '__main__':
    main() 