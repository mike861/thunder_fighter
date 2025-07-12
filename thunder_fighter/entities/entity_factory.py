"""
Entity Factory Base Classes

This module defines the base classes for entity factories, providing a
standardized way to create game entities with configuration and tracking.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Optional, Type, TypeVar

from thunder_fighter.utils.logger import logger

# Type variable for entity types
T = TypeVar("T")


class EntityFactory(ABC, Generic[T]):
    """
    Abstract base class for entity factories.

    This class provides common functionality for creating game entities
    with consistent configuration and initialization patterns.
    """

    def __init__(self, entity_type: Type[T]):
        """
        Initialize the entity factory.

        Args:
            entity_type: The type of entity this factory creates
        """
        self.entity_type = entity_type
        self._default_config: Dict[str, Any] = {}
        self._creation_count = 0

        logger.debug(f"EntityFactory initialized for {entity_type.__name__}")

    def set_default_config(self, config: Dict[str, Any]):
        """
        Set default configuration for entities created by this factory.

        Args:
            config: Default configuration dictionary
        """
        self._default_config = config.copy()
        logger.debug(f"Default config set for {self.entity_type.__name__}")

    def get_default_config(self) -> Dict[str, Any]:
        """
        Get the default configuration.

        Returns:
            Copy of the default configuration dictionary
        """
        return self._default_config.copy()

    def create(self, **kwargs) -> T:
        """
        Create an entity with the given parameters.

        Args:
            **kwargs: Entity creation parameters

        Returns:
            Created entity instance
        """
        # Merge default config with provided parameters
        config = self._default_config.copy()
        config.update(kwargs)

        # Validate configuration
        self._validate_config(config)

        # Create the entity
        entity = self._create_entity(config)

        # Post-creation setup
        self._post_creation_setup(entity, config)

        self._creation_count += 1
        logger.debug(f"Created {self.entity_type.__name__} #{self._creation_count}")

        return entity

    @abstractmethod
    def _create_entity(self, config: Dict[str, Any]) -> T:
        """
        Create the actual entity instance.

        Args:
            config: Configuration dictionary

        Returns:
            Created entity instance
        """
        pass

    def _validate_config(self, config: Dict[str, Any]):
        """
        Validate the configuration before entity creation.

        Args:
            config: Configuration to validate

        Raises:
            ValueError: If configuration is invalid
        """
        # Base validation - subclasses can override
        required_fields = self._get_required_fields()
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Required field '{field}' missing for {self.entity_type.__name__}")

    def _get_required_fields(self) -> list:
        """
        Get list of required configuration fields.

        Returns:
            List of required field names
        """
        return []  # Override in subclasses

    def _post_creation_setup(self, entity: T, config: Dict[str, Any]):
        """
        Perform post-creation setup on the entity.

        Args:
            entity: The created entity
            config: Configuration used for creation
        """
        # Base implementation does nothing - override in subclasses
        pass

    def get_creation_count(self) -> int:
        """
        Get the number of entities created by this factory.

        Returns:
            Number of entities created
        """
        return self._creation_count

    def reset_creation_count(self):
        """Reset the creation counter."""
        self._creation_count = 0
        logger.debug(f"Creation count reset for {self.entity_type.__name__}")

    def create_batch(self, count: int, **kwargs) -> list:
        """
        Create multiple entities with the same configuration.

        Args:
            count: Number of entities to create
            **kwargs: Entity creation parameters

        Returns:
            List of created entities
        """
        entities = []
        for i in range(count):
            # Add batch index to config
            batch_config = kwargs.copy()
            batch_config["batch_index"] = i
            entities.append(self.create(**batch_config))

        logger.debug(f"Created batch of {count} {self.entity_type.__name__} entities")
        return entities

    def __str__(self):
        return f"{self.__class__.__name__}({self.entity_type.__name__}, created={self._creation_count})"


class ConfigurableEntityFactory(EntityFactory[T]):
    """
    Entity factory that supports configuration templates and presets.

    This factory allows defining named configuration presets that can be
    used to create entities with predefined settings.
    """

    def __init__(self, entity_type: Type[T]):
        """Initialize the configurable entity factory."""
        super().__init__(entity_type)
        self._presets: Dict[str, Dict[str, Any]] = {}

    def add_preset(self, name: str, config: Dict[str, Any]):
        """
        Add a configuration preset.

        Args:
            name: Preset name
            config: Configuration dictionary
        """
        self._presets[name] = config.copy()
        logger.debug(f"Added preset '{name}' for {self.entity_type.__name__}")

    def remove_preset(self, name: str):
        """
        Remove a configuration preset.

        Args:
            name: Preset name to remove
        """
        if name in self._presets:
            del self._presets[name]
            logger.debug(f"Removed preset '{name}' for {self.entity_type.__name__}")

    def get_preset(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a configuration preset.

        Args:
            name: Preset name

        Returns:
            Configuration dictionary or None if not found
        """
        return self._presets.get(name, {}).copy() if name in self._presets else None

    def list_presets(self) -> list:
        """
        Get list of available preset names.

        Returns:
            List of preset names
        """
        return list(self._presets.keys())

    def create_from_preset(self, preset_name: str, **overrides) -> T:
        """
        Create an entity using a configuration preset.

        Args:
            preset_name: Name of the preset to use
            **overrides: Additional parameters to override preset values

        Returns:
            Created entity instance

        Raises:
            ValueError: If preset doesn't exist
        """
        if preset_name not in self._presets:
            raise ValueError(f"Preset '{preset_name}' not found for {self.entity_type.__name__}")

        # Start with preset configuration
        config = self._presets[preset_name].copy()
        # Apply overrides
        config.update(overrides)

        return self.create(**config)

    def create_preset_batch(self, preset_name: str, count: int, **overrides) -> list:
        """
        Create multiple entities using a preset.

        Args:
            preset_name: Name of the preset to use
            count: Number of entities to create
            **overrides: Additional parameters to override preset values

        Returns:
            List of created entities
        """
        entities = []
        for i in range(count):
            batch_overrides = overrides.copy()
            batch_overrides["batch_index"] = i
            entities.append(self.create_from_preset(preset_name, **batch_overrides))

        logger.debug(f"Created batch of {count} {self.entity_type.__name__} entities from preset '{preset_name}'")
        return entities
