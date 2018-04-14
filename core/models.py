from datetime import date
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """The User model for pontefract. Email is required"""

    class Meta:
        db_table = "users"

    email = models.EmailField(unique=True)


    def sessions_today(self):
        """What sessions has the user done today?"""
        from projects.models import Session
        today = date.today()
        return Session.objects.filter(project__user=self, start_date=today).order_by("start_time")


    def minutes_worked_today(self):
        """How many minutes of work has the user done in sessions across all
        projects?"""

        sessions = self.sessions_today()
        return sum([session.duration() for session in sessions])


    def hours_worked_today(self):
        """How many hours of work has the user done in sessions accross all
        projects, as a human readable string?"""

        minutes = self.minutes_worked_today()
        if minutes < 60:
            return "{} minute{}".format(minutes, "" if minutes == 1 else "s")
        else:
            hours = minutes // 60
            mins = minutes - (hours * 60)
            text = "{} hour{}".format(hours, "" if hours == 1 else "s")
            if mins:
                text += ", {} minute{}".format(mins, "" if mins == 1 else "s")
            return text
