from datetime import datetime
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


    def start(self):
        """The start time as a Python datetime object."""

        return datetime.combine(self.start_date, self.start_time)


    def end(self):
        """The end time as a Python datetime object."""

        return datetime.combine(self.end_date, self.end_time)


    def duration(self):
        """The length of the session in minutes, accounting for breaks."""

        return int(((self.end() - self.start()).seconds / 60) - self.breaks)


    def duration_string(self):
        """The length of the session in minutes, accounting for breaks, as as
        string."""

        minutes = self.duration()
        if minutes < 60:
            return "{} minute{}".format(minutes, "" if minutes == 1 else "s")
        else:
            hours = minutes // 60
            mins = minutes - (hours * 60)
            text = "{} hour{}".format(hours, "" if hours == 1 else "s")
            if mins:
                text += ", {} minute{}".format(mins, "" if mins == 1 else "s")
            return text
