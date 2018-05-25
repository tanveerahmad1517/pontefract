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

    email = models.EmailField(unique=True)
    timezone = TimeZoneField(default="UTC")


    def first_month(self):
        """What was the first month that the user has sessions for?

        Database queries: 1"""

        from projects.models import Session
        sessions = list(
         Session.objects.filter(project__user=self).order_by("start")
        )
        if sessions:
            start = tz.localtime(sessions[0].start)
            return date(start.year, start.month, 1)


    def project_count(self):
        """Returns the number of projects the user has saved."""

        from projects.models import Project
        return Project.objects.filter(user=self).count()


    def total_time(self):
        """Returns the number of minutes in the user's sessions."""
        
        from projects.models import Session
        sessions = Session.objects.filter(project__user=self)
        return sum(session.duration() for session in sessions)
