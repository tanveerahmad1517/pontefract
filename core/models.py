from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """The User model for pontefract. Email is required"""

    class Meta:
        db_table = "users"

    email = models.EmailField(unique=True)


    def minutes_worked_today(self):
        """How many minutes of work has the user done in sessions across all
        projects?"""
        
        from projects.models import Session
        today = datetime.now().date()
        sessions = Session.objects.filter(project__user=self, start_date=today)
        return sum([session.duration() for session in sessions])
