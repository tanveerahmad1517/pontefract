from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

class Project(models.Model):
    """A project which the user wishes to track time spent on."""

    class Meta:
        db_table = "projects"

    name = models.CharField(max_length=256)
    user = models.ForeignKey(User, on_delete=models.CASCADE)



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
