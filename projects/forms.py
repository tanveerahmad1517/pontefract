from datetime import datetime
from django import forms
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from .models import Session, Project

class ProjectNameWidget(forms.TextInput):
    """The name widget for a Project Form. As this form is never rendered, the
    only thing this widget has to do is find the relevant string from a data
    dictionary when saving a project.

    This has to be overridden because by default it would look for a key called
    'name' but in practice this form will be used to parse POST data from a
    Session form, where the name is a key called 'project'."""

    def value_from_datadict(self, data, files, name):
        """Takes a POST dictionary from a SessionForm and returns the string
        containing the project name."""

        name =  data.get("project")
        return name



class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        exclude = []
        widgets = {"name": ProjectNameWidget()}


    def __init__(self, user, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.fields["user"].required = False
        self.user = user


    def save(self, *args, **kwargs):
        model = forms.ModelForm.save(self, *args, commit=False, **kwargs)
        model.user = self.user
        model.save()



class DateWidget(forms.DateInput):
    """The widget used to take date inputs."""

    input_type = "date"



class TimeWidget(forms.TimeInput):
    """The widget used to take time inputs."""

    input_type = "time"

    def format_value(self, value):
        """This function is used when rendering a Python object in a HTML tag.
        This override makes sure that seconds are not rendered."""

        value = forms.TimeInput.format_value(self, value)
        return value [:5] if isinstance(value, str) else value



class DateTimeWidget(forms.SplitDateTimeWidget):
    """The collective widget used to take time inputs."""

    def __init__(self, *args, **kwargs):
        forms.SplitDateTimeWidget.__init__(self, *args, **kwargs)
        self.widgets = (
         DateWidget(self.widgets[0].attrs), TimeWidget(self.widgets[1].attrs)
        )
        self.instance = False


    def decompress(self, *args, **kwargs):
        """Determines how a datetime is split into two values - date and time.
        If the form has an instance associated, the time will be sent,
        otherwise no time is sent."""

        values = forms.SplitDateTimeWidget.decompress(self, *args, **kwargs)
        return values if self.instance else (values[0], None)



class TimezoneWidget(forms.HiddenInput):
    """The timezone widget, which is never rendered and is just there to pretend
    to get data from POST data."""

    def __init__(self, *args, **kwargs):
        self.user = None
        self.attrs = {}


    def value_from_datadict(self, data, files, name):
        """The widget doesn't get the timezone from any POST data, it just gets
        the user's timezone."""

        return self.user.timezone



class SessionBreaksField(forms.IntegerField):
    """The field used to validate breaks taken. It has to be a positive."""

    def __init__(self, *args, **kwargs):
        forms.IntegerField.__init__(self, *args, **kwargs)
        self.initial = None
        self.required = False
        self.validators.append(MinValueValidator(
         0, message="The break must be positive."
        ))


class SessionBreaksWidget(forms.NumberInput):
    """The widget used to take in breaks."""

    def __init__(self, *args, **kwargs):
        forms.NumberInput.__init__(self, *args, **kwargs)
        self.is_required = False


    def value_from_datadict(self, data, files, name):
        """If no breaks are sent, it will pluck '0' out of nowhere."""

        return data.get(name) or "0"


    def format_value(self, value):
        return None if value == 0 else value



class SessionProjectField(forms.ModelChoiceField):
    """The field used to hold a project."""

    def __init__(self, *args, **kwargs):
        forms.ModelChoiceField.__init__(self, *args, **kwargs)
        self.user = None
        self.queryset = Project.objects


    def to_python(self, value):
        """Controls how the field turns POST data into an object. It will be
        interpreted as a project name. If there is no project, it means that the
        project form that was applied to the POST data previosly wasn't happy,
        so an error about an invalid project name will be sent."""

        try:
            return Project.objects.get(user=self.user, name=value)
        except Project.DoesNotExist:
            raise ValidationError("Invalid project name")



class SessionProjectWidget(forms.TextInput):
    """The widget used to take in a project name. Basically just a textbox."""

    def __init__(self, *args, **kwargs):
        forms.TextInput.__init__(self, *args, **kwargs)
        self.user = None


    def format_value(self, value):
        """If the field holds a number, it's an ID and that project should be
        rendered. If the field holds a string, it's a name and that project
        for that user should be rendered (unless it's just spaces)."""

        if value:
            if isinstance(value, int):
                return Project.objects.get(id=value)
            elif value.strip():
                return Project.objects.get(user=self.user, name=value)



class SessionForm(forms.ModelForm):
    """The form which allows a user to enter a session of work they have done.

    They can provide a new project at the same time."""

    class Meta:
        model = Session
        exclude = []

        field_classes = {
         "start": forms.SplitDateTimeField, "end": forms.SplitDateTimeField,
         "breaks": SessionBreaksField, "project": SessionProjectField
        }

        widgets = {
         "start": DateTimeWidget(
          date_attrs={"tabindex": "1"}, time_attrs={"tabindex": "3"},
         ),
         "end": DateTimeWidget(
          date_attrs={"tabindex": "2"}, time_attrs={"tabindex": "4"}
         ),
         "timezone": TimezoneWidget(),
         "breaks": SessionBreaksWidget(attrs={"tabindex": "5"}),
         "project": SessionProjectWidget(attrs={"tabindex": "6"})
        }


    def __init__(self, *args, user=None, date=None, **kwargs):
        self.user = user
        self.date = date
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.fields["start"].widget.instance = self.instance.id is not None
        self.fields["end"].widget.instance = self.instance.id is not None
        self.fields["start"].initial = timezone.localtime()
        self.fields["end"].initial = timezone.localtime()
        self.fields["timezone"].widget.user = self.user
        self.fields["project"].user = self.user
        self.fields["project"].widget.user = self.user
        if date:
            self.fields["start"].initial = datetime(date.year, date.month, date.day)
            self.fields["end"].initial = datetime(date.year, date.month, date.day)


    def clean(self):
        """Checks that the times and break times mesh well together."""

        forms.ModelForm.clean(self)
        if "start" in self.cleaned_data and "end" in self.cleaned_data:
            if self.cleaned_data["end"] < self.cleaned_data["start"]:
                self.add_error("end", "End time is before start time")
            elif (self.cleaned_data["end"] - self.cleaned_data["start"]
             ).seconds <= self.cleaned_data.get("breaks", 0) * 60:
                self.add_error("breaks", "Break cannot cancel out session")
