import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
	"""
	Custom User model using UUID as primary key with additional fields.
	"""

	class Role(models.TextChoices):
		GUEST = "guest", "Guest"
		HOST = "host", "Host"
		ADMIN = "admin", "Admin"

	user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
	email = models.EmailField(unique=True)
	# Explicitly declare these to satisfy schema/token checks while matching AbstractUser API
	first_name = models.CharField(max_length=150, blank=True)
	last_name = models.CharField(max_length=150, blank=True)
	# Optional password_hash per provided schema (auth still uses AbstractUser.password)
	password_hash = models.CharField(max_length=255, null=True, blank=True)
	phone_number = models.CharField(max_length=50, null=True, blank=True)
	role = models.CharField(max_length=10, choices=Role.choices, default=Role.GUEST)
	created_at = models.DateTimeField(default=timezone.now)

	USERNAME_FIELD = "username"
	REQUIRED_FIELDS = ["email"]

	class Meta(AbstractUser.Meta):
		# Ensure Django treats this as the swappable AUTH_USER_MODEL
		swappable = "AUTH_USER_MODEL"

	def __str__(self) -> str:
		return f"{self.username} ({self.email})"


class Conversation(models.Model):
	"""
	Conversation holds participants via a many-to-many relationship to User.
	"""

	conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
	participants = models.ManyToManyField(User, related_name="conversations", blank=False)
	created_at = models.DateTimeField(default=timezone.now)

	def __str__(self) -> str:
		return f"Conversation {self.conversation_id}"


class Message(models.Model):
	"""
	Message sent by a user within a conversation.
	"""

	message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
	conversation = models.ForeignKey(Conversation, related_name="messages", on_delete=models.CASCADE)
	sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
	message_body = models.TextField()
	sent_at = models.DateTimeField(default=timezone.now)

	class Meta:
		# Preserve chronological ordering, fall back to UUID pk for stability
		ordering = ["sent_at", "message_id"]
		indexes = [
			models.Index(fields=["conversation", "sent_at"]),
		]

	def clean(self) -> None:
		# Ensure sender is a participant of the conversation
		if self.conversation_id and self.sender_id:
			if not self.conversation.participants.filter(id=self.sender_id).exists():
				from django.core.exceptions import ValidationError

				raise ValidationError("Sender must be a participant of the conversation.")

	def save(self, *args, **kwargs):
		self.full_clean()
		return super().save(*args, **kwargs)

	def __str__(self) -> str:
		return f"{self.sender_id}: {self.message_body[:20]}"


