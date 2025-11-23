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


class RestrictAccessByTimeMiddleware:
	"""
	Middleware that restricts access to the messaging app during certain hours.
	
	Access is only allowed between 6PM (18:00) and 9PM (21:00).
	Outside these hours, returns 403 Forbidden.
	"""

	def __init__(self, get_response):
		"""
		Initialize the middleware.
		
		Args:
			get_response: The next middleware or view in the chain
		"""
		self.get_response = get_response
		# Access allowed between 6PM (18:00) and 9PM (21:00)
		self.start_hour = 18  # 6PM
		self.end_hour = 21    # 9PM

	def __call__(self, request):
		"""
		Check current server time and restrict access if outside allowed hours.
		
		Args:
			request: The HTTP request object
			
		Returns:
			HTTP 403 Forbidden response if outside allowed hours,
			otherwise processes the request normally
		"""
		from django.http import HttpResponseForbidden
		
		# Get current server time
		current_time = datetime.now()
		current_hour = current_time.hour
		
		# Check if current hour is outside the allowed range (6PM to 9PM)
		# Access is allowed if current_hour >= 18 and current_hour < 21
		if current_hour < self.start_hour or current_hour >= self.end_hour:
			return HttpResponseForbidden(
				"Access to the messaging app is restricted. "
				f"Service is only available between {self.start_hour}:00 (6PM) and {self.end_hour}:00 (9PM)."
			)
		
		# Process the request if within allowed hours
		response = self.get_response(request)
		
		return response

