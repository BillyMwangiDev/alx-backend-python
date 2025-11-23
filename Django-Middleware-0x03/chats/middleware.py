"""
Request logging middleware for the messaging app.

This middleware logs each user's requests to a file, including
timestamp, user, and request path.
"""
from datetime import datetime
import logging
from pathlib import Path
import os


class RequestLoggingMiddleware:
	"""
	Middleware that logs user requests to a file.
	
	Logs format: "{datetime.now()} - User: {user} - Path: {request.path}"
	"""

	def __init__(self, get_response):
		"""
		Initialize the middleware.
		
		Args:
			get_response: The next middleware or view in the chain
		"""
		self.get_response = get_response
		# Set up logger
		self.logger = logging.getLogger("request_logger")
		self.logger.setLevel(logging.INFO)
		
		# Create log file in project root (where manage.py is)
		# Get the directory where manage.py is located
		project_root = Path(__file__).resolve().parent.parent
		log_file = project_root / "requests.log"
		
		# Remove existing handlers to avoid duplicates
		self.logger.handlers.clear()
		
		# Create file handler
		handler = logging.FileHandler(log_file)
		handler.setLevel(logging.INFO)
		formatter = logging.Formatter("%(message)s")
		handler.setFormatter(formatter)
		self.logger.addHandler(handler)

	def __call__(self, request):
		"""
		Process the request and log user information.
		
		Args:
			request: The HTTP request object
			
		Returns:
			The HTTP response
		"""
		# Get user information
		user = request.user if hasattr(request, "user") and request.user.is_authenticated else "Anonymous"
		if user != "Anonymous":
			user = str(user.username) if hasattr(user, "username") else str(user)
		
		# Log the request
		log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
		self.logger.info(log_message)
		
		# Process the request
		response = self.get_response(request)
		
		return response

