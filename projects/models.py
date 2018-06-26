"""Models needed for time tracking, and helper classes."""

from datetime import date, datetime, timedelta
import pytz
from calendar import monthrange
from itertools import groupby
from timezone_field import TimeZoneField
from django.utils import timezone as tz
from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from django.db.models import F, ExpressionWrapper
from django.db.models.functions import Cast
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


    def total_time(self):
        """Returns the sum of all the project's sessions' durations.

        SQL queries: 1"""

        return sum(s.duration() for s in self.session_set.all())


    @classmethod
    def by_user_order(cls, user):
        """Gets all of a user's projects, sorted by either total duration or
        when it was last done, depending on the user's settings. Each project
        object will be annotated with a duration (in minutes) and a most recent
        session.

        SQL queries: 2"""

        sessions = list(Session.objects.filter(project__user=user).annotate(
         project_id=models.F("project")
        ).order_by("start"))
        projects = {
         p.id: p for p in Project.objects.filter(user=user).order_by("id")
        }
        for project in projects.values():
            project.duration = 0
            project.recent = None
        for session in sessions:
            projects[session.project_id].duration += session.duration()
            projects[session.project_id].recent = session
        if user.project_order == "LD":
            done_projects = [p for p in projects.values() if p.recent]
            never_projects = [p for p in projects.values() if not p.recent]
            return list(
             reversed(sorted(done_projects, key=lambda p: p.recent.end))
            ) + never_projects
        else:
            return reversed(sorted(projects.values(), key=lambda p: p.duration))


class Session(models.Model):
    """A period of time spent on a particular project."""

    class Meta:
        db_table = "sessions"

    start = models.DateTimeField()
    end = models.DateTimeField()
    timezone = TimeZoneField()
    breaks = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)


    def local_start(self):
        """Even when timezone awareness is switched on, the start property just
        returns UTC time. This returns the start time in the current time
        zone."""

        utc_start = self.start
        return tz.localtime(utc_start)


    def local_end(self):
        """Even when timezone awareness is switched on, the start property just
        returns UTC time. This returns the start time in the current time
        zone."""

        utc_end = self.end
        return tz.localtime(utc_end)


    def duration(self):
        """The length of the session in minutes, accounting for breaks."""

        minutes = 0
        delta = self.end - self.start
        minutes += int((delta.seconds / 60) - self.breaks)
        if delta.days:
            minutes += delta.days * 24 * 60
        return minutes


    @classmethod
    def from_day(cls, user, day):
        """Gets all the user's sessions from a given day, as a ``Day`` object.
        The day will just be an ordinary date object with no timezone awareness,
        and should be the date in the user's timezone, as when the database is
        searched the dates there will be converted to that timezone.

        SQL queries: 1"""

        sessions = cls.objects.filter(
         project__user=user, start__year=day.year,
         start__month=day.month, start__day=day.day
        ).annotate(
         project_id=models.F("project"), project_name=models.F("project__name")
        ).order_by("start")
        return Day(sessions, day=day)



class Day:
    """A day of sessions."""

    def __init__(self, session_set, day=None):
        self.sessions = list(session_set)
        self.day = day
        self.total_duration = sum(s.duration() for s in self.sessions)


    def __iter__(self):
        return iter(self.sessions)


    def yesterday(self):
        """The previous day."""

        return self.day - timedelta(days=1)


    def tomorrow(self):
        """The next day."""

        return self.day + timedelta(days=1)


    def next_month(self):
        """The next month after this day's month."""

        year, month = self.day.year, self.day.month
        return date(
         year + 1 if month == 12 else year, 1 if month == 12 else month + 1, 1
        )


    def previous_month(self):
        """The previous month before this day's month."""

        year, month = self.day.year, self.day.month
        return date(
         year - 1 if month == 1 else year, 12 if month == 1 else month - 1, 1
        )


    @staticmethod
    def group_sessions_by_local_date(sessions):
        """Takes a set of sessions, groups them into local days, and makes a
        ``Day`` from each groups."""

        groups = [Day(list(b), day=a) for a, b in groupby(
         sessions, key=lambda s: tz.localtime(s.start).date()
        )]
        groups.sort(key=lambda x: x.day), groups.reverse()
        return groups


    @staticmethod
    def insert_empty_month_days(days, year, month):
        """Inserts empty ``Day`` objects into a list to fill out a given month.
        It will also remove days in the future based on the user's local
        time."""

        month_days = [date(year, month, day) for day in range(
         1, monthrange(year, month)[1] + 1
        )]
        days.reverse()
        for day in month_days:
            if day not in [d.day for d in days]:
                days.insert(day.day - 1, Day([], day=day))
        while days[-1].day > tz.localtime().date(): days.pop()
        days.reverse()
