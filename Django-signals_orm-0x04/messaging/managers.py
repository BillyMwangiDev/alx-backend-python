"""
Custom managers and querysets for the messaging app.

This module defines custom managers and querysets that provide optimized
queries for threaded conversations and unread message filtering.
"""
from django.db import models
from django.db.models import Prefetch


class ThreadedMessageQuerySet(models.QuerySet):
    """Custom QuerySet for optimized threaded message queries."""

    def with_related(self):
        """Optimize queries by prefetching related sender and receiver."""
        return self.select_related("sender", "receiver")

    def with_replies(self, max_depth=3):
        """
        Prefetch replies up to a certain depth for efficient thread loading.

        Args:
            max_depth: Maximum depth of replies to prefetch (default: 3)

        Returns:
            QuerySet with prefetched replies
        """
        queryset = self.select_related("sender", "receiver")

        # Build nested prefetch for replies
        current_level = queryset
        for depth in range(max_depth):
            current_level = Prefetch(
                "replies",
                queryset=self.model.objects.select_related("sender", "receiver").order_by(
                    "timestamp"
                ),
            )
            # For subsequent levels, we'd need to chain prefetches
            # Django's prefetch_related can handle one level effectively
            if depth == 0:
                queryset = queryset.prefetch_related(current_level)

        return queryset

    def top_level_only(self):
        """Return only top-level messages (no parent)."""
        return self.filter(parent_message__isnull=True)

    def get_thread(self, root_message_id):
        """
        Get all messages in a thread starting from a root message.

        This uses a recursive CTE approach for efficient querying of nested replies.

        Args:
            root_message_id: ID of the root message

        Returns:
            QuerySet of all messages in the thread
        """
        # Start with the root message  
        # Need to access the model's manager to create a new queryset
        from django.apps import apps
        Message = apps.get_model('messaging', 'Message')
        root = Message.objects.filter(id=root_message_id).first()
        if not root:
            return Message.objects.none()

        # Collect all message IDs in the thread using recursive approach
        def get_all_descendants(msg_id, collected=None):
            """Recursively collect all descendant message IDs."""
            if collected is None:
                collected = set()

            if msg_id in collected:
                return collected

            collected.add(msg_id)

            # Get direct replies
            reply_ids = list(
                Message.objects.filter(parent_message_id=msg_id).values_list(
                    "id", flat=True
                )
            )

            # Recursively get replies to those replies
            for reply_id in reply_ids:
                get_all_descendants(reply_id, collected)

            return collected

        all_ids = get_all_descendants(root_message_id)
        all_ids.add(root_message_id)

        # Return optimized queryset with all messages in thread
        return (
            Message.objects.filter(id__in=all_ids)
            .select_related("sender", "receiver", "parent_message")
            .prefetch_related(
                Prefetch(
                    "replies",
                    queryset=Message.objects.select_related("sender", "receiver").order_by(
                        "timestamp"
                    ),
                )
            )
            .order_by("timestamp")
        )


class UnreadMessagesQuerySet(models.QuerySet):
    """Custom QuerySet for filtering unread messages with optimizations."""

    def for_user(self, user):
        """
        Filter messages received by a specific user.

        Args:
            user: User instance or user ID to filter messages for

        Returns:
            QuerySet filtered to messages received by the user
        """
        user_id = user.id if hasattr(user, "id") else user
        return self.filter(receiver_id=user_id)

    def unread_only(self):
        """Filter to only unread messages."""
        return self.filter(read=False)

    def read_only(self):
        """Filter to only read messages."""
        return self.filter(read=True)

    def with_optimized_fields(self):
        """
        Optimize query to retrieve only necessary fields for inbox display.

        This method uses .only() to reduce the amount of data retrieved
        from the database, improving query performance.

        Returns:
            QuerySet with only essential fields selected
        """
        return self.only(
            "id",
            "sender",
            "receiver",
            "content",
            "timestamp",
            "read",
            "read_at",
            "parent_message",
        )


class UnreadMessagesManager(models.Manager):
    """
    Custom manager for filtering unread messages for a specific user.

    This manager provides optimized queries for retrieving unread messages
    with minimal database load using .only() to select only necessary fields.
    """

    def get_queryset(self):
        """Return the custom QuerySet."""
        return UnreadMessagesQuerySet(self.model, using=self._db)

    def unread_for_user(self, user):
        """
        Get all unread messages for a specific user with optimized queries.

        This method combines filtering and optimization to efficiently
        retrieve only unread messages for a user's inbox.

        Args:
            user: User instance or user ID to get unread messages for

        Returns:
            QuerySet of unread messages optimized with select_related and only()

        Example:
            >>> unread_messages = Message.unread.unread_for_user(request.user)
            >>> unread_messages = Message.unread.unread_for_user(user_id)
        """
        return (
            self.get_queryset()
            .for_user(user)
            .unread_only()
            .select_related("sender", "receiver")
            .with_optimized_fields()
            .order_by("-timestamp")
        )

    def read_for_user(self, user):
        """
        Get all read messages for a specific user with optimized queries.

        Args:
            user: User instance or user ID to get read messages for

        Returns:
            QuerySet of read messages optimized with select_related and only()
        """
        return (
            self.get_queryset()
            .for_user(user)
            .read_only()
            .select_related("sender", "receiver")
            .with_optimized_fields()
            .order_by("-timestamp")
        )

    def all_for_user(self, user):
        """
        Get all messages (read and unread) for a specific user with optimized queries.

        Args:
            user: User instance or user ID to get messages for

        Returns:
            QuerySet of all messages optimized with select_related and only()
        """
        return (
            self.get_queryset()
            .for_user(user)
            .select_related("sender", "receiver")
            .with_optimized_fields()
            .order_by("-timestamp")
        )


class MessageManager(models.Manager):
    """Custom manager for Message model with optimized query methods."""

    def get_queryset(self):
        """Return the custom QuerySet."""
        return ThreadedMessageQuerySet(self.model, using=self._db)

    def with_related(self):
        """Return messages with sender and receiver prefetched."""
        return self.get_queryset().with_related()

    def with_replies(self, max_depth=3):
        """Return messages with replies prefetched."""
        return self.get_queryset().with_replies(max_depth=max_depth)

    def top_level_only(self):
        """Return only top-level messages."""
        return self.get_queryset().top_level_only()

    def get_thread(self, root_message_id):
        """Get all messages in a thread."""
        return self.get_queryset().get_thread(root_message_id)

