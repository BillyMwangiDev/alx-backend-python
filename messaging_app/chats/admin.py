from django.contrib import admin
from .models import User, Conversation, Message


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = ("id", "username", "email", "role", "created_at")
	search_fields = ("username", "email")
	list_filter = ("role",)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
	list_display = ("id", "created_at")
	search_fields = ("id",)
	filter_horizontal = ("participants",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
	list_display = ("id", "conversation", "sender", "sent_at")
	search_fields = ("message_body",)
	list_filter = ("sent_at",)


