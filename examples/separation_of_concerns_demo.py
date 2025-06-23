"""
Separation of Concerns Demo

This demo showcases the architectural improvements implemented in the Thunder Fighter game,
demonstrating how concerns have been separated into distinct, focused systems.
"""

import pygame
import sys
import os

# Add the parent directory to the path so we can import thunder_fighter modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from thunder_fighter.input import InputManager, KeyBindings, InputEventType
from thunder_fighter.entities import EnemyFactory, BossFactory, ItemFactory, ProjectileFactory
from thunder_fighter.events import EventSystem, GameEventType, GameEvent
from thunder_fighter.utils.logger import logger


def demo_input_management():
    """Demonstrate the input management system."""
    print("\n" + "="*60)
    print("INPUT MANAGEMENT SYSTEM DEMO")
    print("="*60)
    
    # Initialize pygame for input handling
    pygame.init()
    
    # Create input manager
    input_manager = InputManager()
    print(f"✓ Created input manager: {input_manager}")
    
    # Demonstrate key bindings
    key_bindings = input_manager.get_key_bindings()
    print(f"✓ Key bindings loaded with {len(key_bindings.get_all_categories())} categories")
    
    # Show key binding categories
    for category in key_bindings.get_all_categories():
        bindings = key_bindings.get_bindings_by_category(category)
        print(f"  - {category}: {len(bindings)} bindings")
    
    # Demonstrate key rebinding
    print("\n📝 Key Rebinding Demo:")
    original_key = pygame.K_SPACE
    new_key = pygame.K_z
    
    if key_bindings.rebind_key("shoot", original_key, new_key):
        print(f"✓ Successfully rebound 'shoot' from {pygame.key.name(original_key)} to {pygame.key.name(new_key)}")
    else:
        print("✗ Failed to rebind key")
    
    # Demonstrate input event callbacks
    print("\n📡 Input Event Callbacks Demo:")
    
    def movement_callback(event):
        direction = event.get_data('direction')
        pressed = event.get_data('pressed')
        action = "started" if pressed else "stopped"
        print(f"  🎮 Player {action} moving {direction}")
    
    def action_callback(event):
        action = event.get_data('action')
        pressed = event.get_data('pressed')
        status = "started" if pressed else "stopped"
        print(f"  🔫 Player {status} {action}")
    
    # Register callbacks
    input_manager.add_event_callback(InputEventType.MOVE_UP, movement_callback)
    input_manager.add_event_callback(InputEventType.MOVE_DOWN, movement_callback)
    input_manager.add_event_callback(InputEventType.MOVE_LEFT, movement_callback)
    input_manager.add_event_callback(InputEventType.MOVE_RIGHT, movement_callback)
    input_manager.add_event_callback(InputEventType.SHOOT, action_callback)
    
    print("✓ Registered input event callbacks")
    
    # Simulate some input events
    print("\n🎯 Simulating Input Events:")
    
    # Create mock pygame events
    mock_events = [
        # Key down events
        type('Event', (), {'type': pygame.KEYDOWN, 'key': pygame.K_w})(),
        type('Event', (), {'type': pygame.KEYDOWN, 'key': pygame.K_z})(),  # Rebound shoot key
        # Key up events
        type('Event', (), {'type': pygame.KEYUP, 'key': pygame.K_w})(),
        type('Event', (), {'type': pygame.KEYUP, 'key': pygame.K_z})(),
    ]
    
    # Process events
    input_events = input_manager.update(mock_events)
    print(f"✓ Processed {len(input_events)} input events")
    
    # Demonstrate pause/resume functionality
    print("\n⏸️  Pause/Resume Demo:")
    input_manager.pause()
    print("✓ Input manager paused - only certain events allowed")
    
    input_manager.resume()
    print("✓ Input manager resumed - all events allowed")
    
    pygame.quit()


def demo_entity_factories():
    """Demonstrate the entity factory system."""
    print("\n" + "="*60)
    print("ENTITY FACTORY SYSTEM DEMO")
    print("="*60)
    
    # Enemy Factory Demo
    print("\n🤖 Enemy Factory Demo:")
    enemy_factory = EnemyFactory()
    print(f"✓ Created enemy factory: {enemy_factory}")
    
    # Show available presets
    presets = enemy_factory.list_presets()
    print(f"✓ Available enemy presets: {', '.join(presets)}")
    
    # Show preset configurations
    for preset_name in presets[:3]:  # Show first 3 presets
        preset = enemy_factory.get_preset(preset_name)
        print(f"  - {preset_name}: health_mult={preset['health_multiplier']}, "
              f"speed_mult={preset['speed_multiplier']}, can_shoot={preset['can_shoot']}")
    
    # Demonstrate level-based enemy selection
    print("\n🎯 Level-based Enemy Selection:")
    for level in [1, 3, 6]:
        enemy_type = enemy_factory._determine_enemy_type(level, level)
        print(f"  - Level {level}: {enemy_type} enemy")
    
    # Boss Factory Demo
    print("\n👹 Boss Factory Demo:")
    boss_factory = BossFactory()
    print(f"✓ Created boss factory: {boss_factory}")
    
    boss_presets = boss_factory.list_presets()
    print(f"✓ Available boss presets: {', '.join(boss_presets)}")
    
    # Item Factory Demo
    print("\n💎 Item Factory Demo:")
    item_factory = ItemFactory()
    print(f"✓ Created item factory: {item_factory}")
    
    item_presets = item_factory.list_presets()
    print(f"✓ Available item presets: {', '.join(item_presets)}")
    
    # Projectile Factory Demo
    print("\n🚀 Projectile Factory Demo:")
    projectile_factory = ProjectileFactory()
    print(f"✓ Created projectile factory: {projectile_factory}")
    
    projectile_presets = projectile_factory.list_presets()
    print(f"✓ Available projectile presets: {', '.join(projectile_presets)}")
    
    # Demonstrate factory statistics
    print("\n📊 Factory Statistics:")
    factories = [
        ("Enemy", enemy_factory),
        ("Boss", boss_factory),
        ("Item", item_factory),
        ("Projectile", projectile_factory)
    ]
    
    for name, factory in factories:
        print(f"  - {name} Factory: {factory.get_creation_count()} entities created")


def demo_event_system():
    """Demonstrate the event system."""
    print("\n" + "="*60)
    print("EVENT SYSTEM DEMO")
    print("="*60)
    
    # Create event system
    event_system = EventSystem()
    print(f"✓ Created event system: {event_system}")
    
    # Demonstrate event listeners
    print("\n👂 Event Listener Demo:")
    
    class GameEventListener:
        def __init__(self, name):
            self.name = name
            self.events_received = 0
        
        def handle_event(self, event):
            self.events_received += 1
            print(f"  📨 {self.name} received: {event.event_type.value} from {event.source}")
            return False  # Don't consume the event
    
    # Create listeners
    combat_listener = GameEventListener("Combat System")
    ui_listener = GameEventListener("UI System")
    audio_listener = GameEventListener("Audio System")
    
    # Register listeners for specific events
    event_system.register_listener(GameEventType.PLAYER_DIED, combat_listener)
    event_system.register_listener(GameEventType.ENEMY_DIED, combat_listener)
    event_system.register_listener(GameEventType.BOSS_DIED, combat_listener)
    
    event_system.register_listener(GameEventType.NOTIFICATION_ADDED, ui_listener)
    event_system.register_listener(GameEventType.LEVEL_CHANGED, ui_listener)
    
    event_system.register_listener(GameEventType.PLAY_SOUND, audio_listener)
    
    # Register global listener
    global_listener = GameEventListener("Global Logger")
    event_system.register_global_listener(global_listener)
    
    print("✓ Registered event listeners")
    
    # Demonstrate event creation and dispatch
    print("\n📤 Event Dispatch Demo:")
    
    # Create and dispatch various events
    events_to_dispatch = [
        GameEvent.create_player_health_changed("player", 100, 75, 100),
        GameEvent.create_enemy_died("enemy", "basic", 100),
        GameEvent.create_boss_spawned("boss_factory", 2, "elite"),
        GameEvent.create_level_changed("game", 1, 2),
        GameEvent.create_play_sound("audio", "explosion.wav", 0.8),
        GameEvent.create_notification("ui", "Level Up!", "success")
    ]
    
    for event in events_to_dispatch:
        event_system.dispatch_event(event)
    
    print(f"✓ Dispatched {len(events_to_dispatch)} events")
    
    # Process all events
    print("\n⚡ Processing Events:")
    event_system.process_events()
    
    # Show listener statistics
    print("\n📊 Listener Statistics:")
    listeners = [
        ("Combat System", combat_listener),
        ("UI System", ui_listener),
        ("Audio System", audio_listener),
        ("Global Logger", global_listener)
    ]
    
    for name, listener in listeners:
        print(f"  - {name}: {listener.events_received} events received")
    
    # Show event system statistics
    print(f"\n📈 Event System Stats:")
    print(f"  - Events processed: {event_system.get_events_processed()}")
    print(f"  - Queue size: {event_system.get_queue_size()}")
    print(f"  - Total listeners: {event_system.get_listener_count()}")


def demo_system_integration():
    """Demonstrate integration between separated systems."""
    print("\n" + "="*60)
    print("SYSTEM INTEGRATION DEMO")
    print("="*60)
    
    # Initialize all systems
    pygame.init()
    input_manager = InputManager()
    enemy_factory = EnemyFactory()
    event_system = EventSystem()
    
    print("✓ Initialized all systems")
    
    # Demonstrate how systems can work together
    print("\n🔗 System Integration Example:")
    
    # Create a simple game event handler that responds to input
    class GameController:
        def __init__(self, event_system, enemy_factory):
            self.event_system = event_system
            self.enemy_factory = enemy_factory
            self.enemies_spawned = 0
        
        def handle_input_event(self, input_event):
            if input_event.event_type == InputEventType.SHOOT:
                # Shooting triggers enemy spawn (for demo purposes)
                if input_event.get_data('pressed'):
                    self.spawn_enemy()
        
        def spawn_enemy(self):
            self.enemies_spawned += 1
            # Emit game event
            self.event_system.emit_event(
                GameEventType.ENEMY_SPAWNED,
                "game_controller",
                enemy_type="basic",
                level=1
            )
            print(f"  🤖 Spawned enemy #{self.enemies_spawned}")
    
    # Create game controller
    game_controller = GameController(event_system, enemy_factory)
    
    # Register input callback
    input_manager.add_event_callback(InputEventType.SHOOT, game_controller.handle_input_event)
    
    # Register event listener
    def enemy_spawn_listener(event):
        enemy_type = event.get_data('enemy_type')
        level = event.get_data('level')
        print(f"    📡 Event received: {enemy_type} enemy spawned at level {level}")
        return False
    
    event_system.register_listener(GameEventType.ENEMY_SPAWNED, enemy_spawn_listener)
    
    print("✓ Set up system integration")
    
    # Simulate input that triggers the chain
    print("\n🎮 Simulating Input Chain:")
    mock_shoot_event = type('Event', (), {'type': pygame.KEYDOWN, 'key': pygame.K_SPACE})()
    input_events = input_manager.update([mock_shoot_event])
    
    # Process game events
    event_system.process_events()
    
    print(f"✓ Processed integration chain: {len(input_events)} input events generated")
    
    pygame.quit()


def demo_benefits():
    """Show the benefits of separation of concerns."""
    print("\n" + "="*60)
    print("SEPARATION OF CONCERNS BENEFITS")
    print("="*60)
    
    benefits = [
        ("🎯 Single Responsibility", "Each system has one clear purpose"),
        ("🔧 Easy Maintenance", "Changes to one system don't affect others"),
        ("🧪 Better Testing", "Systems can be tested independently"),
        ("🔄 Reusability", "Systems can be reused in different contexts"),
        ("📈 Scalability", "New features can be added without major refactoring"),
        ("🐛 Easier Debugging", "Issues can be isolated to specific systems"),
        ("👥 Team Development", "Different developers can work on different systems"),
        ("📚 Clear Architecture", "Code structure is more understandable")
    ]
    
    print("\n✨ Key Benefits Achieved:")
    for benefit, description in benefits:
        print(f"  {benefit}: {description}")
    
    print("\n🏗️ Architectural Improvements:")
    improvements = [
        "Input handling separated from game logic",
        "Entity creation centralized in factories",
        "Event-driven communication between components",
        "Configurable key bindings system",
        "Type-safe event handling",
        "Modular, pluggable architecture"
    ]
    
    for i, improvement in enumerate(improvements, 1):
        print(f"  {i}. {improvement}")


def main():
    """Run the complete separation of concerns demo."""
    print("🎮 THUNDER FIGHTER - SEPARATION OF CONCERNS DEMO")
    print("This demo showcases architectural improvements for better code organization")
    
    try:
        # Run all demos
        demo_input_management()
        demo_entity_factories()
        demo_event_system()
        demo_system_integration()
        demo_benefits()
        
        print("\n" + "="*60)
        print("✅ DEMO COMPLETED SUCCESSFULLY")
        print("="*60)
        print("\nAll systems demonstrated clean separation of concerns!")
        print("Each system can be developed, tested, and maintained independently.")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        logger.error(f"Demo error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 