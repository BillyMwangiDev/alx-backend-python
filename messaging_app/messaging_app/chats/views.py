from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend

from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation, IsConversationParticipant, IsMessageOwnerOrParticipant, CanAccessOwnData
from .pagination import MessagePagination
from .filters import MessageFilter


class ConversationViewSet(viewsets.ModelViewSet):
	queryset = Conversation.objects.all().prefetch_related("participants", "messages")
	serializer_class = ConversationSerializer
	permission_classes = [permissions.IsAuthenticated, CanAccessOwnData]

	def get_queryset(self):
		"""
		Filter conversations to only show those where the user is a participant.
		"""
		if not self.request.user or not self.request.user.is_authenticated:
			return Conversation.objects.none()
		return Conversation.objects.filter(participants=self.request.user).prefetch_related("participants", "messages")

	def perform_create(self, serializer):
		conversation = serializer.save()
		if self.request.user.is_authenticated and self.request.user not in conversation.participants.all():
			conversation.participants.add(self.request.user)

	@action(detail=True, methods=["post"], url_path="send")
	def send_message(self, request, pk=None):
		conversation = self.get_object()
		serializer = MessageSerializer(data={
			"conversation": str(conversation.pk),
			"sender_id": str(request.user.pk),
			"message_body": request.data.get("message_body", ""),
		})
		serializer.is_valid(raise_exception=True)
		message = serializer.save()
		read_serializer = MessageSerializer(message)
		return Response(read_serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
	queryset = Message.objects.select_related("conversation", "sender").all()
	serializer_class = MessageSerializer
	permission_classes = [IsParticipantOfConversation]
	pagination_class = MessagePagination
	filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
	filterset_class = MessageFilter
	ordering_fields = ["sent_at"]
	search_fields = ["message_body"]

	def perform_create(self, serializer):
		"""
		Create a message and ensure the user is a participant of the conversation.
		"""
		conversation = serializer.validated_data.get("conversation")
		if conversation and not conversation.participants.filter(user_id=self.request.user.user_id).exists():
			from rest_framework.exceptions import PermissionDenied
			raise PermissionDenied(
				"You must be a participant of the conversation to send messages."
			)
		serializer.save(sender=self.request.user)

	def update(self, request, *args, **kwargs):
		"""
		Update a message. Only participants can update messages.
		Returns HTTP_403_FORBIDDEN if user is not a participant.
		"""
		message = self.get_object()
		if not message.conversation.participants.filter(user_id=request.user.user_id).exists():
			return Response(
				{"detail": "You do not have permission to perform this action."},
				status=status.HTTP_403_FORBIDDEN
			)
		return super().update(request, *args, **kwargs)

	def partial_update(self, request, *args, **kwargs):
		"""
		Partially update a message. Only participants can update messages.
		Returns HTTP_403_FORBIDDEN if user is not a participant.
		"""
		message = self.get_object()
		if not message.conversation.participants.filter(user_id=request.user.user_id).exists():
			return Response(
				{"detail": "You do not have permission to perform this action."},
				status=status.HTTP_403_FORBIDDEN
			)
		return super().partial_update(request, *args, **kwargs)

	def destroy(self, request, *args, **kwargs):
		"""
		Delete a message. Only participants can delete messages.
		Returns HTTP_403_FORBIDDEN if user is not a participant.
		"""
		message = self.get_object()
		if not message.conversation.participants.filter(user_id=request.user.user_id).exists():
			return Response(
				{"detail": "You do not have permission to perform this action."},
				status=status.HTTP_403_FORBIDDEN
			)
		return super().destroy(request, *args, **kwargs)

	@method_decorator(cache_page(60))
	def list(self, request, *args, **kwargs):
		"""
		List messages in a conversation with 60-second cache timeout.

		This method is cached to improve performance when retrieving
		lists of messages. The cache expires after 60 seconds.
		"""
		return super().list(request, *args, **kwargs)

	def get_queryset(self):
		"""
		Filter messages to only show those from conversations where the user is a participant.
		"""
		if not self.request.user or not self.request.user.is_authenticated:
			return Message.objects.none()

		qs = Message.objects.filter(
			conversation__participants=self.request.user
		).select_related("conversation", "sender")

		conversation_id = self.request.query_params.get("conversation")
		if conversation_id:
			qs = qs.filter(conversation_id=conversation_id)
		return qs


