"""
Request logging middleware for the messaging app.

This middleware logs each user's requests to a file, including
timestamp, user, and request path.
"""
from datetime import datetime, timedelta
import logging
from pathlib import Path
import os
from collections import defaultdict


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


class OffensiveLanguageMiddleware:
	"""
	Middleware that limits the number of chat messages a user can send
	within a certain time window, based on their IP address.
	
	Limits: 5 messages per minute per IP address.
	"""

	def __init__(self, get_response):
		"""
		Initialize the middleware.
		
		Args:
			get_response: The next middleware or view in the chain
		"""
		self.get_response = get_response
		# Rate limiting configuration
		self.max_messages = 5  # Maximum messages allowed
		self.time_window = timedelta(minutes=1)  # Time window (1 minute)
		
		# Dictionary to track IP addresses and their request timestamps
		# Format: {ip_address: [timestamp1, timestamp2, ...]}
		self.ip_requests = defaultdict(list)

	def _get_client_ip(self, request):
		"""
		Get the client IP address from the request.
		
		Args:
			request: The HTTP request object
			
		Returns:
			Client IP address as string
		"""
		x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
		if x_forwarded_for:
			ip = x_forwarded_for.split(",")[0]
		else:
			ip = request.META.get("REMOTE_ADDR")
		return ip

	def _is_message_request(self, request):
		"""
		Check if the request is a POST request to create a message.
		
		Args:
			request: The HTTP request object
			
		Returns:
			True if it's a message creation request, False otherwise
		"""
		# Check if it's a POST request to message endpoints
		if request.method != "POST":
			return False
		
		# Check if path is related to messages
		path = request.path
		return (
			"/api/v1/messages/" in path or
			"/api/v1/conversations/" in path and "/send/" in path
		)

	def _clean_old_requests(self, ip_address, current_time):
		"""
		Remove request timestamps older than the time window.
		
		Args:
			ip_address: The IP address to clean
			current_time: Current datetime
		"""
		cutoff_time = current_time - self.time_window
		self.ip_requests[ip_address] = [
			timestamp
			for timestamp in self.ip_requests[ip_address]
			if timestamp > cutoff_time
		]

	def __call__(self, request):
		"""
		Track POST requests (messages) from each IP address and enforce rate limit.
		
		Args:
			request: The HTTP request object
			
		Returns:
			HTTP 429 Too Many Requests response if limit exceeded,
			otherwise processes the request normally
		"""
		from django.http import HttpResponse, JsonResponse
		
		# Only check POST requests to message endpoints
		if self._is_message_request(request):
			# Get client IP address
			ip_address = self._get_client_ip(request)
			current_time = datetime.now()
			
			# Clean old requests outside the time window
			self._clean_old_requests(ip_address, current_time)
			
			# Check if IP has exceeded the limit
			if len(self.ip_requests[ip_address]) >= self.max_messages:
				return JsonResponse(
					{
						"error": "Rate limit exceeded",
						"message": f"You can only send {self.max_messages} messages per minute. Please try again later.",
						"limit": self.max_messages,
						"window": "1 minute"
					},
					status=429
				)
			
			# Add current request timestamp
			self.ip_requests[ip_address].append(current_time)
		
		# Process the request
		response = self.get_response(request)
		
		return response

