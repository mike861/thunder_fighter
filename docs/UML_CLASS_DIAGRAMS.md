# Thunder Fighter UML Class Diagrams

## Overview

This document contains detailed UML class diagrams for Thunder Fighter's architecture. These diagrams provide comprehensive implementation details including method signatures, attributes, and relationships between classes.

## Table of Contents

1. [Event System Class Diagram](#event-system-class-diagram)
2. [State Management Class Diagram](#state-management-class-diagram)
3. [Entity System Class Diagram](#entity-system-class-diagram)
4. [Input System Class Diagram](#input-system-class-diagram)
5. [Graphics System Class Diagram](#graphics-system-class-diagram)

## Event System Class Diagram

```mermaid
classDiagram
    class EventType {
        <<enumeration>>
        PLAYER_DIED
        PLAYER_HEALTH_CHANGED
        ENEMY_SPAWNED
        ENEMY_DIED
        BOSS_SPAWNED
        BOSS_DEFEATED
        ITEM_COLLECTED
        GAME_PAUSED
        LEVEL_UP
        GAME_WON
    }
    
    class Event {
        +type: EventType
        +data: dict
        +timestamp: float
        +handled: bool
        +source: str
        +get_data(key: str): any
        +mark_handled()
    }
    
    class GameEvent {
        +create_player_died(player_id: str): GameEvent
        +create_boss_spawned(boss_id: str, level: int): GameEvent
        +create_item_collected(item_type: str, player_id: str): GameEvent
        +create_level_up(new_level: int): GameEvent
    }
    
    class EventListener {
        <<abstract>>
        +handle_event(event: Event)*
    }
    
    class FunctionListener {
        +callback: Callable
        +event_types: list[EventType]
        +handle_event(event: Event)
    }
    
    class EventSystem {
        +listeners: dict[EventType, list[EventListener]]
        +event_queue: list[Event]
        +max_queue_size: int
        +register_listener(listener: EventListener, event_type: EventType)
        +dispatch_event(event: Event)
        +process_events()
        +clear_queue()
    }
    
    class CollisionSystem {
        +handle_event(event: Event)
    }
    
    class ScoringSystem {
        +handle_event(event: Event)
    }
    
    class UIManager {
        +handle_event(event: Event)
    }
    
    Event --> EventType : uses
    GameEvent --|> Event
    EventListener <|-- FunctionListener
    EventListener <|-- CollisionSystem
    EventListener <|-- ScoringSystem
    EventListener <|-- UIManager
    
    EventSystem --> Event : manages
    EventSystem --> EventListener : notifies
    
    GameEvent --> EventType : creates events of
    
    note for EventSystem "Central event dispatcher\\nDecouples game components"
    note for GameEvent "Factory methods for\\ntype-safe event creation"
    note for EventListener "Observer pattern\\nfor event handling"
```

## State Management Class Diagram

```mermaid
classDiagram
    class State {
        <<abstract>>
        +name: str
        +enter(previous_state: str)*
        +exit(next_state: str)*
        +update(dt: float)*
        +handle_event(event: Event)*
        +can_transition_to(state_name: str): bool*
    }
    
    class StateMachine {
        +current_state: State
        +states: dict[str, State]
        +transition_history: list[str]
        +add_state(state: State)
        +transition_to(state_name: str)
        +update(dt: float)
        +handle_event(event: Event)
        +get_current_state_name(): str
    }
    
    class MenuState {
        +enter(previous_state: str)
        +handle_event(event: Event)
        +update(dt: float)
    }
    
    class PlayingState {
        +enter(previous_state: str)
        +exit(next_state: str)
        +update(dt: float)
        +handle_event(event: Event)
    }
    
    class PausedState {
        +enter(previous_state: str)
        +exit(next_state: str)
        +handle_event(event: Event)
    }
    
    class GameOverState {
        +restart_requested: bool
        +enter(previous_state: str)
        +handle_event(event: Event)
        +update(dt: float)
    }
    
    class VictoryState {
        +final_score: int
        +completion_time: float
        +enter(previous_state: str)
        +handle_event(event: Event)
    }
    
    class LevelTransitionState {
        +transition_duration: float
        +target_level: int
        +enter(previous_state: str)
        +update(dt: float)
    }
    
    class StateFactory {
        +create_state(state_name: str, game_instance: Game): State
        +create_all_states(game_instance: Game): dict[str, State]
    }
    
    StateMachine --> State : manages
    State <|-- MenuState
    State <|-- PlayingState
    State <|-- PausedState
    State <|-- GameOverState
    State <|-- VictoryState
    State <|-- LevelTransitionState
    
    StateFactory --> State : creates
    StateFactory --> MenuState : creates
    StateFactory --> PlayingState : creates
    StateFactory --> PausedState : creates
    StateFactory --> GameOverState : creates
    StateFactory --> VictoryState : creates
    StateFactory --> LevelTransitionState : creates
    
    note for StateMachine "Manages state transitions\\nand event forwarding"
    note for PlayingState "Main gameplay state\\nwith entity spawning"
    note for LevelTransitionState "3-second level transition\\nwith smooth animations"
```

## Entity System Class Diagram

```mermaid
classDiagram
    class GameObject {
        <<abstract>>
        +x: float
        +y: float
        +rect: pygame.Rect
        +image: pygame.Surface
        +active: bool
        +update(dt: float)
        +render(screen: pygame.Surface)
    }
    
    class Entity {
        +entity_id: str
        +created_at: float
        +velocity_x: float
        +velocity_y: float
        +update(dt: float)
        +destroy()
    }
    
    class MovableEntity {
        +speed: float
        +direction: float
        +move(dx: float, dy: float)
        +set_velocity(vx: float, vy: float)
    }
    
    class LivingEntity {
        +health: int
        +max_health: int
        +is_alive: bool
        +take_damage(damage: int)
        +heal(amount: int)
    }
    
    class EntityFactory {
        <<abstract>>
        +create_entity(config: dict): Entity
        +get_preset_config(preset_name: str): dict
    }
    
    class EnemyFactory {
        +presets: dict
        +create_for_level(level: int): Enemy
        +create_wave(size: int): list[Enemy]
        +create_random_enemy(): Enemy
    }
    
    class BossFactory {
        +create_boss(level: int): Boss
        +create_final_boss(): Boss
    }
    
    class ItemFactory {
        +create_power_up(): PowerUp
        +create_health_pack(): HealthPack
        +create_wingman_upgrade(): WingmanUpgrade
    }
    
    class ProjectileFactory {
        +create_bullet(x: float, y: float, renderer: Optional): Bullet
        +create_missile(x: float, y: float, target, renderer: Optional): TrackingMissile
        +create_from_preset(preset_name: str): Entity
    }
    
    class BulletLogic {
        +x: float
        +y: float
        +speed: float
        +angle: float
        +speed_x: float
        +speed_y: float
        +update_position()
        +is_out_of_bounds(): bool
        +get_position(): tuple
        +get_velocity(): tuple
    }
    
    class TrackingAlgorithm {
        +x: float
        +y: float
        +speed: float
        +last_target_position: tuple
        +update_target_position(target_x: float, target_y: float)
        +calculate_movement(): dict
        +is_out_of_bounds(): bool
        +get_position(): tuple
        +set_position(x: float, y: float)
        +distance_to_target(): float
    }
    
    class Vector2 {
        +x: float
        +y: float
        +__add__(other: Vector2): Vector2
        +__sub__(other: Vector2): Vector2
        +__mul__(scalar: float): Vector2
        +length(): float
        +normalize_ip()
    }
    
    class Bullet {
        +logic: BulletLogic
        +image: pygame.Surface
        +rect: pygame.Rect
        +update()
        +kill()
    }
    
    class TrackingMissile {
        +algorithm: TrackingAlgorithm
        +target: Optional[Entity]
        +angle: float
        +original_image: pygame.Surface
        +update()
        +kill()
    }
    
    class Player {
        +health: int
        +max_health: int
        +wingmen: list[Wingman]
        +bullet_paths: int
        +missile_count: int
        +shoot(): list[Bullet]
        +launch_missile(): Missile
        +handle_input(input_state: dict)
        +take_damage(damage: int): bool
        +heal(amount: int)
    }
    
    class Enemy {
        +level: int
        +can_shoot: bool
        +shoot_delay: float
        +last_shot_time: float
        +shoot(): Bullet
        +get_points(): int
        +update(dt: float)
    }
    
    class Boss {
        +health: int
        +max_health: int
        +attack_patterns: list
        +current_pattern: int
        +phase: int
        +last_pattern_change: float
        +update_attack_pattern()
        +spawn_minions()
        +special_attack()
    }
    
    pygame.sprite.Sprite <|-- GameObject
    GameObject <|-- Entity
    Entity <|-- MovableEntity
    MovableEntity <|-- LivingEntity
    LivingEntity <|-- Player
    LivingEntity <|-- Enemy
    Enemy <|-- Boss
    
    EntityFactory <|-- EnemyFactory
    EntityFactory <|-- BossFactory
    EntityFactory <|-- ItemFactory
    EntityFactory <|-- ProjectileFactory
    
    EnemyFactory --> Enemy : creates
    BossFactory --> Boss : creates
    ItemFactory --> PowerUp : creates
    ProjectileFactory --> Bullet : creates
    ProjectileFactory --> TrackingMissile : creates
    
    Bullet --> BulletLogic : contains
    TrackingMissile --> TrackingAlgorithm : contains
    BulletLogic --> Vector2 : uses
    TrackingAlgorithm --> Vector2 : uses
    
    Player --> Wingman : manages
    
    note for EntityFactory "Abstract factory pattern\\nfor entity creation"
    note for Player "Manages wingman formation\\nand missile system"
    note for Boss "Multi-phase boss with\\ncomplex attack patterns"
    note for BulletLogic "Mathematical logic layer\\nZero external dependencies"
    note for TrackingAlgorithm "Tracking algorithm\\nImproved testability"
    note for Vector2 "Custom vector implementation\\nMathematical utilities"
    note for ProjectileFactory "Clean interface design\\nRequired parameters"
```

## Input System Class Diagram

```mermaid
classDiagram
    class InputEvent {
        +type: str
        +key: Optional[int]
        +timestamp: float
        +processed: bool
    }
    
    class InputHandler {
        +fallback_enabled: bool
        +critical_keys: set[int]
        +process_event(pygame_event): list[InputEvent]
        +_process_normal(event): InputEvent
        +_process_fallback(event): InputEvent
        +reset_state()
    }
    
    class InputManager {
        +handler: InputHandler
        +event_queue: list[InputEvent]
        +state: dict[str, bool]
        +process_pygame_events(events: list)
        +get_current_state(): dict
        +update_state(input_event: InputEvent)
    }
    
    class InputFacade {
        +manager: InputManager
        +key_bindings: dict[int, str]
        +is_pressed(action: str): bool
        +was_just_pressed(action: str): bool
        +get_movement_vector(): tuple
        +process_input(): dict
    }
    
    class KeyBinding {
        +action: str
        +primary_key: int
        +secondary_key: Optional[int]
        +modifier_keys: list[int]
        +matches(key: int, modifiers: list[int]): bool
    }
    
    InputFacade --> InputManager : uses
    InputManager --> InputHandler : uses
    InputManager --> InputEvent : processes
    InputFacade --> KeyBinding : manages
    
    note for InputHandler "Platform-specific event processing\\nwith fallback mechanisms"
    note for InputManager "Event coordination and\\nstate management"
    note for InputFacade "High-level input interface\\nfor game logic"
```

## Graphics System Class Diagram

```mermaid
classDiagram
    class Renderer {
        <<abstract>>
        +surface: pygame.Surface
        +render()*
    }
    
    class BackgroundRenderer {
        +current_theme: dict
        +buffer: pygame.Surface
        +transition_progress: float
        +render_background(screen: pygame.Surface)
        +transition_to_theme(theme: dict)
        +update_transition(dt: float)
    }
    
    class UIRenderer {
        +components: list[UIComponent]
        +render_ui(screen: pygame.Surface)
        +add_component(component: UIComponent)
        +remove_component(component: UIComponent)
    }
    
    class EffectsRenderer {
        +active_effects: list[Effect]
        +particle_systems: list[ParticleSystem]
        +render_effects(screen: pygame.Surface)
        +add_effect(effect: Effect)
        +update_effects(dt: float)
    }
    
    class UIComponent {
        <<abstract>>
        +rect: pygame.Rect
        +visible: bool
        +render(screen: pygame.Surface)*
        +update(dt: float)*
    }
    
    class HealthBarComponent {
        +current_health: int
        +max_health: int
        +color_scheme: dict
        +render(screen: pygame.Surface)
        +update_health(health: int, max_health: int)
    }
    
    class NotificationManager {
        +notifications: list[Notification]
        +display_duration: float
        +add_notification(text: str, type: str)
        +render(screen: pygame.Surface)
        +update(dt: float)
        +clear_all()
    }
    
    class GameInfoDisplay {
        +score: int
        +level: int
        +elapsed_time: float
        +font: pygame.font.Font
        +render(screen: pygame.Surface)
        +update_info(score: int, level: int, time: float)
    }
    
    Renderer <|-- BackgroundRenderer
    Renderer <|-- UIRenderer
    Renderer <|-- EffectsRenderer
    
    UIComponent <|-- HealthBarComponent
    UIComponent <|-- NotificationManager
    UIComponent <|-- GameInfoDisplay
    
    UIRenderer --> UIComponent : manages
    
    note for BackgroundRenderer "Double-buffered rendering\\nwith smooth transitions"
    note for UIRenderer "Modular UI component\\nmanagement system"
    note for NotificationManager "Game notifications and\\nachievements system"
```

## Usage Guidelines

### For Architecture Documentation
- Reference these diagrams when discussing system relationships
- Focus on high-level component interactions in architecture docs
- Use simplified versions for architectural overviews

### For Technical Documentation
- Reference specific class details when documenting implementations
- Use method signatures for API documentation
- Include implementation file paths alongside diagram references

### For Development
- Use these diagrams as implementation reference
- Validate new features against existing class structures
- Ensure new components follow established patterns

---

*This document provides detailed UML class diagrams for Thunder Fighter's architecture. For high-level architectural concepts, see [Architecture Guide](ARCHITECTURE.md). For implementation details, see [Technical Details](TECHNICAL_DETAILS.md).*