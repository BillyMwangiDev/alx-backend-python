"""
Pagination classes for the messaging app.

This module provides custom pagination classes for API responses.
"""
from rest_framework.pagination import PageNumberPagination


class MessagePagination(PageNumberPagination):
	"""
	Pagination class for messages.
	Returns 20 messages per page.
	"""
	page_size = 20
	page_size_query_param = "page_size"
	max_page_size = 100

