"""
Game Events

This module defines game-specific event types and event classes
for the Thunder Fighter game.
"""

from dataclasses import dataclass
from enum import Enum

from .event_system import Event


class GameEventType(Enum):
    """Game-specific event types."""

    # Base event
    UNKNOWN = "unknown"

    # Player events
    PLAYER_DIED = "player_died"
    PLAYER_LEVELED_UP = "player_leveled_up"
    PLAYER_HEALTH_CHANGED = "player_health_changed"
    PLAYER_MOVED = "player_moved"

    # Enemy events
    ENEMY_SPAWNED = "enemy_spawned"
    ENEMY_DIED = "enemy_died"
    ENEMY_HIT_PLAYER = "enemy_hit_player"

    # Boss events
    BOSS_SPAWNED = "boss_spawned"
    BOSS_DIED = "boss_died"
    BOSS_DEFEATED = "boss_defeated"  # Alias for boss_died, used in game logic
    BOSS_PHASE_CHANGED = "boss_phase_changed"

    # Item events
    ITEM_SPAWNED = "item_spawned"
    ITEM_COLLECTED = "item_collected"

    # Game state events
    GAME_STARTED = "game_started"
    GAME_PAUSED = "game_paused"
    GAME_RESUMED = "game_resumed"
    GAME_OVER = "game_over"
    GAME_WON = "game_won"
    LEVEL_CHANGED = "level_changed"
    LEVEL_UP = "level_up"  # Alias for level_changed, used in game logic

    # Player stat events
    PLAYER_STATS_CHANGED = "player_stats_changed"

    # Score events
    SCORE_CHANGED = "score_changed"
    SCORE_MILESTONE = "score_milestone"

    # Audio events
    PLAY_SOUND = "play_sound"
    PLAY_MUSIC = "play_music"
    STOP_MUSIC = "stop_music"

    # UI events
    NOTIFICATION_ADDED = "notification_added"
    UI_STATE_CHANGED = "ui_state_changed"


@dataclass
class GameEvent(Event):
    """
    Game-specific event class.

    This class extends the base Event class with game-specific
    functionality and convenience methods.
    """

    def __init__(self, event_type: GameEventType, source: str = "unknown", **data):
        """
        Initialize a game event.

        Args:
            event_type: The game event type
            source: The source component
            **data: Event data
        """
        super().__init__(event_type, data, source=source)

    @classmethod
    def create_player_died(cls, source: str = "player", cause: str = "unknown") -> 'GameEvent':
        """Create a player died event."""
        return cls(GameEventType.PLAYER_DIED, source, cause=cause)

    @classmethod
    def create_player_health_changed(cls, source: str = "player",
                                   old_health: int = 0, new_health: int = 0,
                                   max_health: int = 100) -> 'GameEvent':
        """Create a player health changed event."""
        return cls(
            GameEventType.PLAYER_HEALTH_CHANGED, source,
            old_health=old_health, new_health=new_health, max_health=max_health
        )

    @classmethod
    def create_enemy_spawned(cls, source: str = "enemy_factory",
                           enemy_type: str = "basic", level: int = 1) -> 'GameEvent':
        """Create an enemy spawned event."""
        return cls(GameEventType.ENEMY_SPAWNED, source, enemy_type=enemy_type, level=level)

    @classmethod
    def create_enemy_died(cls, source: str = "enemy", enemy_type: str = "basic",
                         score_awarded: int = 0) -> 'GameEvent':
        """Create an enemy died event."""
        return cls(
            GameEventType.ENEMY_DIED, source,
            enemy_type=enemy_type, score_awarded=score_awarded
        )

    @classmethod
    def create_boss_spawned(cls, source: str = "boss_factory",
                          boss_level: int = 1, boss_type: str = "standard") -> 'GameEvent':
        """Create a boss spawned event."""
        return cls(
            GameEventType.BOSS_SPAWNED, source,
            boss_level=boss_level, boss_type=boss_type
        )

    @classmethod
    def create_boss_died(cls, source: str = "boss", boss_level: int = 1,
                        score_awarded: int = 0) -> 'GameEvent':
        """Create a boss died event."""
        return cls(
            GameEventType.BOSS_DIED, source,
            boss_level=boss_level, score_awarded=score_awarded
        )

    @classmethod
    def create_item_collected(cls, source: str = "item", item_type: str = "health",
                            player_id: str = "player") -> 'GameEvent':
        """Create an item collected event."""
        return cls(
            GameEventType.ITEM_COLLECTED, source,
            item_type=item_type, player_id=player_id
        )

    @classmethod
    def create_game_state_changed(cls, source: str = "game", old_state: str = "",
                                new_state: str = "") -> 'GameEvent':
        """Create a game state changed event."""
        event_type_map = {
            'started': GameEventType.GAME_STARTED,
            'paused': GameEventType.GAME_PAUSED,
            'resumed': GameEventType.GAME_RESUMED,
            'over': GameEventType.GAME_OVER,
            'won': GameEventType.GAME_WON
        }

        event_type = event_type_map.get(new_state, GameEventType.GAME_STARTED)
        return cls(event_type, source, old_state=old_state, new_state=new_state)

    @classmethod
    def create_score_changed(cls, source: str = "score", old_score: int = 0,
                           new_score: int = 0, delta: int = 0) -> 'GameEvent':
        """Create a score changed event."""
        return cls(
            GameEventType.SCORE_CHANGED, source,
            old_score=old_score, new_score=new_score, delta=delta
        )

    @classmethod
    def create_level_changed(cls, source: str = "game", old_level: int = 1,
                           new_level: int = 1) -> 'GameEvent':
        """Create a level changed event."""
        return cls(
            GameEventType.LEVEL_CHANGED, source,
            old_level=old_level, new_level=new_level
        )

    @classmethod
    def create_play_sound(cls, source: str = "audio", sound_name: str = "",
                         volume: float = 1.0) -> 'GameEvent':
        """Create a play sound event."""
        return cls(
            GameEventType.PLAY_SOUND, source,
            sound_name=sound_name, volume=volume
        )

    @classmethod
    def create_notification(cls, source: str = "ui", message: str = "",
                          notification_type: str = "info") -> 'GameEvent':
        """Create a notification event."""
        return cls(
            GameEventType.NOTIFICATION_ADDED, source,
            message=message, notification_type=notification_type
        )
