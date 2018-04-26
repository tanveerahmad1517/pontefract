from datetime import date
from timezone_field import TimeZoneField
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models

class User(AbstractUser):
    """The User model for pontefract. Email is required"""

    class Meta:
        db_table = "users"

    email = models.EmailField(unique=True)
    timezone = TimeZoneField(default="UTC")
    

    def first_month(self):
        """What was the first month that the user has sessions for?"""

        from projects.models import Session
        sessions = Session.objects.filter(project__user=self)
        if sessions:
            first = sessions.order_by("start")[0]
            start = first.local_start()
            return date(start.year, start.month, 1)
