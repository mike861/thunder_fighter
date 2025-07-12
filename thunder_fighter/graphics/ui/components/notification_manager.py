"""
Notification Manager Component

Manages all in-game notifications including regular notifications, warnings, and achievements.
"""

from thunder_fighter.constants import HEIGHT
from thunder_fighter.graphics.effects import AchievementNotification, Notification, WarningNotification
from thunder_fighter.utils.logger import logger


class NotificationManager:
    """Manages all game notifications."""

    def __init__(self, screen):
        """
        Initialize the notification manager.

        Args:
            screen: pygame.Surface - The game screen to draw on
        """
        self.screen = screen
        self.notifications = []
        self.notification_duration = 2000  # 2 seconds in milliseconds

    def add(self, text, notification_type="normal"):
        """
        Add a new notification.

        Args:
            text: Notification text
            notification_type: Type of notification ("normal", "warning", "achievement")
        """
        if notification_type == "warning":
            notification = WarningNotification(text)
        elif notification_type == "achievement":
            notification = AchievementNotification(text)
        else:
            notification = Notification(text)

        self.notifications.append(notification)
        logger.info(f"Added {notification_type} notification: {text}")

    def update(self):
        """Update all notifications and remove expired ones."""
        # Update notifications and keep only active ones
        self.notifications = [n for n in self.notifications if n.update()]

        # Arrange notification positions
        self._arrange_notifications()

    def draw(self):
        """Draw all active notifications."""
        for notification in self.notifications:
            notification.draw(self.screen)

    def clear(self):
        """Clear all notifications."""
        self.notifications.clear()

    def clear_all(self):
        """Clear all notifications (alias for clear method)."""
        self.clear()

    def _arrange_notifications(self):
        """Arrange notifications vertically to avoid overlap."""
        if not self.notifications:
            return

        # Group by position type
        top_notifications = []
        center_notifications = []
        bottom_notifications = []

        for notification in self.notifications:
            if notification.position == 'top':
                top_notifications.append(notification)
            elif notification.position == 'center':
                center_notifications.append(notification)
            elif notification.position == 'bottom':
                bottom_notifications.append(notification)

        # Sort by creation time to display newer messages first
        top_notifications.sort(key=lambda n: n.creation_time, reverse=True)
        center_notifications.sort(key=lambda n: n.creation_time, reverse=True)
        bottom_notifications.sort(key=lambda n: n.creation_time, reverse=True)

        # Set top notification positions
        for i, notification in enumerate(top_notifications):
            y_position = 80 + i * 40  # Start from top, move down 40 pixels each
            notification.set_y_position(y_position)

        # Set center notification positions
        center_y_start = HEIGHT // 2 - (len(center_notifications) * 40) // 2
        for i, notification in enumerate(center_notifications):
            y_position = center_y_start + i * 40
            notification.set_y_position(y_position)

        # Set bottom notification positions
        for i, notification in enumerate(bottom_notifications):
            y_position = HEIGHT - 120 - i * 40  # Arrange from bottom up
            notification.set_y_position(y_position)

    def has_notifications(self):
        """Check if there are any active notifications."""
        return len(self.notifications) > 0
