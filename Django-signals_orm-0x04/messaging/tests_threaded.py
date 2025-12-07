"""
Tests for threaded conversations functionality.

This module contains tests for the threaded conversation features including
replies, thread queries, and optimized database access.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Message

User = get_user_model()


class ThreadedConversationTest(TestCase):
    """Test cases for threaded conversations functionality."""

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

    def test_create_reply_message(self) -> None:
        """Test creating a reply to a message."""
        # Create parent message
        parent = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original message",
        )

        # Create reply
        reply = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Reply message",
            parent_message=parent,
        )

        # Verify reply properties
        self.assertEqual(reply.parent_message, parent)
        self.assertTrue(reply.is_reply())
        self.assertEqual(reply.get_thread_depth(), 1)

    def test_get_root_message(self) -> None:
        """Test getting the root message of a thread."""
        # Create message chain: parent -> reply -> nested_reply
        parent = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Parent",
        )
        reply = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Reply",
            parent_message=parent,
        )
        nested_reply = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Nested reply",
            parent_message=reply,
        )

        # Verify root message
        self.assertEqual(nested_reply.get_root_message(), parent)
        self.assertEqual(reply.get_root_message(), parent)
        self.assertEqual(parent.get_root_message(), parent)

    def test_thread_depth_calculation(self) -> None:
        """Test thread depth calculation."""
        parent = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Level 0",
        )
        reply1 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Level 1",
            parent_message=parent,
        )
        reply2 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Level 2",
            parent_message=reply1,
        )

        self.assertEqual(parent.get_thread_depth(), 0)
        self.assertEqual(reply1.get_thread_depth(), 1)
        self.assertEqual(reply2.get_thread_depth(), 2)

    def test_get_all_replies(self) -> None:
        """Test getting all replies to a message."""
        parent = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Parent",
        )

        # Create multiple replies
        reply1 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Reply 1",
            parent_message=parent,
        )
        reply2 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Reply 2",
            parent_message=parent,
        )
        nested_reply = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Nested reply",
            parent_message=reply1,
        )

        # Get all replies
        all_replies = parent.get_all_replies()

        # Verify all replies are included
        reply_ids = [r.id for r in all_replies]
        self.assertIn(reply1.id, reply_ids)
        self.assertIn(reply2.id, reply_ids)
        self.assertIn(nested_reply.id, reply_ids)

    def test_get_reply_count(self) -> None:
        """Test getting total reply count including nested replies."""
        parent = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Parent",
        )

        # Create replies
        reply1 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Reply 1",
            parent_message=parent,
        )
        reply2 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Reply 2",
            parent_message=parent,
        )
        nested_reply = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Nested reply",
            parent_message=reply1,
        )

        # Verify reply count
        self.assertEqual(parent.get_reply_count(), 3)  # 2 direct + 1 nested

    def test_top_level_only_queryset(self) -> None:
        """Test filtering for top-level messages only."""
        # Create top-level messages
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

        # Create reply (not top-level)
        reply = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Reply",
            parent_message=msg1,
        )

        # Get top-level messages only
        top_level = Message.objects.top_level_only()

        # Verify only top-level messages are returned
        self.assertEqual(top_level.count(), 2)
        self.assertIn(msg1, top_level)
        self.assertIn(msg2, top_level)
        self.assertNotIn(reply, top_level)

    def test_get_thread_queryset(self) -> None:
        """Test getting all messages in a thread."""
        root = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Root",
        )
        reply1 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Reply 1",
            parent_message=root,
        )
        reply2 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Reply 2",
            parent_message=root,
        )
        nested = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Nested",
            parent_message=reply1,
        )

        # Get thread
        thread_messages = Message.objects.get_thread(root.id)

        # Verify all messages in thread are included
        thread_ids = list(thread_messages.values_list("id", flat=True))
        self.assertIn(root.id, thread_ids)
        self.assertIn(reply1.id, thread_ids)
        self.assertIn(reply2.id, thread_ids)
        self.assertIn(nested.id, thread_ids)
        self.assertEqual(len(thread_ids), 4)

    def test_cascade_deletion_of_replies(self) -> None:
        """Test that deleting a parent message cascades to replies."""
        parent = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Parent",
        )
        reply = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Reply",
            parent_message=parent,
        )

        # Delete parent
        parent.delete()

        # Verify reply is also deleted (CASCADE)
        self.assertFalse(Message.objects.filter(id=reply.id).exists())

    def test_nested_thread_structure(self) -> None:
        """Test deeply nested thread structure."""
        # Create 3-level deep thread
        level0 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Level 0",
        )
        level1 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Level 1",
            parent_message=level0,
        )
        level2 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Level 2",
            parent_message=level1,
        )

        # Verify structure
        self.assertEqual(level2.get_root_message(), level0)
        self.assertEqual(level2.get_thread_depth(), 2)
        self.assertEqual(level0.get_reply_count(), 2)



