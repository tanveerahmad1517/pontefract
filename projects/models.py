from datetime import date, datetime
import pytz
from calendar import monthrange
from itertools import groupby
from timezone_field import TimeZoneField
from django.utils import timezone
from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
User = get_user_model()

class Project(models.Model):
    """A project which the user wishes to track time spent on."""

    class Meta:
        db_table = "projects"
        unique_together = (("name", "user"),)
        ordering = [models.functions.Lower("name")]

    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


    def __str__(self):
        return self.name        


    def total_time_string(self):
        """Gets the total number of minutes worked, as a human readable
        string."""

        return Session.duration_string(*self.session_set.all())


    def most_recent_session(self):
        """Gets the most recently completed session."""

        return self.session_set.order_by("end").last()



class Session(models.Model):
    """A period of time spent on a particular project."""

    class Meta:
        db_table = "sessions"

    start = models.DateTimeField()
    end = models.DateTimeField()
    timezone = TimeZoneField()
    breaks = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


    def local_start(self):
        """Even when timezone awareness is switched on, the start property just
        returns UTC time. This returns the start time in the current time
        zone."""

        utc_start = self.start
        naive_start = timezone.make_naive(utc_start)
        return timezone.get_current_timezone().localize(naive_start)


    def local_end(self):
        """Even when timezone awareness is switched on, the start property just
        returns UTC time. This returns the start time in the current time
        zone."""

        utc_end = self.end
        naive_end = timezone.make_naive(utc_end)
        return timezone.get_current_timezone().localize(naive_end)


    def duration(self):
        """The length of the session in minutes, accounting for breaks."""

        delta = self.end - self.start
        minutes = int((delta.seconds / 60) - self.breaks)
        if delta.days:
            minutes += delta.days * 24 * 60
        return minutes


    def duration_string(*sessions):
        """Adds up the durations of multiple sessions and returns this duration
        as a human readable string."""

        minutes = sum(session.duration() for session in sessions)
        if minutes < 60:
            return "{} minute{}".format(minutes, "" if minutes == 1 else "s")
        else:
            hours = minutes // 60
            mins = minutes - (hours * 60)
            text = "{} hour{}".format(hours, "" if hours == 1 else "s")
            if mins:
                text += ", {} minute{}".format(mins, "" if mins == 1 else "s")
            return text


    @classmethod
    def from_day(cls, user, day):
        """Gets all the user's sessions from a given day, as a
        (date, duration_string, sessions) tuple. The day will just be an
        ordinary date object with no timezone awareness, and should be the date
        in the user's timezone, as when the database is searched the dates there
        will be converted to that timezone."""

        sessions = cls.objects.filter(
         project__user=user, start__year=day.year,
         start__month=day.month, start__day=day.day
        ).order_by("start")
        return (day, cls.duration_string(*sessions), sessions)


    @classmethod
    def group_by_date(cls, user, project=None, month=None):
        """Gets the user's sessions and groups them by date. You can restrict
        these to those from a particular project, or to a particular month. If
        the latter, it will also fill out the rest of the month."""

        sessions = cls.objects.filter(project__user=user)
        if project: sessions = sessions.filter(project=project)
        if month:
            sessions = sessions.filter(
             start__year=month.year, start__month=month.month
            )
        sessions = sessions.order_by("-start")
        groups = [[a, list(b)] for a, b in groupby(
         sessions, key=lambda s: s.local_start().date()
        )]
        for group in groups:
            group[-1].sort(key=lambda s: s.local_start().time())
        if month:
            today, accounted = timezone.localtime().date(), [day[0] for day in groups]
            month_days = [date(
             month.year, month.month, day
            ) for day in range(1, monthrange(month.year, month.month)[1] + 1)]
            for day in month_days:
                if day not in accounted and day <= today:
                    groups.append((day, []))
            groups.sort(key=lambda x: x[0]), groups.reverse()
        return [(d[0], cls.duration_string(*d[1]), d[1]) for d in groups]
