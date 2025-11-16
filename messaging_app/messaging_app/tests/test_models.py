import pytest
from django.contrib.auth import get_user_model
from messaging_app.chats.models import Conversation, Message


User = get_user_model()


@pytest.mark.django_db
def test_message_sender_must_be_participant():
	u1 = User.objects.create_user(username="alice", email="alice@example.com", password="pass1234")
	u2 = User.objects.create_user(username="bob", email="bob@example.com", password="pass1234")
	conv = Conversation.objects.create()
	conv.participants.add(u1)  # only alice is a participant

	# Sending as bob should fail validation
	msg = Message(conversation=conv, sender=u2, message_body="Hi")
	with pytest.raises(Exception):
		msg.save()


