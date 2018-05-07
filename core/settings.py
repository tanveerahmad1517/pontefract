import os
from .secrets import SECRET_KEY, BASE_DIR, DATABASES

VERSION = "0.1.2"


ALLOWED_HOSTS = []
DEBUG = True

ROOT_URLCONF = "core.urls"

INSTALLED_APPS = [
 "django.contrib.contenttypes",
 "django.contrib.staticfiles",
 "django.contrib.auth",
 "django.contrib.sessions",
 "django.contrib.humanize",
 "timezone_field",
 "core",
 "projects"
]



MIDDLEWARE = [
 "django.contrib.sessions.middleware.SessionMiddleware",
 "django.middleware.common.CommonMiddleware",
 "django.middleware.csrf.CsrfViewMiddleware",
 "django.contrib.auth.middleware.AuthenticationMiddleware",
 "core.middleware.TimezoneMiddleware"
]

STATIC_URL = "/static/"
STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../static"))

AUTH_USER_MODEL = "core.User"

TIME_ZONE = "UTC"
USE_TZ = True
TIME_FORMAT = "H:i"
DATE_FORMAT = "l j F, Y"
TEMPLATES = [{
 "BACKEND": "django.template.backends.django.DjangoTemplates",
 "APP_DIRS": True,
 "OPTIONS": {
  "context_processors": [
   "django.contrib.auth.context_processors.auth",
   "django.template.context_processors.request"
  ],
 },
}]
