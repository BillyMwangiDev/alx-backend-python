"""
Message and Notification models for the messaging app.

This module defines the Message model for storing user messages
and the Notification model for storing notifications when users receive messages.
"""
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from .managers import MessageManager, UnreadMessagesManager


class Message(models.Model):
    """
    Message model representing a message sent from one user to another.

    Fields:
        sender: ForeignKey to User model - the user who sent the message
        receiver: ForeignKey to User model - the user who receives the message
        content: TextField - the message content
        timestamp: DateTimeField - when the message was created (auto-set)
    """

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        help_text="The user who sent this message",
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_messages",
        help_text="The user who receives this message",
    )
    content = models.TextField(
        help_text="The message content",
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="When the message was created",
    )
    edited = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether the message has been edited",
    )
    edited_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="When the message was last edited",
    )
    parent_message = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        help_text="The parent message this is a reply to (null for top-level messages)",
    )
    read = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether the message has been read by the receiver",
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="When the message was read by the receiver",
    )

    # Custom managers for optimized queries
    objects = MessageManager()
    unread = UnreadMessagesManager()

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["receiver", "-timestamp"]),
            models.Index(fields=["sender", "-timestamp"]),
            models.Index(fields=["parent_message", "-timestamp"]),
            models.Index(fields=["receiver", "read", "-timestamp"]),
        ]
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self) -> str:
        """Return a string representation of the message."""
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"

    def clean(self) -> None:
        """Validate that sender and receiver are different users."""
        if self.sender_id and self.receiver_id:
            if self.sender_id == self.receiver_id:
                from django.core.exceptions import ValidationError

                raise ValidationError("Sender and receiver cannot be the same user.")

    def save(self, *args, **kwargs):
        """Override save to call clean validation."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def get_all_replies(self, max_depth=10):
        """
        Recursively get all replies to this message using optimized queries.

        This method efficiently fetches all nested replies using Django ORM
        with select_related and prefetch_related for optimal database access.

        Args:
            max_depth: Maximum recursion depth to prevent infinite loops (default: 10)

        Returns:
            list: A list of all reply messages with their nested structure

        Example:
            >>> message = Message.objects.get(id=1)
            >>> all_replies = message.get_all_replies()
        """
        def collect_replies(msg, collected=None, current_depth=0):
            """Recursively collect all reply IDs."""
            if collected is None:
                collected = []

            if current_depth >= max_depth:
                return collected

            # Get direct replies with optimized query
            direct_replies = list(
                msg.replies.select_related("sender", "receiver").order_by("timestamp")
            )

            for reply in direct_replies:
                collected.append(reply)
                # Recursively collect nested replies
                collect_replies(reply, collected, current_depth + 1)

            return collected

        return collect_replies(self)

    def get_thread_depth(self):
        """
        Get the depth of this message in the thread (0 for top-level messages).

        Returns:
            int: The depth level of this message in the thread

        Example:
            >>> message.get_thread_depth()  # 0 for top-level, 1 for first reply, etc.
        """
        depth = 0
        current = self.parent_message
        while current is not None:
            depth += 1
            current = current.parent_message
            if depth > 100:  # Safety check to prevent infinite loops
                break
        return depth

    def get_root_message(self):
        """
        Get the root message (top-level parent) of this thread.

        Returns:
            Message: The root message, or self if this is already a root message

        Example:
            >>> root = reply_message.get_root_message()
        """
        current = self
        while current.parent_message is not None:
            current = current.parent_message
        return current

    def is_reply(self):
        """
        Check if this message is a reply to another message.

        Returns:
            bool: True if this message has a parent, False otherwise
        """
        return self.parent_message is not None

    def get_reply_count(self):
        """
        Get the total count of all replies (including nested replies) to this message.

        Returns:
            int: Total number of replies

        Example:
            >>> message.get_reply_count()  # Returns total nested reply count
        """
        def count_replies(msg, counted=None):
            """Recursive helper to count all replies."""
            if counted is None:
                counted = set()

            if msg.id in counted:
                return 0

            counted.add(msg.id)
            count = 0
            for reply in msg.replies.all():
                count += 1 + count_replies(reply, counted)
            return count

        return count_replies(self)

    def mark_as_read(self, save=True):
        """
        Mark this message as read by the receiver.

        Args:
            save: Whether to save the changes immediately (default: True)

        Returns:
            Message: The message instance

        Example:
            >>> message.mark_as_read()
        """
        from django.utils import timezone

        self.read = True
        self.read_at = timezone.now()

        if save:
            self.save(update_fields=["read", "read_at"])

        return self

    def mark_as_unread(self, save=True):
        """
        Mark this message as unread by the receiver.

        Args:
            save: Whether to save the changes immediately (default: True)

        Returns:
            Message: The message instance

        Example:
            >>> message.mark_as_unread()
        """
        self.read = False
        self.read_at = None

        if save:
            self.save(update_fields=["read", "read_at"])

        return self


class Notification(models.Model):
    """
    Notification model for storing notifications when users receive messages.

    Fields:
        user: ForeignKey to User model - the user who receives the notification
        message: ForeignKey to Message model - the message that triggered the notification
        is_read: BooleanField - whether the notification has been read
        created_at: DateTimeField - when the notification was created (auto-set)
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        help_text="The user who receives this notification",
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="notifications",
        help_text="The message that triggered this notification",
    )
    is_read = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether the notification has been read",
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="When the notification was created",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["user", "is_read"]),
        ]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        # Ensure one notification per message per user
        unique_together = [["user", "message"]]

    def __str__(self) -> str:
        """Return a string representation of the notification."""
        read_status = "read" if self.is_read else "unread"
        return f"Notification for {self.user} - {read_status}"


class MessageHistory(models.Model):
    """
    MessageHistory model for storing historical versions of edited messages.

    This model stores the previous content of a message before it was edited,
    allowing users to view the edit history of messages.

    Fields:
        message: ForeignKey to Message model - the message being edited
        old_content: TextField - the previous content of the message
        edited_at: DateTimeField - when this version was saved (when edit occurred)
        edited_by: ForeignKey to User model - the user who made the edit
    """

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="history",
        help_text="The message that was edited",
    )
    old_content = models.TextField(
        help_text="The previous content of the message before editing",
    )
    edited_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="When this edit was made",
    )
    edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="message_edits",
        help_text="The user who made this edit",
    )

    class Meta:
        ordering = ["-edited_at"]
        indexes = [
            models.Index(fields=["message", "-edited_at"]),
            models.Index(fields=["edited_at"]),
        ]
        verbose_name = "Message History"
        verbose_name_plural = "Message History"
        get_latest_by = "edited_at"

    def __str__(self) -> str:
        """Return a string representation of the message history entry."""
        return f"History for message {self.message.id} edited at {self.edited_at}"

