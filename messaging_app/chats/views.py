from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
	queryset = Conversation.objects.all().prefetch_related("participants", "messages")
	serializer_class = ConversationSerializer
	permission_classes = [permissions.IsAuthenticated]

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
	permission_classes = [permissions.IsAuthenticated]

	def perform_create(self, serializer):
		serializer.save(sender=self.request.user)

	def get_queryset(self):
		qs = super().get_queryset()
		conversation_id = self.request.query_params.get("conversation")
		if conversation_id:
			qs = qs.filter(conversation_id=conversation_id)
		return qs


