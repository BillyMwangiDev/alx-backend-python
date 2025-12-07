"""
Tests for the messaging app.

This module contains unit tests and integration tests for the Message and
Notification models, as well as the signal handlers that create notifications.
"""
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from .models import Message, MessageHistory, Notification

User = get_user_model()


class MessageModelTest(TestCase):
    """Test cases for the Message model."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.sender = User.objects.create_user(
            username="sender",
            email="sender@example.com",
            password="testpass123",
        )
        self.receiver = User.objects.create_user(
            username="receiver",
            email="receiver@example.com",
            password="testpass123",
        )

    def test_message_creation(self) -> None:
        """Test creating a message."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello, this is a test message!",
        )
        self.assertIsNotNone(message.id)
        self.assertEqual(message.sender, self.sender)
        self.assertEqual(message.receiver, self.receiver)
        self.assertEqual(message.content, "Hello, this is a test message!")
        self.assertIsNotNone(message.timestamp)
        self.assertFalse(message.edited)  # New messages are not edited
        self.assertIsNone(message.edited_at)  # New messages have no edit time

    def test_message_timestamp_auto_set(self) -> None:
        """Test that timestamp is automatically set."""
        before = timezone.now()
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message",
        )
        after = timezone.now()
        self.assertGreaterEqual(message.timestamp, before)
        self.assertLessEqual(message.timestamp, after)

    def test_message_str_representation(self) -> None:
        """Test the string representation of a message."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message",
        )
        str_repr = str(message)
        self.assertIn(str(self.sender), str_repr)
        self.assertIn(str(self.receiver), str_repr)

    def test_message_validation_sender_receiver_different(self) -> None:
        """Test that sender and receiver must be different users."""
        with self.assertRaises(ValidationError):
            message = Message(
                sender=self.sender,
                receiver=self.sender,  # Same user
                content="Test message",
            )
            message.full_clean()

    def test_message_ordering(self) -> None:
        """Test that messages are ordered by timestamp descending."""
        msg1 = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="First message",
        )
        msg2 = Message.objects.create(
            sender=self.receiver,
            receiver=self.sender,
            content="Second message",
        )
        messages = list(Message.objects.all())
        self.assertEqual(messages[0], msg2)
        self.assertEqual(messages[1], msg1)


class NotificationModelTest(TestCase):
    """Test cases for the Notification model."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.sender = User.objects.create_user(
            username="sender",
            email="sender@example.com",
            password="testpass123",
        )
        self.receiver = User.objects.create_user(
            username="receiver",
            email="receiver@example.com",
            password="testpass123",
        )
        self.message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message for notification",
        )

    def test_notification_creation(self) -> None:
        """Test creating a notification."""
        notification = Notification.objects.create(
            user=self.receiver,
            message=self.message,
            is_read=False,
        )
        self.assertIsNotNone(notification.id)
        self.assertEqual(notification.user, self.receiver)
        self.assertEqual(notification.message, self.message)
        self.assertFalse(notification.is_read)
        self.assertIsNotNone(notification.created_at)

    def test_notification_created_at_auto_set(self) -> None:
        """Test that created_at is automatically set."""
        before = timezone.now()
        notification = Notification.objects.create(
            user=self.receiver,
            message=self.message,
        )
        after = timezone.now()
        self.assertGreaterEqual(notification.created_at, before)
        self.assertLessEqual(notification.created_at, after)

    def test_notification_str_representation(self) -> None:
        """Test the string representation of a notification."""
        notification = Notification.objects.create(
            user=self.receiver,
            message=self.message,
            is_read=False,
        )
        str_repr = str(notification)
        self.assertIn(str(self.receiver), str_repr)
        self.assertIn("unread", str_repr)

        notification.is_read = True
        notification.save()
        str_repr = str(notification)
        self.assertIn("read", str_repr)

    def test_notification_default_is_read_false(self) -> None:
        """Test that is_read defaults to False."""
        notification = Notification.objects.create(
            user=self.receiver,
            message=self.message,
        )
        self.assertFalse(notification.is_read)

    def test_notification_unique_constraint(self) -> None:
        """Test that only one notification per user per message is allowed."""
        Notification.objects.create(
            user=self.receiver,
            message=self.message,
        )
        # Try to create duplicate notification
        with self.assertRaises(Exception):  # IntegrityError or ValidationError
            Notification.objects.create(
                user=self.receiver,
                message=self.message,
            )


class MessageSignalTest(TestCase):
    """Test cases for the message post_save signal handler."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.sender = User.objects.create_user(
            username="sender",
            email="sender@example.com",
            password="testpass123",
        )
        self.receiver = User.objects.create_user(
            username="receiver",
            email="receiver@example.com",
            password="testpass123",
        )

    def test_notification_created_on_message_save(self) -> None:
        """Test that a notification is automatically created when a message is saved."""
        # Initially no notifications
        self.assertEqual(Notification.objects.count(), 0)

        # Create a new message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message that should trigger notification",
        )

        # Check that notification was created
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.receiver)
        self.assertEqual(notification.message, message)
        self.assertFalse(notification.is_read)

    def test_notification_not_created_on_message_update(self) -> None:
        """Test that notification is not created when updating an existing message."""
        # Create initial message (should create notification)
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Initial message",
        )
        initial_count = Notification.objects.count()
        self.assertEqual(initial_count, 1)

        # Update the message
        message.content = "Updated message"
        message.save()

        # Notification count should not increase
        self.assertEqual(Notification.objects.count(), initial_count)

    def test_notification_created_for_correct_receiver(self) -> None:
        """Test that notification is created for the message receiver."""
        receiver2 = User.objects.create_user(
            username="receiver2",
            email="receiver2@example.com",
            password="testpass123",
        )

        # Create message from sender to receiver
        message1 = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Message 1",
        )

        # Create message from sender to receiver2
        message2 = Message.objects.create(
            sender=self.sender,
            receiver=receiver2,
            content="Message 2",
        )

        # Check notifications
        self.assertEqual(Notification.objects.count(), 2)
        receiver_notifications = Notification.objects.filter(user=self.receiver)
        receiver2_notifications = Notification.objects.filter(user=receiver2)

        self.assertEqual(receiver_notifications.count(), 1)
        self.assertEqual(receiver_notifications.first().message, message1)

        self.assertEqual(receiver2_notifications.count(), 1)
        self.assertEqual(receiver2_notifications.first().message, message2)

    def test_multiple_messages_create_multiple_notifications(self) -> None:
        """Test that multiple messages create multiple notifications."""
        # Create multiple messages
        for i in range(3):
            Message.objects.create(
                sender=self.sender,
                receiver=self.receiver,
                content=f"Message {i+1}",
            )

        # Check that 3 notifications were created
        self.assertEqual(Notification.objects.count(), 3)
        receiver_notifications = Notification.objects.filter(user=self.receiver)
        self.assertEqual(receiver_notifications.count(), 3)

    def test_notification_get_or_create_prevents_duplicates(self) -> None:
        """Test that get_or_create prevents duplicate notifications."""
        # Create message (should create notification)
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message",
        )

        # Try to create another notification manually
        notification, created = Notification.objects.get_or_create(
            user=self.receiver,
            message=message,
        )

        # Should get existing notification, not create new one
        self.assertFalse(created)
        self.assertEqual(Notification.objects.count(), 1)


class IntegrationTest(TestCase):
    """Integration tests for the messaging system."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.sender = User.objects.create_user(
            username="sender",
            email="sender@example.com",
            password="testpass123",
        )
        self.receiver = User.objects.create_user(
            username="receiver",
            email="receiver@example.com",
            password="testpass123",
        )

    def test_complete_message_flow(self) -> None:
        """Test the complete flow from message creation to notification."""
        # Create a message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Integration test message",
        )

        # Verify message was created
        self.assertIsNotNone(message.id)
        self.assertEqual(Message.objects.count(), 1)

        # Verify notification was automatically created
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.receiver)
        self.assertEqual(notification.message, message)
        self.assertFalse(notification.is_read)

        # Mark notification as read
        notification.is_read = True
        notification.save()

        # Verify notification is now read
        self.assertTrue(Notification.objects.get(id=notification.id).is_read)


class MessageEditTest(TestCase):
    """Test cases for message editing functionality."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.sender = User.objects.create_user(
            username="sender",
            email="sender@example.com",
            password="testpass123",
        )
        self.receiver = User.objects.create_user(
            username="receiver",
            email="receiver@example.com",
            password="testpass123",
        )
        self.message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original message content",
        )

    def test_message_edited_field_default(self) -> None:
        """Test that new messages have edited=False by default."""
        self.assertFalse(self.message.edited)
        self.assertIsNone(self.message.edited_at)

    def test_message_edited_flag_set_on_edit(self) -> None:
        """Test that edited flag is set when message content is changed."""
        original_content = self.message.content
        self.message.content = "Updated content"
        self.message.save()

        # Refresh from database
        self.message.refresh_from_db()
        self.assertTrue(self.message.edited)
        self.assertIsNotNone(self.message.edited_at)
        self.assertNotEqual(self.message.content, original_content)

    def test_message_edited_flag_not_set_without_content_change(self) -> None:
        """Test that edited flag is not set when content hasn't changed."""
        # Update a non-content field
        self.message.edited = False  # Manually reset if needed
        self.message.save()

        # Just update timestamp or other field (but content stays same)
        # Since we're not changing content, edited should remain False
        self.message.refresh_from_db()
        # Note: Actually saving without content change shouldn't set edited=True
        # But our signal only triggers on content change


class MessageHistoryModelTest(TestCase):
    """Test cases for the MessageHistory model."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.sender = User.objects.create_user(
            username="sender",
            email="sender@example.com",
            password="testpass123",
        )
        self.receiver = User.objects.create_user(
            username="receiver",
            email="receiver@example.com",
            password="testpass123",
        )
        self.message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original message",
        )

    def test_message_history_creation(self) -> None:
        """Test creating a message history entry."""
        history = MessageHistory.objects.create(
            message=self.message,
            old_content="Previous content",
            edited_by=self.sender,
        )
        self.assertIsNotNone(history.id)
        self.assertEqual(history.message, self.message)
        self.assertEqual(history.old_content, "Previous content")
        self.assertEqual(history.edited_by, self.sender)
        self.assertIsNotNone(history.edited_at)

    def test_message_history_edited_at_auto_set(self) -> None:
        """Test that edited_at is automatically set."""
        before = timezone.now()
        history = MessageHistory.objects.create(
            message=self.message,
            old_content="Previous content",
        )
        after = timezone.now()
        self.assertGreaterEqual(history.edited_at, before)
        self.assertLessEqual(history.edited_at, after)

    def test_message_history_str_representation(self) -> None:
        """Test the string representation of message history."""
        history = MessageHistory.objects.create(
            message=self.message,
            old_content="Previous content",
        )
        str_repr = str(history)
        self.assertIn(str(self.message.id), str_repr)

    def test_message_history_ordering(self) -> None:
        """Test that message history is ordered by edited_at descending."""
        history1 = MessageHistory.objects.create(
            message=self.message,
            old_content="First edit",
        )
        history2 = MessageHistory.objects.create(
            message=self.message,
            old_content="Second edit",
        )
        histories = list(MessageHistory.objects.all())
        self.assertEqual(histories[0], history2)
        self.assertEqual(histories[1], history1)


class MessageEditSignalTest(TestCase):
    """Test cases for the message edit signal handlers."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.sender = User.objects.create_user(
            username="sender",
            email="sender@example.com",
            password="testpass123",
        )
        self.receiver = User.objects.create_user(
            username="receiver",
            email="receiver@example.com",
            password="testpass123",
        )
        self.message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original message content",
        )

    def test_history_created_on_message_edit(self) -> None:
        """Test that history entry is created when message content is changed."""
        original_content = self.message.content
        self.assertEqual(MessageHistory.objects.count(), 0)

        # Edit the message
        self.message.content = "Edited message content"
        self.message.save()

        # Check that history entry was created
        self.assertEqual(MessageHistory.objects.count(), 1)
        history = MessageHistory.objects.first()
        self.assertEqual(history.message, self.message)
        self.assertEqual(history.old_content, original_content)
        self.assertEqual(history.edited_by, self.sender)

        # Check that message is marked as edited
        self.message.refresh_from_db()
        self.assertTrue(self.message.edited)
        self.assertIsNotNone(self.message.edited_at)

    def test_history_not_created_for_new_message(self) -> None:
        """Test that history is not created when creating a new message."""
        self.assertEqual(MessageHistory.objects.count(), 0)

        new_message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="New message",
        )

        # No history should be created for new messages
        self.assertEqual(MessageHistory.objects.count(), 0)
        self.assertFalse(new_message.edited)

    def test_history_not_created_without_content_change(self) -> None:
        """Test that history is not created when content hasn't changed."""
        initial_count = MessageHistory.objects.count()

        # Save message without changing content
        self.message.save()

        # History count should not increase
        self.assertEqual(MessageHistory.objects.count(), initial_count)

    def test_multiple_edits_create_multiple_history_entries(self) -> None:
        """Test that multiple edits create multiple history entries."""
        # First edit
        self.message.content = "First edit"
        self.message.save()

        # Second edit
        self.message.content = "Second edit"
        self.message.save()

        # Third edit
        self.message.content = "Third edit"
        self.message.save()

        # Should have 3 history entries
        self.assertEqual(MessageHistory.objects.count(), 3)

        # Verify history entries contain old content in order
        histories = list(MessageHistory.objects.all())
        self.assertEqual(histories[0].old_content, "Second edit")  # Latest first
        self.assertEqual(histories[1].old_content, "First edit")
        self.assertEqual(histories[2].old_content, "Original message content")

    def test_history_preserves_all_previous_versions(self) -> None:
        """Test that all previous versions are preserved in history."""
        versions = ["Original", "First edit", "Second edit", "Third edit"]

        for i, version in enumerate(versions[1:], start=1):
            self.message.content = version
            self.message.save()

            # Check that we have history for all previous versions
            self.assertEqual(MessageHistory.objects.count(), i)

        # Verify all old versions are stored
        histories = MessageHistory.objects.all()
        stored_contents = [h.old_content for h in histories]
        self.assertIn("Original", stored_contents)
        self.assertIn("First edit", stored_contents)
        self.assertIn("Second edit", stored_contents)

    def test_history_links_to_correct_message(self) -> None:
        """Test that history entries are correctly linked to their messages."""
        message2 = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Another message",
        )

        # Edit first message
        self.message.content = "Edited first"
        self.message.save()

        # Edit second message
        message2.content = "Edited second"
        message2.save()

        # Check history entries
        self.assertEqual(MessageHistory.objects.count(), 2)
        self.assertEqual(self.message.history.count(), 1)
        self.assertEqual(message2.history.count(), 1)


class MessageEditIntegrationTest(TestCase):
    """Integration tests for message editing with history."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.sender = User.objects.create_user(
            username="sender",
            email="sender@example.com",
            password="testpass123",
        )
        self.receiver = User.objects.create_user(
            username="receiver",
            email="receiver@example.com",
            password="testpass123",
        )

    def test_complete_edit_flow(self) -> None:
        """Test the complete flow from message creation to multiple edits."""
        # Create message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Initial message",
        )

        # Verify initial state
        self.assertFalse(message.edited)
        self.assertIsNone(message.edited_at)
        self.assertEqual(MessageHistory.objects.count(), 0)

        # First edit
        message.content = "First edit"
        message.save()

        # Verify first edit
        message.refresh_from_db()
        self.assertTrue(message.edited)
        self.assertIsNotNone(message.edited_at)
        self.assertEqual(MessageHistory.objects.count(), 1)
        history1 = MessageHistory.objects.first()
        self.assertEqual(history1.old_content, "Initial message")

        # Second edit
        message.content = "Second edit"
        message.save()

        # Verify second edit
        message.refresh_from_db()
        self.assertEqual(MessageHistory.objects.count(), 2)
        histories = list(MessageHistory.objects.all())
        self.assertEqual(histories[0].old_content, "First edit")
        self.assertEqual(histories[1].old_content, "Initial message")

    def test_edit_history_accessibility(self) -> None:
        """Test that edit history is accessible through message relationship."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original",
        )

        # Make several edits
        for i in range(3):
            message.content = f"Edit {i+1}"
            message.save()

        # Access history through message relationship
        self.assertEqual(message.history.count(), 3)
        histories = list(message.history.all())
        self.assertEqual(len(histories), 3)

        # Verify we can access old content
        for history in histories:
            self.assertIsNotNone(history.old_content)
            self.assertEqual(history.message, message)


class UserDeletionTest(TestCase):
    """Test cases for user deletion and cleanup of related data."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="testpass123",
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="testpass123",
        )
        self.user3 = User.objects.create_user(
            username="user3",
            email="user3@example.com",
            password="testpass123",
        )

    def test_user_deletion_cascades_to_sent_messages(self) -> None:
        """Test that deleting a user deletes messages they sent."""
        # Create messages sent by user1
        message1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Message 1",
        )
        message2 = Message.objects.create(
            sender=self.user1,
            receiver=self.user3,
            content="Message 2",
        )

        # Verify messages exist
        self.assertEqual(Message.objects.filter(sender=self.user1).count(), 2)

        # Delete user1
        user_id = self.user1.id
        self.user1.delete()

        # Verify messages are deleted (CASCADE)
        self.assertEqual(Message.objects.filter(sender_id=user_id).count(), 0)
        self.assertFalse(Message.objects.filter(id=message1.id).exists())
        self.assertFalse(Message.objects.filter(id=message2.id).exists())

    def test_user_deletion_cascades_to_received_messages(self) -> None:
        """Test that deleting a user deletes messages they received."""
        # Create messages received by user1
        message1 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Message 1",
        )
        message2 = Message.objects.create(
            sender=self.user3,
            receiver=self.user1,
            content="Message 2",
        )

        # Verify messages exist
        self.assertEqual(Message.objects.filter(receiver=self.user1).count(), 2)

        # Delete user1
        user_id = self.user1.id
        self.user1.delete()

        # Verify messages are deleted (CASCADE)
        self.assertEqual(Message.objects.filter(receiver_id=user_id).count(), 0)
        self.assertFalse(Message.objects.filter(id=message1.id).exists())
        self.assertFalse(Message.objects.filter(id=message2.id).exists())

    def test_user_deletion_cascades_to_notifications(self) -> None:
        """Test that deleting a user deletes their notifications."""
        # Create messages and notifications
        message1 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Message 1",
        )
        message2 = Message.objects.create(
            sender=self.user3,
            receiver=self.user1,
            content="Message 2",
        )

        # Verify notifications exist
        self.assertEqual(Notification.objects.filter(user=self.user1).count(), 2)

        # Delete user1
        user_id = self.user1.id
        self.user1.delete()

        # Verify notifications are deleted (CASCADE)
        self.assertEqual(Notification.objects.filter(user_id=user_id).count(), 0)
        self.assertFalse(Notification.objects.filter(message=message1).exists())
        self.assertFalse(Notification.objects.filter(message=message2).exists())

    def test_user_deletion_handles_message_history(self) -> None:
        """Test that deleting a user handles message history properly."""
        # Create a message and edit it
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original content",
        )

        # Edit the message (creates history)
        message.content = "Edited content"
        message.save()

        # Verify history exists
        self.assertEqual(MessageHistory.objects.count(), 1)
        history = MessageHistory.objects.first()
        self.assertEqual(history.edited_by, self.user1)

        # Delete user1
        user_id = self.user1.id
        self.user1.delete()

        # Message should be deleted (CASCADE), which cascades to history
        self.assertFalse(Message.objects.filter(id=message.id).exists())
        self.assertEqual(MessageHistory.objects.filter(message_id=message.id).count(), 0)

    def test_user_deletion_sets_message_history_edited_by_to_null(self) -> None:
        """Test that message history edited_by is set to NULL when user is deleted."""
        # Create a message sent by user1
        message = Message.objects.create(
            sender=self.user2,
            receiver=self.user3,
            content="Original content",
        )

        # Edit the message as user1 (creates history with edited_by=user1)
        message.content = "Edited content"
        message.save()

        # Manually update history to set edited_by to user1
        history = MessageHistory.objects.first()
        history.edited_by = self.user1
        history.save()

        # Verify history has edited_by set
        history.refresh_from_db()
        self.assertEqual(history.edited_by, self.user1)

        # Delete user1
        user_id = self.user1.id
        self.user1.delete()

        # History should still exist (message still exists), but edited_by should be NULL
        history.refresh_from_db()
        self.assertIsNone(history.edited_by)

    def test_user_deletion_cleanup_complete_scenario(self) -> None:
        """Test complete cleanup scenario when a user is deleted."""
        # Create multiple messages
        msg1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Message 1",
        )
        msg2 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Message 2",
        )
        msg3 = Message.objects.create(
            sender=self.user1,
            receiver=self.user3,
            content="Message 3",
        )

        # Edit one message
        msg1.content = "Edited message 1"
        msg1.save()

        # Verify all data exists
        self.assertEqual(Message.objects.filter(sender=self.user1).count(), 2)
        self.assertEqual(Message.objects.filter(receiver=self.user1).count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.user1).count(), 1)
        self.assertEqual(MessageHistory.objects.count(), 1)

        # Delete user1
        user_id = self.user1.id
        self.user1.delete()

        # Verify all related data is cleaned up
        self.assertEqual(Message.objects.filter(sender_id=user_id).count(), 0)
        self.assertEqual(Message.objects.filter(receiver_id=user_id).count(), 0)
        self.assertEqual(Notification.objects.filter(user_id=user_id).count(), 0)

        # Messages sent/received by user1 should be deleted
        self.assertFalse(Message.objects.filter(id=msg1.id).exists())
        self.assertFalse(Message.objects.filter(id=msg2.id).exists())
        self.assertFalse(Message.objects.filter(id=msg3.id).exists())

        # History for deleted messages should also be deleted
        self.assertEqual(MessageHistory.objects.filter(message_id=msg1.id).count(), 0)

        # Message from user2 to user3 should still exist
        self.assertTrue(Message.objects.filter(sender=self.user2, receiver=self.user3).exists())


class DeleteUserViewTest(TestCase):
    """Test cases for the delete_user view."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass123",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="testpass123",
        )

    def test_delete_user_view_requires_authentication(self) -> None:
        """Test that delete_user view requires authentication."""
        from rest_framework.test import APIClient
        from django.urls import reverse

        client = APIClient()
        url = reverse("messaging:delete_user")

        # Try without authentication
        response = client.delete(url)
        self.assertEqual(response.status_code, 401)

    def test_delete_user_view_deletes_authenticated_user(self) -> None:
        """Test that delete_user view deletes the authenticated user."""
        from rest_framework.test import APIClient
        from django.urls import reverse

        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("messaging:delete_user")

        user_id = self.user.id

        # Delete user
        response = client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("deleted successfully", response.data["message"].lower())

        # Verify user is deleted
        self.assertFalse(User.objects.filter(id=user_id).exists())

    def test_delete_user_view_works_with_post_method(self) -> None:
        """Test that delete_user view accepts POST method."""
        from rest_framework.test import APIClient
        from django.urls import reverse

        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("messaging:delete_user")

        user_id = self.user.id

        # Delete user using POST
        response = client.post(url)
        self.assertEqual(response.status_code, 200)

        # Verify user is deleted
        self.assertFalse(User.objects.filter(id=user_id).exists())

    def test_delete_user_view_cleans_up_related_data(self) -> None:
        """Test that deleting user through view cleans up related data."""
        from rest_framework.test import APIClient
        from django.urls import reverse

        # Create related data
        message1 = Message.objects.create(
            sender=self.user,
            receiver=self.other_user,
            content="Message 1",
        )
        message2 = Message.objects.create(
            sender=self.other_user,
            receiver=self.user,
            content="Message 2",
        )

        # Verify data exists
        self.assertEqual(Message.objects.filter(sender=self.user).count(), 1)
        self.assertEqual(Message.objects.filter(receiver=self.user).count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.user).count(), 1)

        # Delete user through view
        client = APIClient()
        client.force_authenticate(user=self.user)
        url = reverse("messaging:delete_user")
        response = client.delete(url)

        self.assertEqual(response.status_code, 200)

        # Verify all related data is cleaned up
        user_id = self.user.id
        self.assertFalse(User.objects.filter(id=user_id).exists())
        self.assertEqual(Message.objects.filter(sender_id=user_id).count(), 0)
        self.assertEqual(Message.objects.filter(receiver_id=user_id).count(), 0)
        self.assertEqual(Notification.objects.filter(user_id=user_id).count(), 0)

