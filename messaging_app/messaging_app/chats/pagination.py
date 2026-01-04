"""
Pagination classes for the messaging app.

This module provides custom pagination classes for API responses.
"""
from rest_framework.pagination import PageNumberPagination


class MessagePagination(PageNumberPagination):
	"""
	Pagination class for messages.
	Returns 20 messages per page.
	Includes count in the pagination response.
	"""
	page_size = 20
	page_size_query_param = "page_size"
	max_page_size = 100

	def get_paginated_response(self, data):
		"""
		Return a paginated style Response object with count.
		The response includes:
		- count: total number of items
		- next: URL to next page
		- previous: URL to previous page
		- results: list of items for current page
		"""
		from rest_framework.response import Response
		return Response({
			"count": self.page.paginator.count,
			"next": self.get_next_link(),
			"previous": self.get_previous_link(),
			"results": data
		})

