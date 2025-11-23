"""
Authentication utilities for the messaging app.

This module provides custom authentication classes and utilities
for JWT-based authentication.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.exceptions import AuthenticationFailed


class CustomJWTAuthentication(JWTAuthentication):
	"""
	Custom JWT Authentication that handles token validation
	and user retrieval for the custom User model with UUID primary key.
	"""

	def get_user(self, validated_token):
		"""
		Retrieve the user associated with the validated token.

		Args:
			validated_token: The validated JWT token

		Returns:
			User instance associated with the token

		Raises:
			AuthenticationFailed: If user cannot be found or is inactive
		"""
		try:
			user_id = validated_token["user_id"]
		except KeyError:
			raise InvalidToken("Token contained no recognizable user identification")

		try:
			from .models import User
			user = User.objects.get(user_id=user_id)
		except User.DoesNotExist:
			raise AuthenticationFailed("User not found", code="user_not_found")

		if not user.is_active:
			raise AuthenticationFailed("User is inactive", code="user_inactive")

		return user

