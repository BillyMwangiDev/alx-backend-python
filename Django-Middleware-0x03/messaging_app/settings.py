from pathlib import Path
import os
from datetime import timedelta
from decouple import config, Csv


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("DJANGO_SECRET_KEY", default="unsafe-dev-secret-key")

DEBUG = config("DJANGO_DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", default="*", cast=Csv())

INSTALLED_APPS = [
	"django.contrib.admin",
	"django.contrib.auth",
	"django.contrib.contenttypes",
	"django.contrib.sessions",
	"django.contrib.messages",
	"django.contrib.staticfiles",
	"corsheaders",
	"rest_framework",
	"rest_framework_simplejwt",
	"django_filters",
	"messaging_app.chats",
]

MIDDLEWARE = [
	"corsheaders.middleware.CorsMiddleware",
	"django.middleware.security.SecurityMiddleware",
	"django.contrib.sessions.middleware.SessionMiddleware",
	"django.middleware.common.CommonMiddleware",
	"django.middleware.csrf.CsrfViewMiddleware",
	"django.contrib.auth.middleware.AuthenticationMiddleware",
	"chats.middleware.RestrictAccessByTimeMiddleware",
	"chats.middleware.RequestLoggingMiddleware",
	"django.contrib.messages.middleware.MessageMiddleware",
	"django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "messaging_app.urls"

TEMPLATES = [
	{
		"BACKEND": "django.template.backends.django.DjangoTemplates",
		"DIRS": [BASE_DIR / "templates"],
		"APP_DIRS": True,
		"OPTIONS": {
			"context_processors": [
				"django.template.context_processors.debug",
				"django.template.context_processors.request",
				"django.contrib.auth.context_processors.auth",
				"django.contrib.messages.context_processors.messages",
			],
		},
	},
]

WSGI_APPLICATION = "messaging_app.wsgi.application"
ASGI_APPLICATION = "messaging_app.asgi.application"

DATABASES = {
	"default": {
		"ENGINE": config("DB_ENGINE", default="django.db.backends.sqlite3"),
		"NAME": config("DB_NAME", default=str(BASE_DIR / "db.sqlite3")),
		"USER": config("DB_USER", default=""),
		"PASSWORD": config("DB_PASSWORD", default=""),
		"HOST": config("DB_HOST", default=""),
		"PORT": config("DB_PORT", default=""),
	}
}

AUTH_USER_MODEL = "chats.User"

AUTH_PASSWORD_VALIDATORS = [
	{"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
	{"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
	{"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
	{"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOW_ALL_ORIGINS = config("CORS_ALLOW_ALL_ORIGINS", default=True, cast=bool)

REST_FRAMEWORK = {
	"DEFAULT_AUTHENTICATION_CLASSES": [
		"rest_framework_simplejwt.authentication.JWTAuthentication",
		"rest_framework.authentication.SessionAuthentication",
		"rest_framework.authentication.BasicAuthentication",
	],
	"DEFAULT_PERMISSION_CLASSES": [
		"rest_framework.permissions.IsAuthenticated",
	],
	# Use PageNumberPagination with PAGE_SIZE of 20 messages per page
	"DEFAULT_PAGINATION_CLASS": "messaging_app.chats.pagination.MessagePagination",
	"PAGE_SIZE": 20,
	"DEFAULT_FILTER_BACKENDS": [
		"django_filters.rest_framework.DjangoFilterBackend",
		"rest_framework.filters.OrderingFilter",
		"rest_framework.filters.SearchFilter",
	],
}

# JWT Settings
SIMPLE_JWT = {
	"ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
	"REFRESH_TOKEN_LIFETIME": timedelta(days=1),
	"ROTATE_REFRESH_TOKENS": True,
	"BLACKLIST_AFTER_ROTATION": True,
	"UPDATE_LAST_LOGIN": True,
	"ALGORITHM": "HS256",
	"SIGNING_KEY": SECRET_KEY,
	"AUTH_HEADER_TYPES": ("Bearer",),
	"AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
	"USER_ID_FIELD": "user_id",
	"USER_ID_CLAIM": "user_id",
	"AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
	"TOKEN_TYPE_CLAIM": "token_type",
}


