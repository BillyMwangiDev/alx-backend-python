"""
Filter classes for the messaging app.

This module provides filtering capabilities for messages and conversations.
"""
from django_filters import rest_framework as filters
from .models import Message, Conversation, User


class MessageFilter(filters.FilterSet):
	"""
	Filter class for messages.
	Allows filtering by:
	- Conversations with specific users (participants)
	- Messages within a time range (sent_at)
	"""
	# Filter by conversation participants (users)
	participants = filters.ModelMultipleChoiceFilter(
		field_name="conversation__participants",
		queryset=User.objects.all(),
		label="Filter by conversation participants (user IDs)",
		help_text="Filter messages from conversations that include these users",
	)

	# Filter by time range
	sent_at_after = filters.DateTimeFilter(
		field_name="sent_at",
		lookup_expr="gte",
		label="Messages sent after this date/time",
		help_text="Filter messages sent after this datetime (ISO 8601 format)",
	)
	sent_at_before = filters.DateTimeFilter(
		field_name="sent_at",
		lookup_expr="lte",
		label="Messages sent before this date/time",
		help_text="Filter messages sent before this datetime (ISO 8601 format)",
	)

	# Filter by conversation
	conversation = filters.UUIDFilter(
		field_name="conversation__conversation_id",
		label="Filter by conversation ID",
		help_text="Filter messages by conversation UUID",
	)

	# Filter by sender
	sender = filters.UUIDFilter(
		field_name="sender__user_id",
		label="Filter by sender user ID",
		help_text="Filter messages by sender UUID",
	)

	class Meta:
		model = Message
		fields = ["conversation", "sender", "participants", "sent_at_after", "sent_at_before"]

