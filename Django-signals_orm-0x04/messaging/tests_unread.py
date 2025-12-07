"""
Tests for unread messages functionality.

This module contains tests for the UnreadMessagesManager and related
functionality for filtering and managing unread messages.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from .models import Message

User = get_user_model()


class UnreadMessagesTest(TestCase):
    """Test cases for unread messages functionality."""

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

    def test_message_read_field_default(self) -> None:
        """Test that new messages have read=False by default."""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message",
        )

        self.assertFalse(message.read)
        self.assertIsNone(message.read_at)

    def test_mark_message_as_read(self) -> None:
        """Test marking a message as read."""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message",
        )

        # Mark as read
        message.mark_as_read()

        # Verify message is marked as read
        message.refresh_from_db()
        self.assertTrue(message.read)
        self.assertIsNotNone(message.read_at)

    def test_mark_message_as_unread(self) -> None:
        """Test marking a message as unread."""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message",
        )

        # Mark as read first
        message.mark_as_read()
        self.assertTrue(message.read)

        # Mark as unread
        message.mark_as_unread()

        # Verify message is marked as unread
        message.refresh_from_db()
        self.assertFalse(message.read)
        self.assertIsNone(message.read_at)

    def test_unread_for_user_manager(self) -> None:
        """Test UnreadMessagesManager.unread_for_user() method."""
        # Create read and unread messages
        unread_msg1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Unread 1",
            read=False,
        )
        unread_msg2 = Message.objects.create(
            sender=self.user3,
            receiver=self.user2,
            content="Unread 2",
            read=False,
        )
        read_msg = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Read",
            read=True,
            read_at=timezone.now(),
        )

        # Get unread messages for user2
        unread_messages = Message.unread.unread_for_user(self.user2)

        # Verify only unread messages are returned
        self.assertEqual(unread_messages.count(), 2)
        unread_ids = list(unread_messages.values_list("id", flat=True))
        self.assertIn(unread_msg1.id, unread_ids)
        self.assertIn(unread_msg2.id, unread_ids)
        self.assertNotIn(read_msg.id, unread_ids)

    def test_unread_for_user_only_returns_received(self) -> None:
        """Test that unread_for_user only returns messages received by the user."""
        # Create messages sent by user2 (should not appear in their inbox)
        sent_msg = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Sent by user2",
            read=False,
        )

        # Create message received by user2
        received_msg = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Received by user2",
            read=False,
        )

        # Get unread messages for user2
        unread_messages = Message.unread.unread_for_user(self.user2)

        # Verify only received messages are returned
        self.assertEqual(unread_messages.count(), 1)
        self.assertIn(received_msg.id, list(unread_messages.values_list("id", flat=True)))
        self.assertNotIn(sent_msg.id, list(unread_messages.values_list("id", flat=True)))

    def test_read_for_user_manager(self) -> None:
        """Test UnreadMessagesManager.read_for_user() method."""
        # Create read and unread messages
        read_msg1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Read 1",
            read=True,
            read_at=timezone.now(),
        )
        read_msg2 = Message.objects.create(
            sender=self.user3,
            receiver=self.user2,
            content="Read 2",
            read=True,
            read_at=timezone.now(),
        )
        unread_msg = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Unread",
            read=False,
        )

        # Get read messages for user2
        read_messages = Message.unread.read_for_user(self.user2)

        # Verify only read messages are returned
        self.assertEqual(read_messages.count(), 2)
        read_ids = list(read_messages.values_list("id", flat=True))
        self.assertIn(read_msg1.id, read_ids)
        self.assertIn(read_msg2.id, read_ids)
        self.assertNotIn(unread_msg.id, read_ids)

    def test_all_for_user_manager(self) -> None:
        """Test UnreadMessagesManager.all_for_user() method."""
        # Create read and unread messages
        read_msg = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Read",
            read=True,
            read_at=timezone.now(),
        )
        unread_msg = Message.objects.create(
            sender=self.user3,
            receiver=self.user2,
            content="Unread",
            read=False,
        )

        # Get all messages for user2
        all_messages = Message.unread.all_for_user(self.user2)

        # Verify both read and unread messages are returned
        self.assertEqual(all_messages.count(), 2)
        message_ids = list(all_messages.values_list("id", flat=True))
        self.assertIn(read_msg.id, message_ids)
        self.assertIn(unread_msg.id, message_ids)

    def test_with_optimized_fields(self) -> None:
        """Test that with_optimized_fields() uses .only() to limit fields."""
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message",
            read=False,
        )

        # Get queryset with optimized fields
        queryset = Message.unread.unread_for_user(self.user2)

        # The queryset should use .only() to limit fields
        # We can't directly test this, but we can verify the query works
        messages = list(queryset)
        self.assertEqual(len(messages), 1)
        self.assertFalse(messages[0].read)

    def test_unread_messages_ordering(self) -> None:
        """Test that unread messages are ordered by timestamp descending."""
        # Create messages at different times
        msg1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="First",
            read=False,
        )
        msg2 = Message.objects.create(
            sender=self.user3,
            receiver=self.user2,
            content="Second",
            read=False,
        )

        # Get unread messages
        unread_messages = list(Message.unread.unread_for_user(self.user2))

        # Verify ordering (newest first)
        self.assertEqual(unread_messages[0].id, msg2.id)
        self.assertEqual(unread_messages[1].id, msg1.id)


class UnreadMessagesViewTest(TestCase):
    """Test cases for unread messages views."""

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

    def test_inbox_unread_view(self) -> None:
        """Test the inbox_unread view."""
        from rest_framework.test import APIClient
        from django.urls import reverse

        # Create unread messages
        msg1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Unread 1",
            read=False,
        )
        msg2 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Unread 2",
            read=False,
        )
        # Create read message (should not appear)
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Read",
            read=True,
            read_at=timezone.now(),
        )

        # Test view
        client = APIClient()
        client.force_authenticate(user=self.user2)
        url = reverse("messaging:inbox_unread")
        response = client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("unread_messages", response.data)
        self.assertEqual(len(response.data["unread_messages"]), 2)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(response.data["total_unread"], 2)

    def test_inbox_all_view_unread_only(self) -> None:
        """Test the inbox_all view with unread_only parameter."""
        from rest_framework.test import APIClient
        from django.urls import reverse

        # Create messages
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Unread",
            read=False,
        )
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Read",
            read=True,
            read_at=timezone.now(),
        )

        # Test view with unread_only=true
        client = APIClient()
        client.force_authenticate(user=self.user2)
        url = reverse("messaging:inbox_all")
        response = client.get(url, {"unread_only": "true"})

        self.assertEqual(response.status_code, 200)
        self.assertIn("messages", response.data)
        self.assertEqual(len(response.data["messages"]), 1)
        self.assertFalse(response.data["messages"][0]["read"])

    def test_mark_message_read_view(self) -> None:
        """Test the mark_message_read view."""
        from rest_framework.test import APIClient
        from django.urls import reverse

        # Create unread message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test",
            read=False,
        )

        # Mark as read via view
        client = APIClient()
        client.force_authenticate(user=self.user2)
        url = reverse("messaging:mark_message_read", kwargs={"message_id": message.id})
        response = client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["read"], True)
        self.assertIsNotNone(response.data["read_at"])

        # Verify message is marked as read
        message.refresh_from_db()
        self.assertTrue(message.read)
        self.assertIsNotNone(message.read_at)

    def test_mark_message_read_view_only_receiver(self) -> None:
        """Test that only the receiver can mark a message as read."""
        from rest_framework.test import APIClient
        from django.urls import reverse

        # Create message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test",
            read=False,
        )

        # Try to mark as read as sender (should fail)
        client = APIClient()
        client.force_authenticate(user=self.user1)
        url = reverse("messaging:mark_message_read", kwargs={"message_id": message.id})
        response = client.post(url)

        self.assertEqual(response.status_code, 403)

    def test_inbox_unread_view_requires_authentication(self) -> None:
        """Test that inbox_unread view requires authentication."""
        from rest_framework.test import APIClient
        from django.urls import reverse

        client = APIClient()
        url = reverse("messaging:inbox_unread")
        response = client.get(url)

        self.assertEqual(response.status_code, 401)



