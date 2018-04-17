from datetime import date, datetime
from calendar import monthrange
from itertools import groupby
from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
User = get_user_model()

class Project(models.Model):
    """A project which the user wishes to track time spent on."""

    class Meta:
        db_table = "projects"
        unique_together = (("name", "user"),)

    name = models.CharField(max_length=256)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


    def __str__(self):
        return self.name


    @classmethod
    def by_name(cls, user):
        return Project.objects.filter(user=user).order_by(
         models.functions.Lower("name")
        )




class Session(models.Model):
    """A period of time spent on a particular project."""

    class Meta:
        db_table = "sessions"

    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    breaks = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    @classmethod
    def sessions_from(cls, user, day):
        """Gets all the user's sessions from a given day, as a
        (date, duration_string, sessions) tuple."""

        sessions = cls.objects.filter(
         project__user=user, start_date=day
        ).order_by("start_time")
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
             start_date__year=month.year, start_date__month=month.month
            )
        sessions = sessions.order_by("-start_date", "start_time")
        groups = [(a, list(b)) for a, b in groupby(
         sessions, key=lambda s: s.start_date
        )]
        if month:
            today, accounted = date.today(), [day[0] for day in groups]
            month_days = [date(
             month.year, month.month, day
            ) for day in range(1, monthrange(month.year, month.month)[1] + 1)]
            for day in month_days:
                if day not in accounted and day < today:
                    groups.append((day, []))
            groups.sort(key=lambda x: x[0]), groups.reverse()
        return [(d[0], cls.duration_string(*d[1]), d[1]) for d in groups]


    def start(self):
        """The start time as a Python datetime object."""

        return datetime.combine(self.start_date, self.start_time)


    def end(self):
        """The end time as a Python datetime object."""

        return datetime.combine(self.end_date, self.end_time)


    def duration(self):
        """The length of the session in minutes, accounting for breaks."""

        return int(((self.end() - self.start()).seconds / 60) - self.breaks)


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
