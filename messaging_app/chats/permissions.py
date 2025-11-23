"""
Custom permissions for the messaging app.

This module ensures users can only access their own messages and conversations.
"""
from rest_framework import permissions
from .models import Conversation, Message


class IsParticipantOfConversation(permissions.BasePermission):
	"""
	Permission class that:
	- Allows only authenticated users to access the API
	- Allows only participants in a conversation to send, view, update and delete messages
	"""

	def has_permission(self, request, view):
		"""
		Check if the user is authenticated.
		This controls access to the API endpoints.

		Args:
			request: The request object
			view: The view instance

		Returns:
			True if user is authenticated, False otherwise
		"""
		return request.user and request.user.is_authenticated

	def has_object_permission(self, request, view, obj):
		"""
		Check if the user is a participant of the conversation for message operations.
		This controls access to view, update, and delete messages.
		Specifically checks PUT, PATCH, DELETE methods to ensure only participants can modify.

		Args:
			request: The request object
			view: The view instance
			obj: The message object

		Returns:
			True if user is a participant of the conversation, False otherwise
		"""
		if not request.user or not request.user.is_authenticated:
			return False

		# Check for PUT, PATCH, DELETE methods - only participants can update/delete
		if request.method in ["PUT", "PATCH", "DELETE"]:
			# For Message objects, check if user is a participant of the conversation
			if isinstance(obj, Message):
				return obj.conversation.participants.filter(user_id=request.user.user_id).exists()
			# For Conversation objects, check if user is a participant
			if isinstance(obj, Conversation):
				return obj.participants.filter(user_id=request.user.user_id).exists()
			return False

		# For GET and other methods, check if user is a participant
		if isinstance(obj, Message):
			return obj.conversation.participants.filter(user_id=request.user.user_id).exists()

		if isinstance(obj, Conversation):
			return obj.participants.filter(user_id=request.user.user_id).exists()

		return False


class IsConversationParticipant(permissions.BasePermission):
	"""
	Permission to check if the user is a participant of the conversation.
	"""

	def has_object_permission(self, request, view, obj):
		"""
		Check if the requesting user is a participant of the conversation.

		Args:
			request: The request object
			view: The view instance
			obj: The conversation object

		Returns:
			True if user is a participant, False otherwise
		"""
		if not request.user or not request.user.is_authenticated:
			return False

		# Check if user is a participant
		return obj.participants.filter(user_id=request.user.user_id).exists()


class IsMessageOwnerOrParticipant(permissions.BasePermission):
	"""
	Permission to check if the user is the sender of the message
	or a participant of the conversation.
	"""

	def has_object_permission(self, request, view, obj):
		"""
		Check if the requesting user is the sender or a conversation participant.

		Args:
			request: The request object
			view: The view instance
			obj: The message object

		Returns:
			True if user is sender or participant, False otherwise
		"""
		if not request.user or not request.user.is_authenticated:
			return False

		# User is the sender
		if obj.sender.user_id == request.user.user_id:
			return True

		# User is a participant of the conversation
		return obj.conversation.participants.filter(user_id=request.user.user_id).exists()


class CanAccessOwnData(permissions.BasePermission):
	"""
	Permission to ensure users can only access their own conversations and messages.
	"""

	def has_permission(self, request, view):
		"""
		Check if the user is authenticated.

		Args:
			request: The request object
			view: The view instance

		Returns:
			True if user is authenticated, False otherwise
		"""
		return request.user and request.user.is_authenticated

	def has_object_permission(self, request, view, obj):
		"""
		Check if the user can access the object.

		For conversations: user must be a participant
		For messages: user must be sender or conversation participant

		Args:
			request: The request object
			view: The view instance
			obj: The object being accessed

		Returns:
			True if user can access, False otherwise
		"""
		if not request.user or not request.user.is_authenticated:
			return False

		# Handle Conversation objects
		if hasattr(obj, "participants"):
			return obj.participants.filter(user_id=request.user.user_id).exists()

		# Handle Message objects
		if hasattr(obj, "sender") and hasattr(obj, "conversation"):
			# User is the sender
			if obj.sender.user_id == request.user.user_id:
				return True
			# User is a participant of the conversation
			return obj.conversation.participants.filter(user_id=request.user.user_id).exists()

		return False

