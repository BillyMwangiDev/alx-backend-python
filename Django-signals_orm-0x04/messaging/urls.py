"""
URL configuration for the messaging app.

This module defines URL patterns for messaging-related views.
"""
from django.urls import path

from .views import (
    delete_user,
    get_thread,
    list_threads,
    create_reply,
    inbox_unread,
    inbox_all,
    mark_message_read,
)

app_name = "messaging"

urlpatterns = [
    path("users/delete/", delete_user, name="delete_user"),
    path("messages/<int:message_id>/thread/", get_thread, name="get_thread"),
    path("messages/threads/", list_threads, name="list_threads"),
    path("messages/<int:message_id>/reply/", create_reply, name="create_reply"),
    path("messages/inbox/unread/", inbox_unread, name="inbox_unread"),
    path("messages/inbox/", inbox_all, name="inbox_all"),
    path("messages/<int:message_id>/mark-read/", mark_message_read, name="mark_message_read"),
]

