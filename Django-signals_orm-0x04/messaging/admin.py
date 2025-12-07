"""
Admin configuration for the messaging app models.

This module registers Message, Notification, and MessageHistory models
in the Django admin interface with appropriate list displays, filters,
and search capabilities, including edit history display.
"""
from django.contrib import admin

from .models import Message, MessageHistory, Notification


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin interface for Message model."""

    list_display = (
        "id",
        "sender",
        "receiver",
        "content_preview",
        "edited",
        "timestamp",
        "edited_at",
    )
    list_filter = (
        "timestamp",
        "edited",
        "edited_at",
        "sender",
        "receiver",
    )
    search_fields = (
        "content",
        "sender__username",
        "sender__email",
        "receiver__username",
        "receiver__email",
    )
    readonly_fields = ("timestamp", "edited", "edited_at", "edit_history_display")
    date_hierarchy = "timestamp"
    ordering = ("-timestamp",)

    fieldsets = (
        (
            "Message Information",
            {
                "fields": ("sender", "receiver", "content", "timestamp"),
            },
        ),
        (
            "Edit Information",
            {
                "fields": ("edited", "edited_at", "edit_history_display"),
                "classes": ("collapse",),
            },
        ),
    )

    def edit_history_display(self, obj: Message) -> str:
        """Display edit history links for the message."""
        if not obj.pk:
            return "N/A"

        history_count = obj.history.count()
        if history_count == 0:
            return "No edit history"

        return f"{history_count} edit(s) - View in Message History section"

    edit_history_display.short_description = "Edit History"

    def content_preview(self, obj: Message) -> str:
        """Return a preview of the message content."""
        if len(obj.content) > 50:
            return f"{obj.content[:50]}..."
        return obj.content

    content_preview.short_description = "Content Preview"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model."""

    list_display = (
        "id",
        "user",
        "message_preview",
        "is_read",
        "created_at",
    )
    list_filter = (
        "is_read",
        "created_at",
        "user",
    )
    search_fields = (
        "user__username",
        "user__email",
        "message__content",
    )
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_editable = ("is_read",)

    fieldsets = (
        (
            "Notification Information",
            {
                "fields": ("user", "message", "is_read", "created_at"),
            },
        ),
    )

    def message_preview(self, obj: Notification) -> str:
        """Return a preview of the related message content."""
        if obj.message and len(obj.message.content) > 50:
            return f"{obj.message.content[:50]}..."
        return obj.message.content if obj.message else "N/A"

    message_preview.short_description = "Message Preview"


@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    """Admin interface for MessageHistory model."""

    list_display = (
        "id",
        "message_link",
        "old_content_preview",
        "edited_by",
        "edited_at",
    )
    list_filter = (
        "edited_at",
        "edited_by",
    )
    search_fields = (
        "message__id",
        "old_content",
        "message__content",
        "edited_by__username",
        "edited_by__email",
    )
    readonly_fields = ("edited_at", "message", "old_content", "edited_by")
    date_hierarchy = "edited_at"
    ordering = ("-edited_at",)

    fieldsets = (
        (
            "History Information",
            {
                "fields": ("message", "old_content", "edited_by", "edited_at"),
            },
        ),
    )

    def message_link(self, obj: MessageHistory) -> str:
        """Return a link to the related message."""
        if obj.message:
            return f"Message #{obj.message.id} (from {obj.message.sender} to {obj.message.receiver})"
        return "N/A"

    message_link.short_description = "Message"

    def old_content_preview(self, obj: MessageHistory) -> str:
        """Return a preview of the old content."""
        if len(obj.old_content) > 50:
            return f"{obj.old_content[:50]}..."
        return obj.old_content

    old_content_preview.short_description = "Old Content Preview"

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related("message", "message__sender", "message__receiver", "edited_by")

