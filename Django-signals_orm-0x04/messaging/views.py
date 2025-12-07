"""
Views for the messaging app.

This module contains view functions and classes for handling user deletion,
threaded conversations, and other messaging-related operations.
"""
import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Message

logger = logging.getLogger(__name__)

User = get_user_model()


@api_view(["DELETE", "POST"])
@permission_classes([IsAuthenticated])
def delete_user(request):
    """
    View function to delete the authenticated user's account.

    This view allows a user to delete their own account. It will trigger
    the post_delete signal which will clean up all related data including
    messages, notifications, and message history.

    Methods:
        DELETE: Delete the user account
        POST: Delete the user account (alternative method)

    Returns:
        Response: JSON response indicating success or failure

    Example:
        DELETE /api/users/delete/
        POST /api/users/delete/
    """
    if request.method not in ["DELETE", "POST"]:
        return Response(
            {"error": "Method not allowed"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    user = request.user

    if not user.is_authenticated:
        return Response(
            {"error": "Authentication required"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        # Log the deletion attempt
        logger.info(
            f"User {user.id} ({user.username}) requested account deletion"
        )

        # Get user ID before deletion for logging
        user_id = user.id
        username = user.username

        # Delete the user - this will trigger post_delete signal
        user.delete()

        logger.info(
            f"User {user_id} ({username}) account deleted successfully"
        )

        return Response(
            {
                "message": "Account deleted successfully",
                "detail": "Your account and all associated data have been permanently deleted.",
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(
            f"Failed to delete user {user.id}: {str(e)}",
            exc_info=True,
        )
        return Response(
            {
                "error": "Failed to delete account",
                "detail": "An error occurred while deleting your account. Please try again later.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class DeleteUserView(View):
    """
    Class-based view for deleting a user account.

    This view provides an alternative class-based implementation
    for user account deletion.
    """

    @method_decorator(login_required)
    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def delete(self, request):
        """
        Handle DELETE request to delete user account.

        Args:
            request: HTTP request object

        Returns:
            JsonResponse: JSON response with deletion status
        """
        user = request.user

        try:
            # Log the deletion attempt
            logger.info(
                f"User {user.id} ({user.username}) requested account deletion via class-based view"
            )

            # Get user info before deletion
            user_id = user.id
            username = user.username

            # Delete the user - this will trigger post_delete signal
            user.delete()

            logger.info(
                f"User {user_id} ({username}) account deleted successfully via class-based view"
            )

            return JsonResponse(
                {
                    "message": "Account deleted successfully",
                    "detail": "Your account and all associated data have been permanently deleted.",
                },
                status=200,
            )

        except Exception as e:
            logger.error(
                f"Failed to delete user {user.id}: {str(e)}",
                exc_info=True,
            )
            return JsonResponse(
                {
                    "error": "Failed to delete account",
                    "detail": "An error occurred while deleting your account. Please try again later.",
                },
                status=500,
            )

    def post(self, request):
        """
        Handle POST request to delete user account (alternative to DELETE).

        Args:
            request: HTTP request object

        Returns:
            JsonResponse: JSON response with deletion status
        """
        return self.delete(request)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@cache_page(60)
def get_thread(request, message_id):
    """
    Retrieve a threaded conversation starting from a root message.

    This view uses optimized queries with prefetch_related and select_related
    to efficiently fetch all messages in a thread, including nested replies.

    Args:
        request: HTTP request object
        message_id: ID of the root message to get thread for

    Returns:
        Response: JSON response with threaded conversation data

    Example:
        GET /api/messages/{message_id}/thread/
    """
    try:
        # Get the root message with optimized queries using filter and select_related
        root_message = get_object_or_404(
            Message.objects.filter(id=message_id)
            .select_related("sender", "receiver", "parent_message"),
            id=message_id,
        )

        # Get the actual root message (in case this is a reply)
        actual_root = root_message.get_root_message()

        # Get all messages in the thread using optimized query
        # Use Message.objects.filter for recursive querying with prefetch_related and select_related
        thread_messages = Message.objects.get_thread(actual_root.id)

        # Build threaded structure
        def build_thread_structure(messages):
            """Build a nested thread structure from flat message list."""
            message_dict = {}
            root_messages = []

            # First pass: create dict of all messages
            for msg in messages:
                message_dict[msg.id] = {
                    "id": msg.id,
                    "sender": {
                        "id": msg.sender.id,
                        "username": getattr(msg.sender, "username", str(msg.sender.id)),
                    },
                    "receiver": {
                        "id": msg.receiver.id,
                        "username": getattr(
                            msg.receiver, "username", str(msg.receiver.id)
                        ),
                    },
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "edited": msg.edited,
                    "edited_at": msg.edited_at.isoformat() if msg.edited_at else None,
                    "parent_message_id": msg.parent_message_id,
                    "replies": [],
                    "depth": msg.get_thread_depth(),
                }

            # Second pass: build tree structure
            for msg in messages:
                msg_data = message_dict[msg.id]
                if msg.parent_message_id:
                    parent_data = message_dict.get(msg.parent_message_id)
                    if parent_data:
                        parent_data["replies"].append(msg_data)
                else:
                    root_messages.append(msg_data)

            return root_messages

        thread_structure = build_thread_structure(thread_messages)

        return Response(
            {
                "root_message_id": actual_root.id,
                "thread": thread_structure,
                "total_messages": len(thread_messages),
            },
            status=status.HTTP_200_OK,
        )

    except Message.DoesNotExist:
        return Response(
            {"error": "Message not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        logger.error(
            f"Error retrieving thread for message {message_id}: {str(e)}",
            exc_info=True,
        )
        return Response(
            {"error": "Failed to retrieve thread"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_threads(request):
    """
    List all top-level messages (thread roots) with optimized queries.

    This view returns only top-level messages (messages without a parent)
    with their direct replies prefetched for efficiency.

    Query Parameters:
        - receiver: Filter by receiver ID
        - sender: Filter by sender ID
        - limit: Maximum number of threads to return (default: 50)

    Returns:
        Response: JSON response with list of thread roots

    Example:
        GET /api/messages/threads/?receiver=1&limit=20
    """
    try:
        # Get query parameters
        receiver_id = request.query_params.get("receiver")
        sender_id = request.query_params.get("sender")
        limit = int(request.query_params.get("limit", 50))

        # Start with optimized queryset for top-level messages only
        # Use Message.objects.filter to query messages without a parent (thread roots)
        queryset = (
            Message.objects.filter(parent_message__isnull=True)
            .select_related("sender", "receiver")
            .prefetch_related("replies")
            .order_by("-timestamp")
        )

        # Apply filters using Message.objects.filter for optimized queries
        if receiver_id:
            queryset = Message.objects.filter(
                parent_message__isnull=True, receiver_id=receiver_id
            ).select_related("sender", "receiver").prefetch_related("replies").order_by("-timestamp")

        if sender_id:
            queryset = Message.objects.filter(
                parent_message__isnull=True, sender_id=sender_id
            ).select_related("sender", "receiver").prefetch_related("replies").order_by("-timestamp")

        if receiver_id and sender_id:
            queryset = Message.objects.filter(
                parent_message__isnull=True,
                receiver_id=receiver_id,
                sender_id=sender_id
            ).select_related("sender", "receiver").prefetch_related("replies").order_by("-timestamp")

        # Limit results
        threads = queryset[:limit]

        # Build response data
        threads_data = []
        for thread in threads:
            threads_data.append(
                {
                    "id": thread.id,
                    "sender": {
                        "id": thread.sender.id,
                        "username": getattr(thread.sender, "username", str(thread.sender.id)),
                    },
                    "receiver": {
                        "id": thread.receiver.id,
                        "username": getattr(
                            thread.receiver, "username", str(thread.receiver.id)
                        ),
                    },
                    "content": thread.content,
                    "timestamp": thread.timestamp.isoformat(),
                    "edited": thread.edited,
                    "edited_at": thread.edited_at.isoformat() if thread.edited_at else None,
                    "reply_count": thread.get_reply_count(),
                }
            )

        return Response(
            {
                "threads": threads_data,
                "count": len(threads_data),
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"Error listing threads: {str(e)}", exc_info=True)
        return Response(
            {"error": "Failed to retrieve threads"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_reply(request, message_id):
    """
    Create a reply to a specific message.

    This view allows users to reply to existing messages, creating
    a threaded conversation structure.

    Request Body:
        {
            "content": "Reply message content",
            "receiver_id": <receiver_id>  # Optional, defaults to original sender
        }

    Returns:
        Response: JSON response with created reply message

    Example:
        POST /api/messages/{message_id}/reply/
    """
    try:
        # Get the parent message
        parent_message = get_object_or_404(Message.objects.with_related(), id=message_id)

        # Get request data
        content = request.data.get("content")
        receiver_id = request.data.get("receiver_id")

        if not content:
            return Response(
                {"error": "Content is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Determine receiver (default to original sender if not specified)
        if receiver_id:
            receiver = get_object_or_404(User, id=receiver_id)
        else:
            receiver = parent_message.sender

        # Create reply message
        reply = Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content,
            parent_message=parent_message,
        )

        # Return reply with optimized queries
        reply = Message.objects.with_related().get(id=reply.id)

        return Response(
            {
                "id": reply.id,
                "sender": {
                    "id": reply.sender.id,
                    "username": getattr(reply.sender, "username", str(reply.sender.id)),
                },
                "receiver": {
                    "id": reply.receiver.id,
                    "username": getattr(
                        reply.receiver, "username", str(reply.receiver.id)
                    ),
                },
                "content": reply.content,
                "timestamp": reply.timestamp.isoformat(),
                "parent_message_id": reply.parent_message_id,
                "thread_depth": reply.get_thread_depth(),
            },
            status=status.HTTP_201_CREATED,
        )

    except Message.DoesNotExist:
        return Response(
            {"error": "Parent message not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        logger.error(
            f"Error creating reply to message {message_id}: {str(e)}",
            exc_info=True,
        )
        return Response(
            {"error": "Failed to create reply"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def inbox_unread(request):
    """
    Retrieve all unread messages for the authenticated user's inbox.

    This view uses the UnreadMessagesManager to efficiently filter and
    retrieve only unread messages with optimized queries using .only()
    to select only necessary fields.

    Query Parameters:
        - limit: Maximum number of messages to return (default: 50)

    Returns:
        Response: JSON response with list of unread messages

    Example:
        GET /api/messages/inbox/unread/?limit=20
    """
    try:
        user = request.user
        limit = int(request.query_params.get("limit", 50))

        # Use custom manager to get unread messages with optimized queries
        unread_messages = Message.unread.unread_for_user(user)[:limit]

        # Build response data
        messages_data = []
        for message in unread_messages:
            messages_data.append(
                {
                    "id": message.id,
                    "sender": {
                        "id": message.sender.id,
                        "username": getattr(
                            message.sender, "username", str(message.sender.id)
                        ),
                    },
                    "content": message.content,
                    "timestamp": message.timestamp.isoformat(),
                    "read": message.read,
                    "read_at": message.read_at.isoformat() if message.read_at else None,
                    "parent_message_id": message.parent_message_id,
                    "is_reply": message.is_reply(),
                }
            )

        return Response(
            {
                "unread_messages": messages_data,
                "count": len(messages_data),
                "total_unread": Message.unread.unread_for_user(user).count(),
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"Error retrieving unread messages for user {request.user.id}: {str(e)}", exc_info=True)
        return Response(
            {"error": "Failed to retrieve unread messages"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def inbox_all(request):
    """
    Retrieve all messages (read and unread) for the authenticated user's inbox.

    This view uses the UnreadMessagesManager with optimized queries.

    Query Parameters:
        - unread_only: If true, return only unread messages (default: false)
        - limit: Maximum number of messages to return (default: 50)

    Returns:
        Response: JSON response with list of messages

    Example:
        GET /api/messages/inbox/?unread_only=true&limit=20
    """
    try:
        user = request.user
        unread_only = request.query_params.get("unread_only", "false").lower() == "true"
        limit = int(request.query_params.get("limit", 50))

        # Use custom manager based on filter
        if unread_only:
            messages = Message.unread.unread_for_user(user)[:limit]
        else:
            messages = Message.unread.all_for_user(user)[:limit]

        # Build response data
        messages_data = []
        for message in messages:
            messages_data.append(
                {
                    "id": message.id,
                    "sender": {
                        "id": message.sender.id,
                        "username": getattr(
                            message.sender, "username", str(message.sender.id)
                        ),
                    },
                    "content": message.content,
                    "timestamp": message.timestamp.isoformat(),
                    "read": message.read,
                    "read_at": message.read_at.isoformat() if message.read_at else None,
                    "parent_message_id": message.parent_message_id,
                    "is_reply": message.is_reply(),
                }
            )

        return Response(
            {
                "messages": messages_data,
                "count": len(messages_data),
                "unread_only": unread_only,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"Error retrieving inbox for user {request.user.id}: {str(e)}", exc_info=True)
        return Response(
            {"error": "Failed to retrieve inbox"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST", "PATCH"])
@permission_classes([IsAuthenticated])
def mark_message_read(request, message_id):
    """
    Mark a message as read.

    This view allows users to mark messages they received as read.

    Methods:
        POST: Mark message as read
        PATCH: Mark message as read (alternative method)

    Returns:
        Response: JSON response indicating success

    Example:
        POST /api/messages/{message_id}/mark-read/
        PATCH /api/messages/{message_id}/mark-read/
    """
    try:
        user = request.user
        message = get_object_or_404(
            Message.objects.select_related("receiver"), id=message_id
        )

        # Verify user is the receiver
        if message.receiver_id != user.id:
            return Response(
                {"error": "You can only mark your own received messages as read"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Mark as read
        message.mark_as_read()

        return Response(
            {
                "message": "Message marked as read",
                "id": message.id,
                "read": message.read,
                "read_at": message.read_at.isoformat() if message.read_at else None,
            },
            status=status.HTTP_200_OK,
        )

    except Message.DoesNotExist:
        return Response(
            {"error": "Message not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        logger.error(
            f"Error marking message {message_id} as read: {str(e)}",
            exc_info=True,
        )
        return Response(
            {"error": "Failed to mark message as read"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

