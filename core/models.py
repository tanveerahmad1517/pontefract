"""The models needed for the core site, such as the User class."""

from datetime import date
from timezone_field import TimeZoneField
from django.contrib.auth.models import AbstractUser
from django.utils import timezone as tz
from django.db import models

class User(AbstractUser):
    """The User model for pontefract. Email is required"""

    class Meta:
        db_table = "users"

    PROJECT_ORDER_CHOICES = (("TD", "Total Duration"), ("LD", "Last Done"))

    email = models.EmailField(unique=True)
    timezone = TimeZoneField(default="UTC")
    project_order = models.CharField(
     max_length=2, choices=PROJECT_ORDER_CHOICES, default="TD"
    )


    def project_count(self):
        """Returns the number of projects the user has saved."""

        from projects.models import Project
        return Project.objects.filter(user=self).count()


    def total_time(self):
        """Returns the number of minutes in the user's sessions."""

        from projects.models import Session
        sessions = Session.objects.filter(project__user=self)
        return sum(session.duration() for session in sessions)
