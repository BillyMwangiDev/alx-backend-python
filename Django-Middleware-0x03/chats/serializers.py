from typing import Any, Dict
from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ["user_id", "username", "first_name", "last_name", "email", "phone_number", "role", "created_at"]
		read_only_fields = ["user_id", "created_at"]


class MessageSerializer(serializers.ModelSerializer):
	message_body = serializers.CharField(allow_blank=False, allow_null=False, min_length=1)
	sender = UserSerializer(read_only=True)
	sender_id = serializers.PrimaryKeyRelatedField(
		source="sender", queryset=User.objects.all(), write_only=True
	)
	preview = serializers.SerializerMethodField()

	class Meta:
		model = Message
		fields = ["message_id", "conversation", "sender", "sender_id", "message_body", "sent_at", "preview"]
		read_only_fields = ["message_id", "sent_at", "sender", "preview"]

	def get_preview(self, obj: Message) -> str:
		text = obj.message_body or ""
		return text[:30]


class ConversationSerializer(serializers.ModelSerializer):
	participants = serializers.PrimaryKeyRelatedField(
		queryset=User.objects.all(), many=True
	)
	messages = MessageSerializer(many=True, read_only=True)
	participants_count = serializers.SerializerMethodField()

	class Meta:
		model = Conversation
		fields = ["conversation_id", "participants", "created_at", "messages", "participants_count"]
		read_only_fields = ["conversation_id", "created_at", "messages", "participants_count"]

	def create(self, validated_data: Dict[str, Any]) -> Conversation:
		participants = validated_data.pop("participants", [])
		if not participants:
			raise serializers.ValidationError({"participants": "At least one participant is required."})
		conversation = Conversation.objects.create(**validated_data)
		conversation.participants.set(participants)
		return conversation

	def get_participants_count(self, obj: Conversation) -> int:
		return obj.participants.count()


