import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


User = get_user_model()


@pytest.mark.django_db
def test_create_conversation_and_send_message():
	client = APIClient()
	# create users
	u1 = User.objects.create_user(username="alice", email="alice@example.com", password="pass1234")
	u2 = User.objects.create_user(username="bob", email="bob@example.com", password="pass1234")
	assert u1.id and u2.id

	# authenticate as alice
	assert client.login(username="alice", password="pass1234")

	# create conversation with both participants
	resp = client.post(reverse("conversation-list"), {"participants": [str(u1.id), str(u2.id)]}, format="json")
	assert resp.status_code == 201, resp.content
	conversation_id = resp.data["id"]

	# send a message
	send_url = reverse("conversation-send", kwargs={"pk": conversation_id})
	resp2 = client.post(send_url, {"message_body": "Hello Bob"}, format="json")
	assert resp2.status_code == 201, resp2.content
	assert resp2.data["message_body"] == "Hello Bob"

	# list messages by conversation filter
	resp3 = client.get(reverse("message-list"), {"conversation": conversation_id})
	assert resp3.status_code == 200
	assert len(resp3.data) == 1
	assert resp3.data[0]["message_body"] == "Hello Bob"


