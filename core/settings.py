import os
from .secrets import BASE_DIR, SECRET_KEY, DATABASES

ALLOWED_HOSTS = []
DEBUG = True

ROOT_URLCONF = "core.urls"

INSTALLED_APPS = [
 "django.contrib.contenttypes",
 "django.contrib.staticfiles",
 "django.contrib.auth",
 "django.contrib.sessions",
 "core"
]

MIDDLEWARE = [
 "django.contrib.sessions.middleware.SessionMiddleware",
 "django.middleware.common.CommonMiddleware",
 "django.middleware.csrf.CsrfViewMiddleware",
 "django.contrib.auth.middleware.AuthenticationMiddleware",
]

TEMPLATES = [{
 "BACKEND": "django.template.backends.django.DjangoTemplates",
 "APP_DIRS": True,
 "OPTIONS": {
  "context_processors": [
   "django.contrib.auth.context_processors.auth",
  ],
 },
}]

STATIC_URL = "/static/"
