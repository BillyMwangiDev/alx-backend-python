"""
Django signals for the messaging app.

This module defines signal handlers that automatically create notifications
when new Message instances are created, captures message edit history
when messages are updated, and cleans up related data when users are deleted.
"""
import logging

from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Message, MessageHistory, Notification

logger = logging.getLogger(__name__)

User = get_user_model()


@receiver(pre_save, sender=Message)
def capture_message_history(sender, instance, **kwargs):
    """
    Signal handler that captures the old content of a message before it's updated.

    This signal is triggered before a Message instance is saved.
    It captures the previous content and stores it as an instance attribute
    for use in the post_save handler.

    Args:
        sender: The model class that sent the signal (Message)
        instance: The actual instance being saved
        **kwargs: Additional keyword arguments

    Returns:
        None
    """
    # Skip if this is a new message (no id yet)
    if not instance.pk:
        return

    try:
        # Get the existing message from the database
        old_message = Message.objects.get(pk=instance.pk)

        # Check if content has changed
        if old_message.content != instance.content:
            # Store old content and sender in instance attributes for use in post_save
            instance._old_content = old_message.content
            instance._old_sender_id = old_message.sender_id
            instance._content_changed = True

            logger.info(
                f"Message content change detected for message {instance.id} "
                f"(will be logged in post_save)"
            )
    except Message.DoesNotExist:
        # Message doesn't exist yet (new message), nothing to capture
        pass
    except Exception as e:
        logger.error(
            f"Failed to capture message history for message {instance.id}: {str(e)}",
            exc_info=True,
        )


@receiver(post_save, sender=Message)
def create_notification_on_message(sender, instance, created, **kwargs):
    """
    Signal handler that creates a notification when a new Message is created
    and updates the edited flag when a message is updated.

    This signal is triggered after a Message instance is saved.
    It automatically creates a Notification for the receiving user when a new
    message is created, and updates the edited/edited_at fields when content changes.

    Args:
        sender: The model class that sent the signal (Message)
        instance: The actual instance being saved
        created: Boolean indicating if this is a new record
        **kwargs: Additional keyword arguments

    Returns:
        None
    """
    # Handle message creation - create notification
    if created:
        # Ensure receiver exists
        if not instance.receiver_id:
            logger.warning(
                f"Message {instance.id} has no receiver, skipping notification creation"
            )
            return

        try:
            # Create notification for the receiver
            Notification.objects.create(
                user=instance.receiver,
                message=instance,
                is_read=False,
            )
            logger.info(
                f"Notification created for user {instance.receiver_id} "
                f"regarding message {instance.id}"
            )
        except Exception as e:
            logger.error(
                f"Failed to create notification for message {instance.id}: {str(e)}",
                exc_info=True,
            )
    else:
        # Handle message update - create history entry and set edited flag if content changed
        if hasattr(instance, "_content_changed") and instance._content_changed:
            try:
                # Create history entry with old content
                MessageHistory.objects.create(
                    message=instance,
                    old_content=instance._old_content,
                    edited_by=instance.sender,  # Usually the sender edits their own message
                    edited_at=timezone.now(),
                )

                # Update edited fields on the message
                Message.objects.filter(pk=instance.pk).update(
                    edited=True,
                    edited_at=timezone.now(),
                )

                logger.info(
                    f"Message history created for message {instance.id} "
                    f"(edited at {timezone.now()})"
                )
            except Exception as e:
                logger.error(
                    f"Failed to create message history for message {instance.id}: {str(e)}",
                    exc_info=True,
                )


@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Signal handler that cleans up all related data when a User is deleted.

    This signal is triggered after a User instance is deleted.
    It ensures that all related data (messages, notifications, message history)
    associated with the deleted user are properly cleaned up.

    Note: Due to CASCADE relationships, messages and notifications are
    automatically deleted when a user is deleted. However, this handler
    explicitly logs the cleanup and handles any additional cleanup logic.

    Args:
        sender: The model class that sent the signal (User)
        instance: The actual instance that was deleted
        **kwargs: Additional keyword arguments

    Returns:
        None
    """
    user_id = instance.id
    username = getattr(instance, "username", "Unknown")

    try:
        logger.info(
            f"Starting cleanup for deleted user {user_id} ({username})"
        )

        # Count related objects before cleanup (for logging)
        # Note: These may already be deleted due to CASCADE, but we check anyway
        sent_messages_count = 0
        received_messages_count = 0
        notifications_count = 0
        message_history_count = 0

        try:
            # Count messages sent by the user (if any still exist)
            sent_messages_count = Message.objects.filter(sender_id=user_id).count()
        except Exception:
            pass

        try:
            # Count messages received by the user (if any still exist)
            received_messages_count = Message.objects.filter(receiver_id=user_id).count()
        except Exception:
            pass

        try:
            # Count notifications for the user (if any still exist)
            notifications_count = Notification.objects.filter(user_id=user_id).count()
        except Exception:
            pass

        try:
            # Count message history entries edited by the user
            # Note: MessageHistory.edited_by uses SET_NULL, so these won't be deleted
            # but the edited_by field will be set to NULL
            message_history_count = MessageHistory.objects.filter(edited_by_id=user_id).count()
        except Exception:
            pass

        # Messages are automatically deleted via CASCADE when user is deleted
        # Notifications are automatically deleted via CASCADE when user is deleted
        # MessageHistory entries with edited_by pointing to this user will have
        # edited_by set to NULL (due to SET_NULL)

        logger.info(
            f"Cleanup completed for user {user_id} ({username}): "
            f"{sent_messages_count} sent messages, "
            f"{received_messages_count} received messages, "
            f"{notifications_count} notifications, "
            f"{message_history_count} message history entries "
            "were associated with this user"
        )

    except Exception as e:
        logger.error(
            f"Error during cleanup for deleted user {user_id}: {str(e)}",
            exc_info=True,
        )

