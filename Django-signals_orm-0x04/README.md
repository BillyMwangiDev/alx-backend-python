# Django Signals - Automatic Message Notifications

This project demonstrates how to use Django signals to automatically create notifications when users receive new messages.

## Overview

The messaging app automatically creates notifications for users when they receive a new message. This is accomplished using Django's `post_save` signal, which triggers whenever a `Message` instance is saved.

## Project Structure

```
Django-signals_orm-0x04/
└── messaging/
    ├── __init__.py
    ├── models.py          # Message, Notification, and MessageHistory models
    ├── signals.py         # Signal handlers for automatic notifications and cleanup
    ├── views.py           # Views for user deletion
    ├── urls.py            # URL configuration
    ├── apps.py            # App configuration with signal registration
    ├── admin.py           # Django admin configuration
    ├── tests.py           # Unit and integration tests
    └── migrations/
        └── __init__.py
```

## Models

### Message Model

The `Message` model represents a message sent from one user to another:

- **sender**: ForeignKey to User - the user who sent the message
- **receiver**: ForeignKey to User - the user who receives the message
- **content**: TextField - the message content
- **timestamp**: DateTimeField - when the message was created (auto-set)
- **edited**: BooleanField - whether the message has been edited (default: False)
- **edited_at**: DateTimeField - when the message was last edited (nullable)

### Notification Model

The `Notification` model stores notifications for users:

- **user**: ForeignKey to User - the user who receives the notification
- **message**: ForeignKey to Message - the message that triggered the notification
- **is_read**: BooleanField - whether the notification has been read (default: False)
- **created_at**: DateTimeField - when the notification was created (auto-set)

### MessageHistory Model

The `MessageHistory` model stores historical versions of edited messages:

- **message**: ForeignKey to Message - the message that was edited
- **old_content**: TextField - the previous content of the message before editing
- **edited_at**: DateTimeField - when this edit was made (auto-set)
- **edited_by**: ForeignKey to User - the user who made the edit (nullable)

## Signals

### pre_save Signal Handler

The `capture_message_history` function is a signal handler that:

1. Listens for `pre_save` signals from the `Message` model
2. Captures the old content of a message before it's updated
3. Stores the old content as an instance attribute for use in `post_save`
4. Only triggers for existing messages (has a primary key)

### post_save Signal Handler

The `create_notification_on_message` function is a signal handler that:

1. Listens for `post_save` signals from the `Message` model
2. Automatically creates a `Notification` for the receiving user when a new message is created
3. Only triggers for newly created messages (not updates)
4. Uses `get_or_create` to prevent duplicate notifications
5. When a message is updated, creates a `MessageHistory` entry with the old content
6. Sets the `edited` flag and `edited_at` timestamp when content changes

### post_delete Signal Handler

The `cleanup_user_data` function is a signal handler that:

1. Listens for `post_delete` signals from the `User` model
2. Logs the deletion of the user and related data
3. Ensures proper cleanup of all related data (messages, notifications, message history)

**Note**: Due to CASCADE relationships defined in the models:
- Messages sent by or received by a deleted user are automatically deleted
- Notifications for a deleted user are automatically deleted
- MessageHistory entries where `edited_by` points to the deleted user will have `edited_by` set to NULL (SET_NULL)

The signals are automatically registered when the app is loaded via the `ready()` method in `apps.py`.

## Usage

### Setting Up in Your Django Project

1. Add the `messaging` app to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # ... other apps
    'messaging.apps.MessagingConfig',  # Use the app config to ensure signals are loaded
]
```

2. Make sure your `AUTH_USER_MODEL` is properly configured in `settings.py`:

```python
AUTH_USER_MODEL = 'your_app.User'  # Replace with your user model
```

3. Run migrations:

```bash
python manage.py makemigrations messaging
python manage.py migrate
```

### Creating Messages

When you create a new `Message`, a notification is automatically created:

```python
from messaging.models import Message
from django.contrib.auth import get_user_model

User = get_user_model()

sender = User.objects.get(username='alice')
receiver = User.objects.get(username='bob')

# Create a message - notification is automatically created!
message = Message.objects.create(
    sender=sender,
    receiver=receiver,
    content="Hello, Bob!"
)

# The notification is automatically created
from messaging.models import Notification
notification = Notification.objects.get(user=receiver, message=message)
print(notification.is_read)  # False
```

### Accessing Notifications

```python
from messaging.models import Notification

# Get all unread notifications for a user
unread_notifications = Notification.objects.filter(
    user=receiver,
    is_read=False
)

# Mark a notification as read
notification.is_read = True
notification.save()
```

### Editing Messages and Viewing History

When you edit a message, the old content is automatically saved to `MessageHistory`:

```python
from messaging.models import Message, MessageHistory

# Get a message
message = Message.objects.get(id=1)

# Edit the message - history is automatically created!
message.content = "Updated content"
message.save()

# Check if message was edited
print(message.edited)  # True
print(message.edited_at)  # datetime object

# View edit history
history_entries = message.history.all()
for entry in history_entries:
    print(f"Previous content: {entry.old_content}")
    print(f"Edited at: {entry.edited_at}")
    print(f"Edited by: {entry.edited_by}")
```

### Multiple Edits

The system tracks all edits, creating a complete history:

```python
# Multiple edits create multiple history entries
message.content = "First edit"
message.save()

message.content = "Second edit"
message.save()

message.content = "Third edit"
message.save()

# View all history entries (ordered by most recent first)
history = message.history.all()
print(f"Total edits: {history.count()}")  # 3
```

### Deleting User Accounts

Users can delete their accounts through the `delete_user` view:

```python
from rest_framework.test import APIClient
from django.urls import reverse

client = APIClient()
client.force_authenticate(user=user)

# Delete user account
response = client.delete(reverse('messaging:delete_user'))
# Or using POST method
response = client.post(reverse('messaging:delete_user'))
```

When a user is deleted:
- All messages sent by the user are automatically deleted (CASCADE)
- All messages received by the user are automatically deleted (CASCADE)
- All notifications for the user are automatically deleted (CASCADE)
- MessageHistory entries where the user was the editor will have `edited_by` set to NULL (SET_NULL)
- The `post_delete` signal logs the cleanup process

**API Endpoint**: `DELETE /api/users/delete/` or `POST /api/users/delete/`

**Authentication Required**: Yes

**Example Response**:
```json
{
    "message": "Account deleted successfully",
    "detail": "Your account and all associated data have been permanently deleted."
}
```

## Testing

Run the tests using Django's test runner:

```bash
python manage.py test messaging
```

Or using pytest (if configured):

```bash
pytest messaging/tests.py
```

### Test Coverage

The test suite includes:

- **MessageModelTest**: Tests for Message model validation and creation
- **NotificationModelTest**: Tests for Notification model functionality
- **MessageSignalTest**: Tests for the signal handler behavior
- **IntegrationTest**: End-to-end tests for the complete flow

## Key Features

1. **Automatic Notification Creation**: Notifications are created automatically when messages are sent
2. **No Duplicates**: Uses `get_or_create` to prevent duplicate notifications
3. **Update-Safe**: Only creates notifications for new messages, not updates
4. **Edit Tracking**: Automatically tracks when messages are edited with `edited` flag and `edited_at` timestamp
5. **Complete Edit History**: Stores all previous versions of messages in `MessageHistory` model
6. **Automatic History Capture**: Uses `pre_save` signal to capture old content before updates
7. **User Account Deletion**: Allows users to delete their accounts with automatic cleanup of all related data
8. **Automatic Data Cleanup**: Uses `post_delete` signal to clean up messages, notifications, and message history when users are deleted
9. **CASCADE Relationships**: Properly configured foreign key relationships ensure data integrity during deletions
10. **Proper Signal Registration**: Signals are registered in `apps.py` using the `ready()` method
11. **Comprehensive Tests**: Full test coverage including unit and integration tests for all features

## Django Admin Integration

All three models (`Message`, `Notification`, and `MessageHistory`) are registered in the Django admin interface with:

### Message Admin
- List displays showing key fields including `edited` status
- Search functionality
- Filtering options including by `edited` and `edited_at`
- Read-only timestamp and edit fields
- Edit history display in the detail view
- Custom preview methods for content

### Notification Admin
- List displays showing key fields
- Search functionality
- Filtering options
- Read-only timestamp fields
- Custom preview methods for content

### MessageHistory Admin
- List displays showing message, old content preview, editor, and edit time
- Search functionality across message content and editor
- Filtering by edit time and editor
- Optimized queryset with `select_related` for performance
- Custom preview methods for old content

Access the admin interface at `/admin/` after creating a superuser.

## Best Practices Demonstrated

1. **Signal Registration**: Signals are registered in `apps.py` using the app config's `ready()` method
2. **Error Handling**: Signal handlers include proper error handling and logging
3. **Validation**: Model validation ensures data integrity (e.g., sender ≠ receiver)
4. **Indexing**: Database indexes on frequently queried fields for performance
5. **Type Hints**: Type hints throughout the code for better IDE support and documentation

## Notes

- The signal handler only creates notifications for **newly created** messages, not when messages are updated
- Notifications are automatically linked to the message receiver
- The `unique_together` constraint ensures one notification per user per message
- All timestamps are automatically set using Django's `timezone.now()`
- Message edit history is automatically captured using `pre_save` and `post_save` signals
- Only content changes trigger history creation - other field updates don't create history entries
- Multiple edits create multiple history entries, preserving a complete audit trail
- The `edited` flag and `edited_at` timestamp are automatically updated when content changes
- History entries are ordered by most recent first for easy access to latest changes
- User deletion automatically cleans up all related data due to CASCADE relationships
- The `post_delete` signal handler logs the cleanup process for audit purposes
- MessageHistory entries with `edited_by` pointing to a deleted user will have `edited_by` set to NULL (SET_NULL)

