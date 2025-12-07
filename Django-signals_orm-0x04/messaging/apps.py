"""
App configuration for the messaging app.

This module configures the messaging app and ensures signals are registered
when the app is ready.
"""
from django.apps import AppConfig


class MessagingConfig(AppConfig):
    """Configuration class for the messaging app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "messaging"
    verbose_name = "Messaging"

    def ready(self) -> None:
        """
        Called when Django starts up.

        This method imports signals to ensure they are registered
        and connected to their respective models.
        """
        # Import signals to register them
        import messaging.signals  # noqa: F401

