from typing import Any
from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ["id", "username", "first_name", "last_name", "email", "phone_number", "role", "created_at"]
		read_only_fields = ["id", "created_at"]


class MessageSerializer(serializers.ModelSerializer):
	sender = UserSerializer(read_only=True)
	sender_id = serializers.PrimaryKeyRelatedField(
		source="sender", queryset=User.objects.all(), write_only=True
	)

	class Meta:
		model = Message
		fields = ["id", "conversation", "sender", "sender_id", "message_body", "sent_at"]
		read_only_fields = ["id", "sent_at", "sender"]


class ConversationSerializer(serializers.ModelSerializer):
	participants = serializers.PrimaryKeyRelatedField(
		queryset=User.objects.all(), many=True
	)
	messages = MessageSerializer(many=True, read_only=True)

	class Meta:
		model = Conversation
		fields = ["id", "participants", "created_at", "messages"]
		read_only_fields = ["id", "created_at", "messages"]

	def create(self, validated_data: dict[str, Any]) -> Conversation:
		participants = validated_data.pop("participants", [])
		conversation = Conversation.objects.create(**validated_data)
		conversation.participants.set(participants)
		return conversation


