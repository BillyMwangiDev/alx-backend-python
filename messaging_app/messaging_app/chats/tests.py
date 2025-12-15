from django.test import TestCase
from django.contrib.auth import get_user_model
from messaging_app.chats.models import Conversation, Message


class ChatsSmokeTests(TestCase):
	def test_create_conversation_and_message(self):
		User = get_user_model()
		u1 = User.objects.create_user(username="alice", email="alice@example.com", password="pass1234")
		u2 = User.objects.create_user(username="bob", email="bob@example.com", password="pass1234")

		conv = Conversation.objects.create()
		conv.participants.add(u1, u2)

		msg = Message.objects.create(conversation=conv, sender=u1, message_body="hello")
		self.assertEqual(msg.message_body, "hello")
		self.assertEqual(msg.conversation, conv)
		self.assertTrue(conv.messages.exists())


